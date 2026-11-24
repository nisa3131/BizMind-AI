import os
from fastapi.staticfiles import StaticFiles
from app.main import app

if len(os.getenv("JWT_SECRET", "")) < 32 or len(os.getenv("BIZMIND_INVITE_CODE", "")) < 16:
    raise RuntimeError("Configure JWT_SECRET and BIZMIND_INVITE_CODE before starting the cloud demo")
app.mount("/", StaticFiles(directory="/srv/static", html=True), name="dashboard")
