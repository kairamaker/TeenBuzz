#!/usr/bin/env python3
"""
Script to periodically check Supabase connection
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def test_connection():
    """Test if Supabase is reachable"""
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            },
            timeout=10
        )
        if response.status_code == 200:
            print("🎉 SUCCESS! Supabase connection is working!")
            print("You can now restart your Flask app to use real data.")
            return True
        else:
            print(f"❌ Connection failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"⏳ Still waiting... ({str(e)[:50]}...)")
        return False

if __name__ == "__main__":
    print("🔍 Checking Supabase connection...")
    print(f"URL: {SUPABASE_URL}")
    print("This will check every 30 minutes until connection works.\n")
    
    while True:
        if test_connection():
            break
        print("⏰ Waiting 30 minutes before next check...")
        time.sleep(1800)  # 30 minutes
