#!/usr/bin/env python3
"""
Manual database setup script for TeenBuzz
"""

import os
from dotenv import load_dotenv
from supabase.client import create_client

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def setup_database():
    """Set up the database tables manually"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Test basic connection
        try:
            result = supabase.table('articles').select('*').limit(1).execute()
            print("✅ Articles table exists and is accessible")
        except Exception as e:
            print(f"⚠️  Articles table issue: {str(e)}")
            print("💡 You may need to create the articles table in Supabase dashboard")
        
        # Test users table
        try:
            result = supabase.table('users').select('*').limit(1).execute()
            print("✅ Users table exists and is accessible")
        except Exception as e:
            print(f"⚠️  Users table issue: {str(e)}")
            print("💡 You may need to create the users table in Supabase dashboard")
        
        # Try to insert a test article
        try:
            test_article = {
                'headline': 'Test Article - Database Connection Working!',
                'content': 'This is a test article to verify that the database connection is working properly. If you can see this article, then the TeenBuzz application is successfully connected to your Supabase database.',
                'source': 'TeenBuzz Test',
                'category': 'Technology',
                'relevance': 'Testing database connectivity'
            }
            result = supabase.table('articles').insert(test_article).execute()
            print("✅ Successfully inserted test article")
            print(f"📰 Article ID: {result.data[0]['id']}")
        except Exception as e:
            print(f"⚠️  Could not insert test article: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing TeenBuzz Database Connection...")
    success = setup_database()
    if success:
        print("\n✅ Database connection test completed!")
    else:
        print("\n❌ Database connection test failed.")
