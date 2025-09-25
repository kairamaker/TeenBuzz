#!/usr/bin/env python3
"""
Debug Reading History Database Structure
"""

from database_manager import get_database

def debug_reading_history():
    db = get_database()
    if not db:
        print("❌ Database not initialized")
        return
    
    print("🔍 Debugging Reading History Database Structure")
    print("=" * 50)
    
    # Check reading_history table structure
    print("\n1. Reading History Table Structure:")
    try:
        schema = db.execute_query('PRAGMA table_info(reading_history)')
        print(f"   Found {len(schema)} columns:")
        for i, col in enumerate(schema):
            print(f"   {i}: {col[1]} ({col[2]})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check articles table structure
    print("\n2. Articles Table Structure:")
    try:
        schema = db.execute_query('PRAGMA table_info(articles)')
        print(f"   Found {len(schema)} columns:")
        for i, col in enumerate(schema):
            print(f"   {i}: {col[1]} ({col[2]})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check sample data
    print("\n3. Sample Reading History Data:")
    try:
        data = db.execute_query('SELECT * FROM reading_history LIMIT 1')
        if data:
            print(f"   Found {len(data[0])} columns in row:")
            for i, value in enumerate(data[0]):
                print(f"   {i}: {value}")
        else:
            print("   No data found")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test the problematic query
    print("\n4. Testing JOIN Query:")
    try:
        result = db.execute_query("""
            SELECT rh.id, rh.user_id, rh.article_id, rh.progress_percentage, rh.last_read_at, rh.created_at, rh.updated_at,
                   a.id, a.headline, a.content, a.category, a.source, a.url, a.created_at, a.updated_at, 
                   a.drawn_by_user_id, a.publish_date, a.tags, a.views, a.likes
            FROM reading_history rh
            JOIN articles a ON rh.article_id = a.id
            LIMIT 1
        """)
        if result:
            print(f"   ✅ JOIN query successful: {len(result[0])} columns")
            for i, value in enumerate(result[0]):
                print(f"   {i}: {value}")
        else:
            print("   No results from JOIN query")
    except Exception as e:
        print(f"   ❌ JOIN query failed: {e}")

if __name__ == '__main__':
    debug_reading_history()

