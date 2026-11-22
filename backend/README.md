## BizMind API foundation

From `backend/` run `python -m pip install -r requirements.txt`, then `uvicorn app.main:app --reload`.

Visit http://localhost:8000/docs and test `/api/v1/health`.

This is only the first foundation stage; auth, RAG and tenant isolation are not implemented yet.
