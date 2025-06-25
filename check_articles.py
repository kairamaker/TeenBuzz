#!/usr/bin/env python3
"""
Script to check what articles are currently in the database
"""

from app import supabase

def check_articles():
    """Check all articles in the database"""
    try:
        result = supabase.table('articles').select('*').order('created_at', desc=True).execute()
        articles = result.data or []
        
        print(f"📊 Found {len(articles)} articles in database:")
        print("-" * 50)
        
        for i, article in enumerate(articles, 1):
            print(f"{i}. ID: {article['id']}")
            print(f"   Headline: {article['headline']}")
            print(f"   Category: {article['category']}")
            print(f"   Source: {article['source']}")
            print(f"   Created: {article['created_at']}")
            print()
            
    except Exception as e:
        print(f"❌ Error checking articles: {str(e)}")

if __name__ == "__main__":
    check_articles() 