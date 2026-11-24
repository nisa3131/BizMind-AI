from fastapi.testclient import TestClient
from app.main import app
import app.main as api
import app.db as db
import app.rag as rag

def test_tenant_isolation_and_chat(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "db.sqlite3"))
    monkeypatch.setenv("JWT_SECRET", "test-secret-" * 4)
    monkeypatch.setenv("UPLOAD_PATH", str(tmp_path / "uploads"))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    chunks = {}
    def ingest(tenant_id, document_id, text, filename):
        chunks.setdefault(tenant_id, []).append({"text":text, "source":filename,
                                                 "document_id":document_id,"chunk":0})
        return 1
    monkeypatch.setattr(api, "ingest", ingest)
    monkeypatch.setattr(api, "retrieve", lambda tenant_id, question: chunks.get(tenant_id, []))
    client = TestClient(app)
    def signup(name, email):
        response = client.post("/api/v1/auth/signup", json={"business_name":name,
            "email":email, "password":"test-password-123"})
        assert response.status_code == 201, response.text
        return {"Authorization":"Bearer "+response.json()["access_token"]}
    a = signup("Alpha", "alpha@example.com")
    b = signup("Beta", "beta@example.com")
    assert client.get("/api/v1/documents").status_code == 401
    response = client.post("/api/v1/documents", headers=a,
                           files={"file":("faq.txt", b"Returns are allowed within 30 days.", "text/plain")})
    assert response.status_code == 201, response.text
    assert len(client.get("/api/v1/documents",headers=a).json()) == 1
    assert client.get("/api/v1/documents",headers=b).json() == []
    qa = client.post("/api/v1/chat", headers=a, json={"question":"Return policy?"}).json()
    qb = client.post("/api/v1/chat", headers=b, json={"question":"Return policy?"}).json()
    assert "30 days" in qa["answer"] and qa["citations"][0]["source"] == "faq.txt"
    assert qb["citations"] == [] and qb["answer_mode"] == "no_sources"
    assert client.get("/api/v1/analytics",headers=a).json()["total_queries"] == 1
    assert client.get("/api/v1/analytics",headers=b).json()["total_queries"] == 1

def test_retrieval_filters_other_tenants(monkeypatch):
    class Collection:
        def get(self, **kwargs):
            assert kwargs["where"] == {"tenant_id": 7}
            return {"ids":["7:1:0"]}
        def query(self, **kwargs):
            assert kwargs["where"] == {"tenant_id": 7}
            return {"documents":[["allowed","foreign"]], "metadatas":[[
                {"tenant_id":7,"filename":"a.txt","document_id":1,"chunk":0},
                {"tenant_id":8,"filename":"b.txt","document_id":2,"chunk":0}]]}
    monkeypatch.setattr(rag,"collection",lambda:Collection())
    assert [item["text"] for item in rag.retrieve(7,"question")] == ["allowed"]
