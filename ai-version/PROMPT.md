# Stage 7 — AI Rematch: The Prompt I Used

## My Prompt

```
I need a secure FastAPI API using Supabase Auth as the Identity Provider.
Python 3.12, FastAPI, supabase Python SDK (supabase==2.31.0).

Build exactly these five endpoints:

POST /auth/signup     → 201 on success | 400 if email or password missing
POST /auth/login      → 200 + access_token + refresh_token | 400 missing fields | 401 invalid creds
POST /auth/logout     → 204 No Content | 401 if no/bad token (PROTECTED)
GET  /protected/profile   → 200 + user id/email/created_at | 401 if no/bad token (PROTECTED)
GET  /public/info     → 200 {"message": "Welcome stranger! This info is public."} — no auth

Rules:
- NEVER store or hash passwords yourself — forward to supabase.auth.sign_up() / sign_in_with_password()
- Verify tokens with supabase.auth.get_user(token) — real network call, not local JWT decode
- Auth check must be a REUSABLE FastAPI dependency (Depends) — NOT copy-pasted into each route
- Extract token from "Authorization: Bearer <token>" header — reject if missing with 401
- Configure Swagger UI HTTPBearer security scheme so lock icon appears on protected routes
- Load SUPABASE_URL and SUPABASE_KEY from .env using python-dotenv
- Use anon key only — never service_role key
- Status codes: 201 signup, 200 login/read, 204 logout, 400 missing input, 401 auth failure
- All error responses must be JSON: {"detail": "..."}
- Add a second protected route GET /protected/dashboard to prove the dependency reuse

Put code in these files:
  main.py, app/supabase_client.py, app/dependencies.py,
  app/auth_routes.py, app/protected_routes.py
```
