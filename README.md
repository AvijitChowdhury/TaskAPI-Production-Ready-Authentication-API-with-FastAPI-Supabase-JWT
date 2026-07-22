# Auth API — FlyRank W4 A4: Auth · Login & Protect

Secure FastAPI API with Supabase Auth — signup, login, logout, JWT verification, protected routes, and Swagger HTTPBearer.

---

## What This Is

A backend authentication system built around the **trust triangle**:

```
Client → POST /auth/login → Supabase (checks credentials, signs JWT)
                                  ↓
                           access_token (JWT) returned
                                  ↓
Client → GET /protected/profile → Your server (verifies JWT with Supabase) → 200 or 401
```

You never store passwords. You never write cryptography. Supabase does both — your job is receiving a token, verifying it, and opening (or refusing) the door.

---

## Setup

### 1. Create a Supabase project

1. Go to [supabase.com](https://supabase.com) → New project
2. In **Project Settings → API**, copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon/public key** → `SUPABASE_KEY` (never use the `service_role` key)
3. In **Authentication → Sign In / Providers → Email**, turn **"Confirm email" OFF** for this practice project

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your real SUPABASE_URL and SUPABASE_KEY
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run

```bash
uvicorn main:app --reload
```

Server starts on **http://localhost:8000**

---

## Endpoints

| Method | Path | Auth | Status | Description |
|--------|------|------|--------|-------------|
| `POST` | `/auth/signup` | None | 201, 400 | Register a new user |
| `POST` | `/auth/login` | None | 200, 400, 401 | Log in, receive JWT |
| `POST` | `/auth/logout` | 🔒 Bearer | 204, 401 | End session |
| `GET` | `/protected/profile` | 🔒 Bearer | 200, 401 | Private profile data |
| `GET` | `/protected/dashboard` | 🔒 Bearer | 200, 401 | Private dashboard |
| `GET` | `/protected/admin` | 🔒 Bearer | 200, 401, 403 | Admin-only (stretch) |
| `GET` | `/public/info` | None | 200 | Public, open data |
| `GET` | `/health` | None | 200 | Health check |

### Status Codes

| Code | Meaning |
|------|---------|
| 201 | Signup created |
| 200 | Success |
| 204 | Logout — no body |
| 400 | Missing/invalid input |
| 401 | Missing, bad, or expired token |
| 403 | Authenticated but not authorised |

---

## The Full Auth Flow (curl)

```bash
# 1. Sign up
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"YourPass123!"}'
# → 201 {"user": {"id": "...", "email": "you@example.com"}}

# 2. Log in — copy the access_token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"YourPass123!"}'
# → 200 {"access_token": "eyJ...", "refresh_token": "...", "token_type": "bearer"}

# 3. Call a protected route
curl http://localhost:8000/protected/profile \
  -H "Authorization: Bearer eyJ..."
# → 200 {"user": {"id": "...", "email": "...", "created_at": "..."}}

# 4. Tamper with the token → 401
curl http://localhost:8000/protected/profile \
  -H "Authorization: Bearer eyJ...TAMPERED"
# → 401 {"detail": "Invalid or expired token"}

# 5. Call without token → 401
curl http://localhost:8000/protected/profile
# → 401 {"detail": "Access token required"}

# 6. Public route — no token needed
curl http://localhost:8000/public/info
# → 200 {"message": "Welcome stranger! This info is public."}

# 7. Log out
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer eyJ..."
# → 204 (empty body)
```

---

## Swagger UI (Stage 5)

Open **http://localhost:8000/docs**

1. Click **Authorize** (🔒 button, top right)
2. Paste your `access_token` from `/auth/login`
3. Click **Authorize** → **Close**
4. All protected routes now include your token automatically
5. Click **Try it out** on any endpoint

Protected routes show a 🔒 icon next to them.

> *(Screenshot: add DB Browser / Swagger screenshot here)*

---

## Project Structure

```
auth-api/
├── main.py                   ← FastAPI app, startup, Swagger HTTPBearer config
├── requirements.txt
├── .env                      ← gitignored (your real secrets)
├── .env.example              ← committed (key names, placeholder values)
├── .gitignore
│
├── app/
│   ├── __init__.py
│   ├── supabase_client.py    ← Stage 0: Supabase client from .env
│   ├── dependencies.py       ← Stage 4: reusable get_current_user dependency
│   ├── auth_routes.py        ← Stage 1+4: signup, login, logout
│   └── protected_routes.py   ← Stage 2+3+4: public/info, profile, dashboard
│
└── ai-version/               ← Stage 7: AI-generated version for comparison
    ├── main.py
    └── PROMPT.md
```

---

## Architecture

### The Trust Triangle

```
      ┌──────────────┐
      │    CLIENT    │
      └──────┬───────┘
             │ 1. POST /auth/login (email+password)
             ▼
      ┌──────────────┐         ┌──────────────────┐
      │  YOUR SERVER │────────▶│  SUPABASE AUTH   │
      │  (FastAPI)   │◀────────│  (Identity Prov) │
      └──────┬───────┘  token  └──────────────────┘
             │ 2. access_token (JWT) returned
             ▼
      ┌──────────────┐
      │    CLIENT    │ stores token
      └──────┬───────┘
             │ 3. GET /protected/profile
             │    Authorization: Bearer <token>
             ▼
      ┌──────────────┐         ┌──────────────────┐
      │  YOUR SERVER │────────▶│  SUPABASE AUTH   │
      │  verifies    │◀────────│  get_user(token) │
      └──────┬───────┘  valid? └──────────────────┘
             │ 4. 200 (valid) or 401 (invalid)
             ▼
      ┌──────────────┐
      │    CLIENT    │
      └──────────────┘
```

### The Reusable Guard (Stage 4)

```python
# Written ONCE in app/dependencies.py
async def get_current_user(credentials = Depends(bearer_scheme)):
    # 1. Check header exists
    # 2. Call supabase.auth.get_user(token)
    # 3. Return verified user OR raise 401

# Applied to ANY route with zero extra auth code:
@router.get("/protected/profile")
def profile(user = Depends(get_current_user)):  # ← one line
    return {"email": user.email}

@router.get("/protected/dashboard")
def dashboard(user = Depends(get_current_user)):  # ← same one line
    return {"email": user.email}
```

One guard. Every locked door. That's the point of Stage 4.

---

## 401 vs 403 — The Difference

| Code | Means | When |
|------|-------|------|
| 401 Unauthorized | "I don't know who you are" | Missing token, bad token, expired token |
| 403 Forbidden | "I know exactly who you are — and no." | Authenticated but not authorised (e.g. non-admin hitting `/protected/admin`) |

```bash
# 401 — no token
curl http://localhost:8000/protected/admin
# → 401 Access token required

# 401 — bad token  
curl http://localhost:8000/protected/admin -H "Authorization: Bearer FAKE"
# → 401 Invalid or expired token

# 403 — valid token, wrong role
curl http://localhost:8000/protected/admin -H "Authorization: Bearer VALID_TOKEN"
# → 403 Access denied. You are authenticated but not authorised.
```

---

## Why We Never Hash Passwords Ourselves

Rolling your own auth is how careers end. Supabase:
- Uses bcrypt to hash passwords before storage
- Signs JWTs with RS256 (asymmetric keys)
- Handles token expiry, refresh, revocation

Your code only ever calls `sign_up()`, `sign_in_with_password()`, `get_user()`, and `sign_out()`.

---

## Security Notes

- `.env` is git-ignored — your Supabase keys never reach GitHub
- We use the **anon key** only — never `service_role` (which bypasses all security)
- All tokens verified with `supabase.auth.get_user()` — a real network call to Supabase, not local decode
- Parameterized inputs everywhere — no SQL injection risk

---

## Stage 7 — AI vs Me

See [`ai-version/PROMPT.md`](ai-version/PROMPT.md) for the full prompt.
See [`ai-version/main.py`](ai-version/main.py) for the generated code.

### Three Concrete Differences

**1. Structure: flat vs layered**
My version splits responsibilities across `supabase_client.py`, `dependencies.py`, `auth_routes.py`, `protected_routes.py`. The AI put everything in one `main.py`. Both work — mine is easier to test and grow.

**2. What it got right**
The AI correctly used `get_user(token)` for verification (not local decode), correctly used `auto_error=False` on `HTTPBearer` to control the 401 response, and correctly applied `Depends(get_current_user)` as a dependency rather than copy-pasting auth code into each route.

**3. What my prompt forgot — and the AI decided silently**
The AI returned `401` for the missing-header case, which is correct. But it did not include a `WWW-Authenticate: Bearer` header in the 401 response. RFC 7235 requires this. My prompt said "return 401" but didn't say "include the WWW-Authenticate header." The AI passed the functional test but failed the spec.

### One Rematch: Improved Prompt

Added: *"All 401 responses must include a `WWW-Authenticate: Bearer` header as required by RFC 7235."*

The regenerated version added `headers={"WWW-Authenticate": "Bearer"}` to every 401 raise.

**The lesson:** The AI's output is exactly as good as your specification. You could only catch that missing header because you know what a correct 401 response looks like — and you know because you built it yourself first.

---

## Git Log (≥6 commits)

```
Stage 0: setup server and supabase client
Stage 1: signup and login routes working
Stage 2: public route and unverified protected route
Stage 3: profile route token verification
Stage 4: auth middleware and logout endpoint
Stage 5: Swagger UI documentation with bearer auth
Stage 6: publish to GitHub and write README
Stage 7: AI vs me (AI code in ai-version/)
```
