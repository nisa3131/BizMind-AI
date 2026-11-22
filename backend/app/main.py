from fastapi import FastAPI

app = FastAPI(title="BizMind AI", version="0.1.0")

@app.get("/api/v1/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "bizmind-api"}
