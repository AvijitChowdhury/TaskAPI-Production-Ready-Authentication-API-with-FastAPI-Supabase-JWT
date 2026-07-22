from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print("URL:", url)
print("Key starts with:", key[:20])

client = create_client(url, key)

try:
    response = client.auth.sign_up({
        "email": "testuser123456789@example.com",
        "password": "Password123!"
    })
    print("SUCCESS")
    print(response)
except Exception as e:
    print("ERROR:")
    print(type(e).__name__)
    print(repr(e))