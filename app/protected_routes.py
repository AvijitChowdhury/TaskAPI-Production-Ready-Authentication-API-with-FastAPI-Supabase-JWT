# ============================================================
# app/protected_routes.py — Public and protected endpoints
#
# Stage 2: GET /public/info        → no auth, open to anyone
# Stage 3: GET /protected/profile  → verify token, return user
# Stage 4: GET /protected/dashboard → second protected route
#           (proves the middleware reuse — zero new auth code)
#
# HOW THE GUARD IS APPLIED:
#   user = Depends(get_current_user)
#   FastAPI calls get_current_user() before the route body runs.
#   If the token is bad → 401 is raised inside the dependency.
#   If the token is good → user object is injected into the handler.
#   The route body never deals with token extraction or verification.
# ============================================================

from fastapi import APIRouter, Depends
from app.dependencies import get_current_user

router = APIRouter(tags=["endpoints"])


# ── Stage 2: Public endpoint ──────────────────────────────────

@router.get(
    "/public/info",
    summary="Public info — no auth required",
    description="Open to anyone. No token needed.",
)
def public_info():
    """
    GET /public/info

    No authentication. Returns a welcome message.
    Status code: 200
    """
    return {
        "message": "Welcome stranger! This info is public.",
        "hint":    "Log in and call /protected/profile to see your account details.",
    }


# ── Stage 3 & 4: Protected profile endpoint ───────────────────

@router.get(
    "/protected/profile",
    summary="Private profile — Bearer token required",
    description=(
        "Returns the logged-in user's profile. "
        "Requires `Authorization: Bearer <token>` header."
    ),
)
def profile(user=Depends(get_current_user)):
    """
    GET /protected/profile

    Protected by get_current_user dependency.
    FastAPI runs the dependency first:
      • Missing token  → 401 Access token required
      • Bad/expired    → 401 Invalid or expired token
      • Valid token    → user object injected here

    Returns safe metadata — never passwords or internal ids.
    Status code: 200
    """
    return {
        "message":    "Welcome to your private profile.",
        "user": {
            "id":         str(user.id),
            "email":      user.email,
            "created_at": str(user.created_at),
            "last_sign_in": str(user.last_sign_in_at),
        },
    }


# ── Stage 4: Second protected route (proves guard reuse) ─────

@router.get(
    "/protected/dashboard",
    summary="Private dashboard — Bearer token required",
    description=(
        "A second protected route. Uses the EXACT same dependency as /profile. "
        "Zero new auth code written — that reuse is the point of Stage 4."
    ),
)
def dashboard(user=Depends(get_current_user)):
    """
    GET /protected/dashboard

    Stage 4 checkpoint:
      Same Depends(get_current_user) guard, no new auth logic.
      Bad token → 401. Valid token → 200.

    This proves the middleware pattern:
      One guard, applied to every locked door.
    """
    return {
        "message": "Welcome to your private dashboard.",
        "user_id": str(user.id),
        "email":   user.email,
        "note":    (
            "This route uses the same guard as /protected/profile. "
            "Zero new auth code was written to protect it."
        ),
    }


# ── Stretch: 403 Forbidden example ───────────────────────────

@router.get(
    "/protected/admin",
    summary="Admin-only route — 403 for non-admins",
    description=(
        "Authenticated users can reach this route, but only 'admins' may use it. "
        "Demonstrates 401 vs 403: 401 = 'who are you?', 403 = 'I know you, and no.'"
    ),
)
def admin_only(user=Depends(get_current_user)):
    """
    GET /protected/admin

    Stretch goal: a 403 case.

    401 Unauthorized = "I don't know who you are" (missing/bad token).
    403 Forbidden    = "I know exactly who you are — and you still may not."

    Here we check the user's email for an admin domain.
    A real app would check a `role` claim in the JWT or a DB lookup.
    """
    from fastapi import HTTPException, status

    # Simple demo: only @admin.com emails are "admins"
    # In production: check user.app_metadata["role"] == "admin"
    if not user.email or not user.email.endswith("@admin.com"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Access denied. You are authenticated but not authorised. "
                "401 = 'who are you?' — 403 = 'I know you, and no.'"
            ),
        )

    return {
        "message": "Welcome, admin.",
        "user_id": str(user.id),
        "email":   user.email,
    }
