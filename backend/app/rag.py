import os
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

VECTOR_PATH = os.getenv("VECTOR_PATH", "/data/chroma")
def collection():
    client = chromadb.PersistentClient(path=VECTOR_PATH)
    return client.get_or_create_collection("bizmind_chunks", embedding_function=DefaultEmbeddingFunction())

def ingest(tenant_id: int, document_id: int, text: str, filename: str) -> int:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    chunks = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120).split_text(text)
    if chunks:
        collection().upsert(
            ids=[f"{tenant_id}:{document_id}:{i}" for i in range(len(chunks))],
            documents=chunks,
            metadatas=[{"tenant_id": tenant_id, "document_id": document_id,
                        "filename": filename, "chunk": i} for i in range(len(chunks))])
    return len(chunks)

def retrieve(tenant_id: int, question: str) -> list[dict]:
    coll = collection()
    if coll.count() == 0:
        return []
    result = coll.query(query_texts=[question], n_results=min(4,coll.count()),
                        where={"tenant_id": tenant_id})
    return [{"text": text, "source": meta["filename"], "document_id": meta["document_id"],
             "chunk": meta["chunk"]} for text,meta in zip(result["documents"][0], result["metadatas"][0])]
