#!/usr/bin/env python3
"""
Direct Supabase connection test
"""

import os
from dotenv import load_dotenv
from supabase.client import create_client
import requests

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print(f"🔍 Testing Supabase Connection...")
print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_KEY[:20]}...")

try:
    # Test direct HTTP request first
    print("\n🌐 Testing direct HTTP request...")
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/articles",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        },
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Direct HTTP request successful")
        data = response.json()
        print(f"📰 Found {len(data)} articles")
        if data:
            print(f"First article: {data[0].get('headline', 'No headline')}")
    else:
        print(f"❌ HTTP request failed: {response.text}")
    
    # Test Supabase client
    print("\n🔧 Testing Supabase client...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Test articles table
    print("📰 Testing articles table...")
    result = supabase.table('articles').select('*').limit(5).execute()
    print(f"✅ Articles query successful: {len(result.data)} articles found")
    
    if result.data:
        print("📄 Sample article:")
        article = result.data[0]
        print(f"  - ID: {article.get('id')}")
        print(f"  - Headline: {article.get('headline')}")
        print(f"  - Category: {article.get('category')}")
        print(f"  - Source: {article.get('source')}")
    
    # Test users table
    print("\n👥 Testing users table...")
    users_result = supabase.table('users').select('*').limit(3).execute()
    print(f"✅ Users query successful: {len(users_result.data)} users found")
    
    print("\n🎉 All tests passed! Database is working correctly.")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
