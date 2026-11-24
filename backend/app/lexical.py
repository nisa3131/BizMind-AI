"""Low-memory retrieval for ephemeral public demos."""
import math
import re
from collections import Counter
from app.db import db_connection

def terms(text: str):
    return Counter(re.findall(r"\w+", text.casefold()))

def add_chunks(tenant_id, document_id, chunks, filename):
    with db_connection() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS lexical_chunks (
            tenant_id INTEGER NOT NULL, document_id INTEGER NOT NULL,
            chunk INTEGER NOT NULL, filename TEXT NOT NULL, text TEXT NOT NULL,
            PRIMARY KEY(tenant_id, document_id, chunk))""")
        db.executemany("INSERT OR REPLACE INTO lexical_chunks VALUES(?,?,?,?,?)",
            [(tenant_id, document_id, i, filename, text) for i,text in enumerate(chunks)])

def search(tenant_id, question):
    query = terms(question)
    with db_connection() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS lexical_chunks (
            tenant_id INTEGER NOT NULL, document_id INTEGER NOT NULL,
            chunk INTEGER NOT NULL, filename TEXT NOT NULL, text TEXT NOT NULL,
            PRIMARY KEY(tenant_id, document_id, chunk))""")
        rows = db.execute("SELECT * FROM lexical_chunks WHERE tenant_id=?", (tenant_id,)).fetchall()
    ranked = []
    for row in rows:
        words = terms(row["text"])
        dot = sum(n * words.get(w,0) for w,n in query.items())
        norm = math.sqrt(sum(n*n for n in query.values())*sum(n*n for n in words.values()))
        if dot and norm:
            ranked.append((dot/norm, {"text":row["text"], "source":row["filename"], "document_id":row["document_id"], "chunk":row["chunk"]}))
    ranked.sort(key=lambda item:item[0], reverse=True)
    return [item for _,item in ranked[:4]]
