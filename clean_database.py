#!/usr/bin/env python3
"""
Script to clean up the database and remove duplicate articles
"""

from app import supabase

def clean_database():
    """Remove all articles and start fresh"""
    try:
        # Delete all articles
        result = supabase.table('articles').delete().neq('id', 0).execute()
        print("✅ Cleared all articles from database")
        
        # Verify it's empty
        check_result = supabase.table('articles').select('*').execute()
        print(f"📊 Database now contains {len(check_result.data)} articles")
        
    except Exception as e:
        print(f"❌ Error cleaning database: {str(e)}")

if __name__ == "__main__":
    print("Cleaning database...")
    clean_database() 