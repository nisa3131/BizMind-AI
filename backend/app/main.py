import io
import os
import time
import uuid
from pathlib import Path
import fitz
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, EmailStr, Field
from app.db import db_connection
from app.security import create_token, current_user, hasher
from app.rag import ingest, retrieve

app = FastAPI(title="BizMind AI", version="0.2.0")

class Signup(BaseModel):
    business_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

class Login(BaseModel):
    email: EmailStr
    password: str

class Question(BaseModel):
    question: str = Field(min_length=1, max_length=3000)

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "bizmind-api"}

@app.post("/api/v1/auth/signup", status_code=201)
def signup(body: Signup):
    with db_connection() as db:
        if db.execute("SELECT 1 FROM users WHERE email=?", (body.email.lower(),)).fetchone():
            raise HTTPException(409, "Email already registered")
        cursor = db.execute("INSERT INTO tenants(name) VALUES(?)", (body.business_name,))
        tenant_id = cursor.lastrowid
        user_id = db.execute("INSERT INTO users(tenant_id,email,password_hash) VALUES(?,?,?)",
                             (tenant_id, body.email.lower(), hasher.hash(body.password))).lastrowid
    return {"access_token": create_token(user_id,tenant_id), "token_type": "bearer"}

@app.post("/api/v1/auth/login")
def login(body: Login):
    with db_connection() as db:
        user = db.execute("SELECT * FROM users WHERE email=?", (body.email.lower(),)).fetchone()
    if user is None or not hasher.verify(body.password,user["password_hash"]):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_token(user["id"],user["tenant_id"]), "token_type": "bearer"}

@app.post("/api/v1/documents", status_code=201)
async def upload(file: UploadFile = File(...), user: dict = Depends(current_user)):
    if file.content_type != "application/pdf" or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(415, "PDF only")
    content = await file.read(10 * 1024 * 1024 + 1)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(413, "Maximum file size is 10 MB")
    try:
        pdf = fitz.open(stream=content, filetype="pdf")
        if pdf.page_count > 200:
            raise HTTPException(413, "Maximum 200 pages")
        text = "\n".join(page.get_text() for page in pdf)
        pdf.close()
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(422, "Invalid PDF")
    if not text.strip():
        raise HTTPException(422, "No extractable text in PDF")
    directory = Path(os.getenv("UPLOAD_PATH","/data/uploads")) / str(user["tenant_id"])
    directory.mkdir(parents=True,exist_ok=True)
    path = directory / (uuid.uuid4().hex + ".pdf")
    path.write_bytes(content)
    with db_connection() as db:
        document_id = db.execute("INSERT INTO documents(tenant_id,filename,storage_path) VALUES(?,?,?)",
                                 (user["tenant_id"],Path(file.filename).name,str(path))).lastrowid
    chunks = ingest(user["tenant_id"],document_id,text,Path(file.filename).name)
    return {"document_id": document_id, "chunks": chunks}

@app.get("/api/v1/documents")
def documents(user: dict = Depends(current_user)):
    with db_connection() as db:
        rows = db.execute("SELECT id,filename FROM documents WHERE tenant_id=?",
                          (user["tenant_id"],)).fetchall()
    return [dict(row) for row in rows]

@app.post("/api/v1/chat")
def chat(body: Question, user: dict = Depends(current_user)):
    started = time.perf_counter()
    matches = retrieve(user["tenant_id"],body.question)
    if not matches:
        answer = "I couldn't find an answer in the uploaded documents."
    else:
        # Retrieval-only safe fallback until an optional LLM provider is configured.
        answer = "Relevant passages from your documents:\n" + "\n\n".join(
            f"[{i+1}] {item['text'][:700]}" for i,item in enumerate(matches))
    latency = round((time.perf_counter()-started)*1000,2)
    with db_connection() as db:
        db.execute("INSERT INTO queries(tenant_id,latency_ms) VALUES(?,?)",
                   (user["tenant_id"],latency))
    return {"answer":answer,"citations":[{"source":x["source"],"document_id":x["document_id"],
              "chunk":x["chunk"]} for x in matches], "latency_ms":latency}

@app.get("/api/v1/analytics")
def analytics(user: dict = Depends(current_user)):
    with db_connection() as db:
        total, avg = db.execute("SELECT COUNT(*),COALESCE(AVG(latency_ms),0) FROM queries WHERE tenant_id=?",
                                (user["tenant_id"],)).fetchone()
    return {"total_queries":total,"average_latency_ms":round(avg,2)}
