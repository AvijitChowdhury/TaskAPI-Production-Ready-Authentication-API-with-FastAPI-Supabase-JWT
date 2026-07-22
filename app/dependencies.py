# ============================================================
# app/dependencies.py — Stage 4: Reusable auth dependency
#
# This is FastAPI's equivalent of Express middleware.
# Instead of copy-pasting token verification into every route,
# we write it ONCE here and inject it with Depends(get_current_user).
#
# HOW FASTAPI DEPENDENCIES WORK:
#   @router.get("/protected/profile")
#   def profile(user = Depends(get_current_user)):
#       # get_current_user ran first; if token was bad → 401 already raised
#       # if token is good → user object is injected here
#       return {"email": user.email}
#
# WHAT THIS FUNCTION DOES (Stages 2 → 3 → 4):
#   Stage 2: extract the token from the Authorization header
#   Stage 3: verify it with supabase.auth.get_user(token)
#   Stage 4: encapsulate it here so ALL protected routes share ONE guard
#
# TOKEN VERIFICATION — WHY get_user() AND NOT LOCAL DECODE?
#   supabase.auth.get_user(token) makes a real network call to Supabase.
#   Supabase checks the signature AND the expiry server-side.
#   This is trustworthy: a tampered or expired token is rejected by Supabase.
#   Local JWT decode is faster but skips revocation; Supabase's check is safe.
# ============================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.supabase_client import supabase

# HTTPBearer:
#   • Adds a "lock" icon to Swagger UI on every route that uses this
#   • Extracts the token from "Authorization: Bearer <token>" automatically
#   • Returns 403 if the header is missing (we override to 401 below)
#
# auto_error=False: we handle the missing-header case ourselves so we can
# return 401 (not 403) and a JSON body matching the assignment spec.
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    """
    FastAPI dependency — run before any protected route.

    Steps:
      1. Check the Authorization header exists and contains a Bearer token.
         Missing or malformed → 401 {"error": "Access token required"}

      2. Call supabase.auth.get_user(token) to verify with Supabase.
         Expired, tampered, or unknown → 401 {"error": "Invalid or expired token"}

      3. Return the verified user object.
         The route receives it via: user = Depends(get_current_user)

    Usage:
        # Option A — inject user into route function
        def my_route(user = Depends(get_current_user)):
            return {"email": user.email}

        # Option B — just guard, don't need user data
        @router.post("/logout", dependencies=[Depends(get_current_user)])
        def logout(): ...
    """

    # ── Step 1: Check header present ─────────────────────────
    # credentials is None when the Authorization header is missing
    # or when the scheme is not "Bearer"
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
            headers={"WWW-Authenticate": "Bearer"},
            # WWW-Authenticate header is required by RFC 7235 for 401 responses
        )

    token = credentials.credentials   # the raw JWT string

    # ── Step 2: Verify with Supabase ─────────────────────────
    # get_user() makes a network call to Supabase.
    # It checks the signature AND the expiry — can't be faked.
    try:
        response = supabase.auth.get_user(token)
    except Exception:
        # Supabase SDK raises if the token is invalid or expired
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

    # ── Step 3: Return the verified user ─────────────────────
    # Injected into the route function as the `user` parameter.
    return response.user
