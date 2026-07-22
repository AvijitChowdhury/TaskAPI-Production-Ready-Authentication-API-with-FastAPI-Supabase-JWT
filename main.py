# ============================================================
# main.py — Application entrypoint
#
# Stage 0: Creates the FastAPI app, connects to Supabase on startup
# Stage 5: Configures Swagger UI with HTTPBearer security scheme
#          so the lock icon appears on all protected routes
#
# SWAGGER UI AND THE PADLOCK:
#   FastAPI generates /docs automatically.
#   We add a "bearerAuth" security scheme to the OpenAPI spec.
#   Every protected route gets the padlock by declaring the
#   HTTPBearer dependency (via get_current_user → bearer_scheme).
#   Users click "Authorize", paste their JWT, and all protected
#   routes include it automatically — no manual header editing.
# ============================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.auth_routes      import router as auth_router
from app.protected_routes import router as protected_router
from app.supabase_client  import supabase, SUPABASE_URL


# ── Stage 0: Startup lifespan ─────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once on startup. Verifies Supabase connection.
    Logs a clear message so you know it's working (Stage 0 checkpoint).
    """
    print("=" * 55)
    print("  Task Auth API starting up...")
    print(f"  Connected to Supabase: {SUPABASE_URL}")
    print("  Server running — open http://localhost:8000/docs")
    print("=" * 55)
    yield   # server accepts requests
    print("Server shutting down.")


# ── Create app ────────────────────────────────────────────────

app = FastAPI(
    title       = "Auth API — FlyRank W4 A4",
    description = (
        "Secure API with Supabase Auth — signup, login, logout, and protected routes.\n\n"
        "## How to use the protected endpoints\n"
        "1. Call `POST /auth/signup` to create an account.\n"
        "2. Call `POST /auth/login` to get an `access_token`.\n"
        "3. Click **Authorize** (lock icon), paste the token, click **Authorize**.\n"
        "4. All protected routes will include your token automatically.\n\n"
        "## Auth flow\n"
        "```\n"
        "Client → POST /auth/login → Supabase → JWT returned\n"
        "Client → GET /protected/profile (Authorization: Bearer JWT) → Supabase verifies → 200\n"
        "```"
    ),
    version     = "1.0.0",
    lifespan    = lifespan,
)

# ── Mount routers ─────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(protected_router)


# ── Root & health ─────────────────────────────────────────────

@app.get("/", tags=["info"], summary="API info")
def root():
    return {
        "name":    "Auth API",
        "version": "1.0.0",
        "docs":    "/docs",
        "routes": {
            "signup":    "POST /auth/signup",
            "login":     "POST /auth/login",
            "logout":    "POST /auth/logout   (token required)",
            "profile":   "GET  /protected/profile (token required)",
            "dashboard": "GET  /protected/dashboard (token required)",
            "public":    "GET  /public/info",
        },
    }


@app.get("/health", tags=["info"], summary="Health check")
def health():
    return {"status": "ok"}


# ── Stage 5: Swagger HTTPBearer security scheme ───────────────
#
# This customises the auto-generated OpenAPI spec to add a
# "bearerAuth" security scheme. FastAPI already generates the spec;
# we inject the securitySchemes block that tells Swagger:
#   "This API uses HTTP Bearer tokens."
#
# The padlock appears automatically on routes that declare
# the HTTPBearer dependency (our get_current_user dependency
# uses bearer_scheme = HTTPBearer(), which registers it).
#
# Result: Swagger UI shows an "Authorize" button at the top.
# Users paste their JWT once → all locked routes use it.

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title       = app.title,
        version     = app.version,
        description = app.description,
        routes      = app.routes,
    )

    # Add the Bearer token security scheme
    schema.setdefault("components", {})
    schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type":         "http",
            "scheme":       "bearer",
            "bearerFormat": "JWT",
            "description":  (
                "Paste the `access_token` from `POST /auth/login`. "
                "Example: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`"
            ),
        }
    }

    # Apply security to every path that is "protected" (has Bearer in it)
    # FastAPI's HTTPBearer dependency also marks these automatically,
    # but we make it explicit here so Swagger shows the lock icon.
    for path, methods in schema.get("paths", {}).items():
        if "/protected/" in path or path == "/auth/logout":
            for method in methods.values():
                method["security"] = [{"bearerAuth": []}]

    app.openapi_schema = schema
    return app.openapi_schema


# app.openapi = custom_openapi


# ── Run locally ───────────────────────────────────────────────
# uvicorn main:app --reload
# Open: http://localhost:8000/docs
