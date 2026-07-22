<!-- # Auth API

A secure FastAPI authentication service powered by Supabase Auth, designed for signup, login, logout, JWT verification, protected endpoints, and Swagger-based API testing.

## Overview

This project demonstrates a clean backend authentication flow using FastAPI and Supabase. Instead of storing or hashing passwords inside the application, the API delegates identity verification and password handling to Supabase Auth.

The result is a modular, production-friendly structure where:

- the client sends credentials to `POST /auth/login`
- Supabase validates the credentials and issues a JWT
- the client sends that token in the `Authorization: Bearer <token>` header
- the FastAPI backend verifies the token with Supabase before allowing access

## Key Features

- User signup with Supabase Auth
- User login that returns an `access_token` and `refresh_token`
- JWT-protected routes with reusable dependency-based authorization
- Public and private endpoints
- Swagger UI with Bearer token authorization support
- Clean separation of concerns across router and dependency modules

## Tech Stack

- FastAPI
- Supabase Python SDK
- Uvicorn
- Python-dotenv
- Pydantic

## Architecture

The app follows a simple trust model:

```text
Client → FastAPI API → Supabase Auth → JWT issued/validated
```

A reusable `get_current_user()` dependency verifies the incoming Bearer token before any protected route is executed. That keeps the authentication logic centralized and easy to reuse.

## Project Structure

```text
auth-api/
├── main.py
├── requirements.txt
├── .env
├── README.md
├── app/
│   ├── auth_routes.py
│   ├── dependencies.py
│   ├── protected_routes.py
│   └── supabase_client.py
└── ai-version/
    ├── main.py
    └── PROMPT.md
```

## Environment Setup

1. Create a Supabase project in the Supabase dashboard.
2. In Project Settings → API, copy:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
3. Add these values to a local `.env` file.
4. Never commit your `.env` file.

Example:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

## Install and Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Once running, open:

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/signup` | Register a new user |
| `POST` | `/auth/login` | Authenticate and receive JWT tokens |
| `POST` | `/auth/logout` | Sign out the current authenticated user |
| `GET` | `/public/info` | Open public route |
| `GET` | `/protected/profile` | Returns protected user profile details |
| `GET` | `/protected/dashboard` | Protected dashboard endpoint |
| `GET` | `/protected/admin` | Admin-only demonstration route |
| `GET` | `/health` | Health check |

## Example Auth Flow

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"YourPass123!"}'

curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"YourPass123!"}'

curl http://localhost:8000/protected/profile \
  -H "Authorization: Bearer <access_token>"
```

## Swagger Authorization

The FastAPI docs are configured to support Bearer authentication. In the Swagger UI:

1. Open `/docs`
2. Click the Authorize button
3. Paste the `access_token` returned by `/auth/login`
4. Execute protected requests directly from the browser

## Security Notes

- Tokens are verified through Supabase, not by decoding locally in application code.
- The application uses the public/anon key pattern for client-facing authentication interactions.
- Sensitive credentials are stored in `.env` and excluded from version control.

## Screenshots

### Project Workspace and API Setup

![VS Code Project Interface](assets/1_vscode_project_interface.png)

### Signup Flow

![Signup Screenshot](assets/3_signup.png)

### Login Flow

![Login Screenshot](assets/4_login.png)

### Swagger Bearer Authorization

![Bearer Authorize Screenshot](assets/5_bearer_authorize.png)

### Protected Authorization Response

![Protected Authorization Screenshot](assets/6_protected_autho.png)

### Public Info Endpoint

![Public Info Screenshot](assets/7_api_public_info.png)

### Protected Profile Endpoint

![Protected Profile Screenshot](assets/8_protected_profile.png)

### Protected Dashboard Endpoint

![Protected Dashboard Screenshot](assets/9_protected_dashboard.png)

### Admin Protection Demo

![Protected Admin Screenshot](assets/10_protected_admin.png)

## Notes

This project is a learning-focused implementation that shows how to wire a simple, secure authentication backend with FastAPI and Supabase while keeping the codebase readable and maintainable.
 -->
# 🔐 Auth API — FastAPI + Supabase Authentication System

![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)
![Supabase](https://img.shields.io/badge/Supabase-Authentication-3FCF8E?style=for-the-badge&logo=supabase)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)
![JWT](https://img.shields.io/badge/JWT-Security-orange?style=for-the-badge)

A production-style authentication backend built with **FastAPI and Supabase Auth** implementing secure user registration, login, JWT verification, protected routes, logout, and Swagger Bearer authentication.

This project was developed as part of:

> **FlyRank Backend Track — Week 4 Assignment: Authentication, Login & Protected Routes**

---

# 📌 Overview

Modern backend applications require secure identity management without exposing sensitive authentication logic.

This project follows a secure authentication architecture where:

- FastAPI handles API requests
- Supabase Auth manages user identity
- JWT tokens provide secure authorization
- Protected routes validate user identity before returning data


The application follows the principle:

> Never store passwords. Never implement cryptography yourself. Delegate identity management to a trusted authentication provider.

---

# 🔥 Key Features

## Authentication

✅ User signup  
✅ Email/password authentication  
✅ JWT access token generation  
✅ Refresh token support  
✅ Secure logout  
✅ Supabase-managed sessions  


## Authorization

✅ JWT Bearer authentication  
✅ Protected API endpoints  
✅ Reusable authentication dependency  
✅ Role-based authorization example  
✅ Proper 401 and 403 handling  


## Developer Experience

✅ FastAPI Swagger UI integration  
✅ Modular project structure  
✅ Environment variable configuration  
✅ Clean separation of responsibilities  


---

# 🏗 System Architecture

                     USER / CLIENT

                          |
                          |
                          | HTTP Request
                          |
                          v


                +----------------+
                |                |
                |    FastAPI     |
                |    Backend     |
                |                |
                +----------------+

                          |
                          |
          +---------------+---------------+
          |                               |
          v                               v


 +-------------------+          +-------------------+
 |                   |          |                   |
 | Authentication    |          | Protected Routes  |
 | Middleware        |          |                   |
 |                   |          |                   |
 +-------------------+          +-------------------+

          |
          |
          |
          v


    Verify JWT Token


          |
          |
          v


   +----------------+
   |                |
   | Supabase Auth  |
   |                |
   +----------------+


          |
          |
          v


    User Identity Verified


          |
          |
          v


    Protected Response
    
---

# 🔄 Complete Authentication Flow


## 1. Signup Flow

Client

|
|
| POST /auth/signup
|
v

FastAPI Backend

|
|
| sign_up()
|
v

Supabase Auth

|
|
v

User Account Created

---

## 2. Login Flow

Client

|
|
| Email + Password
|
v

FastAPI

|
|
| sign_in_with_password()
|
v

Supabase Authentication

|
|
v

JWT Access Token Returned

|
|
v

Client Stores Token


---

## 3. Protected Route Flow



Client

|
|
| GET /protected/profile
|
| Authorization:
| Bearer <JWT>
|
v

FastAPI Dependency

|
|
| Validate Token
|
v

Supabase get_user()

|
|
+----------------+
| |
| Valid Token |
| |
+----------------+

      |
      |
      v

Return Protected Data


---

# 🛠 Technology Stack


| Technology | Purpose |
|---|---|
| FastAPI | REST API Framework |
| Python | Backend Language |
| Supabase Auth | Identity Provider |
| JWT | Authorization Tokens |
| Uvicorn | ASGI Server |
| Pydantic | Request Validation |
| python-dotenv | Environment Management |


---

# 📂 Project Structure



auth-api/

│
├── main.py
├── requirements.txt
├── README.md
├── .env
├── .env.example
├── .gitignore
│
│
├── app/
│
│ ├── init.py
│ │
│ ├── supabase_client.py
│ │ |
│ │ └── Supabase connection configuration
│ │
│ ├── auth_routes.py
│ │ |
│ │ └── Signup, Login, Logout endpoints
│ │
│ ├── dependencies.py
│ │ |
│ │ └── JWT verification middleware
│ │
│ └── protected_routes.py
│ |
│ └── Protected API endpoints
│
│
└── ai-version/

├── main.py
└── PROMPT.md

---

# ⚙️ Installation & Setup


## 1. Clone Repository


```bash
git clone https://github.com/yourusername/auth-api.git

cd auth-api
2. Create Supabase Project

Create a project:

https://supabase.com

Navigate:

Project Settings
        |
        |
        API

Copy:

SUPABASE_URL

SUPABASE_KEY
3. Configure Environment Variables

Create:

.env

Example:

SUPABASE_URL=https://your-project.supabase.co

SUPABASE_KEY=your-anon-public-key

Important:

Never commit .env
Never expose the service_role key
4. Install Dependencies
pip install -r requirements.txt
5. Start Server
uvicorn main:app --reload

Application:

http://localhost:8000

Swagger Documentation:

http://localhost:8000/docs
📡 API Endpoints
Method	Endpoint	Authentication	Description
POST	/auth/signup	❌	Create user account
POST	/auth/login	❌	Authenticate user
POST	/auth/logout	🔒	Logout user
GET	/public/info	❌	Public information
GET	/protected/profile	🔒	User profile
GET	/protected/dashboard	🔒	Dashboard data
GET	/protected/admin	🔒	Admin-only route
GET	/health	❌	Health check

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
## Screenshots

### Project Workspace and API Setup

![VS Code Project Interface](assets/1_vscode_project_interface.png)

### Signup Flow

![Signup Screenshot](assets/3_signup.png)

### Login Flow

![Login Screenshot](assets/4_login.png)

### Swagger Bearer Authorization

![Bearer Authorize Screenshot](assets/5_bearer_authorize.png)

### Protected Authorization Response

![Protected Authorization Screenshot](assets/6_protected_autho.png)

### Public Info Endpoint

![Public Info Screenshot](assets/7_api_public_info.png)

### Protected Profile Endpoint

![Protected Profile Screenshot](assets/8_protected_profile.png)

### Protected Dashboard Endpoint

![Protected Dashboard Screenshot](assets/9_protected_dashboard.png)

### Admin Protection Demo

![Protected Admin Screenshot](assets/10_protected_admin.png)

## Notes

This project is a learning-focused implementation that shows how to wire a simple, secure authentication backend with FastAPI and Supabase while keeping the codebase readable and maintainable.