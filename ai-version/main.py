# ============================================================
# ai-version/main.py — Stage 7: AI-generated version
#
# Generated from the prompt in PROMPT.md.
# Kept in its own folder — the hand-built version is the submission.
# ============================================================

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

bearer_scheme = HTTPBearer(auto_error=False)


class AuthRequest(BaseModel):
    email: str
    password: str


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        response = supabase.auth.get_user(credentials.credentials)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if response.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return response.user


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Connected to Supabase: {SUPABASE_URL}")
    yield


app = FastAPI(title="Auth API — AI Version", lifespan=lifespan)


@app.post("/auth/signup", status_code=201)
def signup(body: AuthRequest):
    if not body.email or not body.email.strip():
        raise HTTPException(400, detail="email is required")
    if not body.password:
        raise HTTPException(400, detail="password is required")
    try:
        res = supabase.auth.sign_up({"email": body.email, "password": body.password})
    except Exception as e:
        raise HTTPException(400, detail=str(e))
    if res.user is None:
        raise HTTPException(400, detail="Signup failed")
    return {"message": "Account created", "user": {"id": str(res.user.id), "email": res.user.email}}


@app.post("/auth/login", status_code=200)
def login(body: AuthRequest):
    if not body.email or not body.password:
        raise HTTPException(400, detail="email and password are required")
    try:
        res = supabase.auth.sign_in_with_password({"email": body.email, "password": body.password})
    except Exception:
        raise HTTPException(401, detail="Invalid login credentials")
    if res.session is None:
        raise HTTPException(401, detail="Invalid login credentials")
    return {
        "access_token":  res.session.access_token,
        "refresh_token": res.session.refresh_token,
        "token_type":    "bearer",
    }


@app.post("/auth/logout", status_code=204, dependencies=[Depends(get_current_user)])
def logout():
    supabase.auth.sign_out()


@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.get("/protected/profile")
def profile(user=Depends(get_current_user)):
    return {
        "id":         str(user.id),
        "email":      user.email,
        "created_at": str(user.created_at),
    }


@app.get("/protected/dashboard")
def dashboard(user=Depends(get_current_user)):
    return {"message": "Dashboard", "user_id": str(user.id), "email": user.email}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version="1.0.0", routes=app.routes)
    schema.setdefault("components", {})
    schema["components"]["securitySchemes"] = {
        "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path, methods in schema.get("paths", {}).items():
        if "/protected/" in path or path == "/auth/logout":
            for method in methods.values():
                method["security"] = [{"bearerAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = custom_openapi
