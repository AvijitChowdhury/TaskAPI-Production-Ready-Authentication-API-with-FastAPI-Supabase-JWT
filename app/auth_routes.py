# ============================================================
# app/auth_routes.py — Auth endpoints
#
# Stage 1: POST /auth/signup   → register a new user
# Stage 1: POST /auth/login    → authenticate and receive JWT
# Stage 4: POST /auth/logout   → end the session (protected)
#
# GOLDEN RULE (from the assignment):
#   We never store a password and never hash anything ourselves.
#   We forward credentials to Supabase and verify what it returns.
#   Supabase does all the cryptography.
# ============================================================

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from app.supabase_client import supabase
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Request body schemas ──────────────────────────────────────

class AuthRequest(BaseModel):
    """Body for both signup and login — email + password."""
    email:    str
    password: str


# ── Stage 1: Sign Up ──────────────────────────────────────────

@router.post(
    "/signup",
    status_code=201,
    summary="Register a new user account",
    description=(
        "Creates a new user in Supabase Auth. "
        "No token required. Returns the user object on success."
    ),
)
def signup(body: AuthRequest):
    """
    POST /auth/signup

    Calls supabase.auth.sign_up() with the provided email + password.
    Supabase hashes the password — we never see or store it.

    Status codes:
      201 → user created successfully
      400 → missing/empty email or password
      400 → Supabase rejected the input (e.g. weak password, duplicate email)
    """
    # ── Validate inputs ───────────────────────────────────────
    if not body.email or not body.email.strip():
        raise HTTPException(status_code=400, detail="email is required")
    if not body.password or not body.password.strip():
        raise HTTPException(status_code=400, detail="password is required")

    # ── Call Supabase ─────────────────────────────────────────
    try:
        response = supabase.auth.sign_up({
            "email":    body.email.strip(),
            "password": body.password,
        })
    except Exception as e:
        # Supabase SDK raises on network errors
        raise HTTPException(status_code=400, detail=str(e))

    # ── Check for auth error in response ──────────────────────
    if response.user is None:
        raise HTTPException(
            status_code=400,
            detail="Signup failed — check your email and password.",
        )

    # ── Return user info (never return the password) ──────────
    user = response.user
    return {
        "message": "Account created successfully.",
        "user": {
            "id":         str(user.id),
            "email":      user.email,
            "created_at": str(user.created_at),
        },
    }


# ── Stage 1: Log In ───────────────────────────────────────────

@router.post(
    "/login",
    status_code=200,
    summary="Log in and receive a JWT",
    description=(
        "Authenticates the user with Supabase. "
        "Returns an access token (JWT) and a refresh token on success."
    ),
)
def login(body: AuthRequest):
    """
    POST /auth/login

    Calls supabase.auth.sign_in_with_password().
    Supabase checks the credentials and returns a signed JWT.
    We return that JWT to the client — it is used as the Bearer token
    on all subsequent protected requests.

    Status codes:
      200 → login successful, access_token returned
      400 → missing/empty email or password
      401 → Supabase rejected credentials (wrong email or password)
    """
    # ── Validate inputs ───────────────────────────────────────
    if not body.email or not body.email.strip():
        raise HTTPException(status_code=400, detail="email is required")
    if not body.password or not body.password.strip():
        raise HTTPException(status_code=400, detail="password is required")

    # ── Call Supabase ─────────────────────────────────────────
    try:
        response = supabase.auth.sign_in_with_password({
            "email":    body.email.strip(),
            "password": body.password,
        })
    except Exception as e:
        # Supabase raises an exception on invalid credentials
        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials",
        )

    # ── Check session was returned ────────────────────────────
    if response.session is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials",
        )

    session = response.session
    user    = response.user

    # ── Return tokens ─────────────────────────────────────────
    # The client stores access_token and sends it as:
    #   Authorization: Bearer <access_token>
    return {
        "message":       "Login successful.",
        "access_token":  session.access_token,    # JWT — short-lived (~1 hour)
        "refresh_token": session.refresh_token,   # longer-lived, used to renew
        "token_type":    "bearer",
        "user": {
            "id":    str(user.id),
            "email": user.email,
        },
    }


# ── Stage 4: Log Out ──────────────────────────────────────────

@router.post(
    "/logout",
    status_code=204,
    summary="End the current session",
    description=(
        "Signs out the current user. Requires a valid Bearer token. "
        "Returns 204 No Content on success."
    ),
    dependencies=[Depends(get_current_user)],   # guard: must be logged in
)
def logout():
    """
    POST /auth/logout

    Protected endpoint — requires Authorization: Bearer <token>.
    Calls supabase.auth.sign_out() to invalidate the session.

    Status codes:
      204 → signed out successfully (no body)
      401 → missing or invalid token
    """
    try:
        supabase.auth.sign_out()
    except Exception:
        pass   # sign_out rarely fails; if it does, session expires naturally
    # 204 No Content — FastAPI sends empty body automatically
