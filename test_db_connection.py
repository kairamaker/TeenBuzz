#!/usr/bin/env python3
"""
Test database connection
"""

from database_manager import get_database, get_database_status

def test_db_connection():
    print("Testing database connection...")
    
    try:
        db = get_database()
        if db:
            print(f"✅ Database status: {get_database_status()}")
            
            # Test selecting articles
            articles = db.select('articles', limit=5)
            print(f"✅ Found {len(articles)} articles")
            
            for article in articles:
                print(f"  - {article.get('headline', 'No headline')}")
                print(f"    Tags: {article.get('tags', 'No tags')[:100]}...")
                print()
                
        else:
            print("❌ No database connection")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_db_connection()