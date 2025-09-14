#!/usr/bin/env python3
"""
Test Supabase connection with different approaches
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print(f"🔍 Testing Supabase Connection...")
print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_KEY[:20]}...")

# Test 1: Try with different timeout and headers
print("\n🌐 Test 1: Direct HTTP with extended timeout...")
try:
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        },
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Connection successful!")
        print(f"Response: {response.text[:200]}...")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Test 2: Try with different user agent
print("\n🌐 Test 2: With different user agent...")
try:
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        },
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Connection successful!")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Test 3: Try just the base URL without /rest/v1/
print("\n🌐 Test 3: Base URL only...")
try:
    response = requests.get(
        SUPABASE_URL,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        },
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code in [200, 404, 405]:  # 404/405 might be expected for base URL
        print("✅ Base URL is reachable!")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n🔍 If all tests fail, the issue might be:")
print("1. DNS resolution problem")
print("2. Network firewall blocking the connection")
print("3. Project might be in a different region")
print("4. Temporary Supabase service issue")
