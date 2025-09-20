#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

print("=== TeenBuzz Database Connection Debug ===")
print()

# Check environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_KEY: {SUPABASE_KEY[:20] if SUPABASE_KEY else 'None'}...")
print()

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Environment variables not set!")
    print("Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
    exit(1)

if SUPABASE_URL.startswith('your_') or SUPABASE_KEY.startswith('your_'):
    print("❌ Placeholder values detected!")
    print("Please replace 'your_supabase_url' and 'your_supabase_key' with real values")
    exit(1)

print("✅ Environment variables look good")
print()

# Try to create client
try:
    print("Attempting to create Supabase client...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client created successfully")
except Exception as e:
    print(f"❌ Failed to create Supabase client: {e}")
    exit(1)

# Try to test connection
try:
    print("Testing database connection...")
    result = supabase.table('articles').select('*').limit(1).execute()
    print(f"✅ Database connection successful!")
    print(f"Query result: {result}")
    if result.data:
        print(f"Found {len(result.data)} articles")
    else:
        print("No articles found in database")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print(f"Error type: {type(e).__name__}")
    exit(1)

print()
print("🎉 All tests passed! Your database connection is working.")
