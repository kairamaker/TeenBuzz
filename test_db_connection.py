#!/usr/bin/env python3
"""
Test script to check database connection and table status
"""

import os
from dotenv import load_dotenv
from supabase.client import create_client

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def test_connection():
    """Test Supabase connection and table status"""
    print("🔍 Testing TeenBuzz Database Connection...")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Test articles table
        print("\n📰 Testing articles table...")
        try:
            result = supabase.table('articles').select('id, headline').limit(1).execute()
            print(f"✅ Articles table accessible - Found {len(result.data)} articles")
        except Exception as e:
            print(f"❌ Articles table error: {str(e)}")
        
        # Test users table
        print("\n👥 Testing users table...")
        try:
            result = supabase.table('users').select('id, username').limit(1).execute()
            print(f"✅ Users table accessible - Found {len(result.data)} users")
        except Exception as e:
            print(f"❌ Users table error: {str(e)}")
            print("💡 You may need to create the users table first")
        
        # Test user_draws table
        print("\n🎲 Testing user_draws table...")
        try:
            result = supabase.table('user_draws').select('id').limit(1).execute()
            print(f"✅ User draws table accessible - Found {len(result.data)} draws")
        except Exception as e:
            print(f"❌ User draws table error: {str(e)}")
            print("💡 You may need to create the user_draws table first")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection() 