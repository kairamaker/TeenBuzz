#!/usr/bin/env python3

import os
import requests
import socket
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

print("=== TeenBuzz Database Connection Fix ===")
print()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_KEY: {SUPABASE_KEY[:20] if SUPABASE_KEY else 'None'}...")
print()

# Test 1: Basic DNS resolution
print("1. Testing DNS resolution...")
try:
    socket.gethostbyname('syazoykzdnlqmelqnozz.supabase.co')
    print("✅ DNS resolution successful")
except socket.gaierror as e:
    print(f"❌ DNS resolution failed: {e}")
    print("   This is the main issue - the domain is not resolving")
print()

# Test 2: Try alternative Supabase domains
print("2. Testing alternative Supabase domains...")
alternative_domains = [
    'supabase.com',
    'app.supabase.com',
    'api.supabase.com'
]

for domain in alternative_domains:
    try:
        socket.gethostbyname(domain)
        print(f"✅ {domain} resolves")
    except socket.gaierror:
        print(f"❌ {domain} does not resolve")
print()

# Test 3: Check if it's a network connectivity issue
print("3. Testing basic internet connectivity...")
try:
    response = requests.get('https://google.com', timeout=5)
    print(f"✅ Internet connectivity works (status: {response.status_code})")
except Exception as e:
    print(f"❌ Internet connectivity issue: {e}")
print()

# Test 4: Try using a different approach - direct API call
print("4. Testing direct API approach...")
if SUPABASE_URL and SUPABASE_KEY:
    try:
        # Try to make a direct HTTP request to the API
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Try the REST API endpoint directly
        api_url = f"{SUPABASE_URL}/rest/v1/articles"
        print(f"   Trying API URL: {api_url}")
        
        response = requests.get(api_url, headers=headers, timeout=10)
        print(f"✅ Direct API call successful (status: {response.status_code})")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} articles in database")
        else:
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout error: {e}")
    except Exception as e:
        print(f"❌ Other error: {e}")
else:
    print("❌ Missing Supabase credentials")
print()

# Test 5: Try creating a new Supabase client with error handling
print("5. Testing Supabase client creation...")
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client created successfully")
        
        # Try a simple query
        result = supabase.table('articles').select('*').limit(1).execute()
        print(f"✅ Database query successful: {result}")
        
    except Exception as e:
        print(f"❌ Supabase client error: {e}")
        print(f"   Error type: {type(e).__name__}")
else:
    print("❌ Missing Supabase credentials")
print()

print("=== Recommendations ===")
print("1. Check your internet connection")
print("2. Try using a VPN or different network")
print("3. Check if your ISP is blocking Supabase")
print("4. Try creating a new Supabase project")
print("5. Contact Supabase support if the issue persists")
