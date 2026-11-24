import os
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Header, HTTPException
from pwdlib import PasswordHash
from app.db import db_connection

hasher = PasswordHash.recommended()

def create_token(user_id: int, tenant_id: int) -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret or len(secret) < 32:
        raise HTTPException(503, "JWT_SECRET must be configured (at least 32 characters)")
    return jwt.encode({"sub": str(user_id), "tenant_id": tenant_id,
                       "exp": datetime.now(timezone.utc) + timedelta(hours=12)}, secret, algorithm="HS256")

def current_user(authorization: str | None = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Bearer token required")
    try:
        claims = jwt.decode(authorization[7:], os.environ["JWT_SECRET"], algorithms=["HS256"])
        user_id = int(claims["sub"])
        tenant_id = int(claims["tenant_id"])
    except (jwt.PyJWTError, ValueError, KeyError):
        raise HTTPException(401, "Invalid token")
    with db_connection() as db:
        user = db.execute("SELECT id,tenant_id,email FROM users WHERE id=? AND tenant_id=?",
                          (user_id, tenant_id)).fetchone()
    if user is None:
        raise HTTPException(401, "Unknown user")
    return dict(user)
