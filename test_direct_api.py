#!/usr/bin/env python3

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

print("=== Testing Direct API Connection ===")
print()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print(f"Testing: {SUPABASE_URL}")
print()

# Try to get the IP address of Supabase
try:
    import socket
    # Try to resolve the main Supabase domain
    supabase_ip = socket.gethostbyname('supabase.com')
    print(f"Supabase IP: {supabase_ip}")
    
    # Try to make a direct request using the IP
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Host': 'kkevjmmtwvvmrxmqpltv.supabase.co'
    }
    
    # Try the direct API endpoint
    api_url = f"https://{supabase_ip}/rest/v1/articles"
    print(f"Trying direct API: {api_url}")
    
    response = requests.get(api_url, headers=headers, timeout=10)
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS! Found {len(data)} articles in database")
        print("Sample article:", data[0]['headline'] if data else "No articles")
    else:
        print(f"❌ API Error: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=== Alternative: Check Supabase Dashboard ===")
print("1. Go to your Supabase dashboard")
print("2. Click on 'Table Editor'")
print("3. Check if you can see the 'articles' table")
print("4. If you see it, the database is working!")
print()
print("Your app will work once DNS resolves!")
