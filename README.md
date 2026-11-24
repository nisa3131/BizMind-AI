# BizMind AI

A multi-tenant document intelligence and customer-support prototype built with FastAPI, SQLite, ChromaDB, React/TypeScript and Docker.

## Windows quick start

Install Git and Docker Desktop (WSL 2). Open PowerShell in the repository folder.

```powershell
git pull
if (!(Test-Path .env)) {
    $secret = [guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N")
    "JWT_SECRET=$secret" | Set-Content -Encoding ascii .env
}
docker compose up --build
```

Dashboard: http://localhost:3000
API docs: http://localhost:8000/docs

Create an account, upload a PDF or UTF-8 FAQ, and ask a question. Sign in to a different business to verify documents and analytics remain separate.

## Optional hosted answer generation

By default, the application returns cited excerpts locally. Add OPENAI_API_KEY and OPENAI_MODEL to your local .env to enable hosted generation. This sends your question and retrieved document excerpts to OpenAI; only enable it for data you have permission to share. Never commit the .env file. Provider failures fall back to excerpts.

## Architecture

React → Nginx → FastAPI → JWT authorization → SQLite and tenant-filtered Chroma retrieval → optional hosted generation.

## Current limitations

Prototype, not a production security guarantee. Citation numbering is checked, not semantic entailment. Scanned PDFs need OCR outside this application. SQLite is used for the local demo; PostgreSQL migration, rate limiting, observability and production deployment remain future work.
