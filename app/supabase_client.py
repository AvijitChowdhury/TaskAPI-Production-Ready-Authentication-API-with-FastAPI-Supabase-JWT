# ============================================================
# app/supabase_client.py — Stage 0: Supabase client
#
# A single shared Supabase client created once at import time.
# All routes and the auth dependency import `supabase` from here.
#
# WHY A SINGLE CLIENT?
#   Creating a client is cheap but we only need one.
#   It reads SUPABASE_URL and SUPABASE_KEY from .env and opens
#   an HTTP connection pool. Every call reuses that pool.
#
# WHICH KEY TO USE — anon vs service_role
#   anon key   → safe to use in your app; respects Row Level Security
#   service_role → bypasses ALL security; NEVER use it here
#   We use the anon key. The assignment explicitly forbids service_role.
# ============================================================

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()   # read .env into os.environ

SUPABASE_URL: str = os.environ["SUPABASE_URL"]
SUPABASE_KEY: str = os.environ["SUPABASE_KEY"]

# Create the shared client — used everywhere in the app
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
