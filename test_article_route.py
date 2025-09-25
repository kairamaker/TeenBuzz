#!/usr/bin/env python3
"""
Test the article route functionality
"""

from database_manager import get_database
from user_management import user_manager

def test_article_query():
    """Test the article query that's failing"""
    try:
        db = get_database()
        if db:
            print("✅ Database connection successful")
            articles = db.select('articles', where='id = ?', params=(1,), limit=1)
            print(f"✅ Found {len(articles)} articles with id=1")
            if articles:
                article = articles[0]
                print(f"✅ Article: {article['headline']}")
                return article
            else:
                print("❌ No article found")
                return None
        else:
            print("❌ Database connection failed")
            return None
    except Exception as e:
        print(f"❌ Error in article query: {e}")
        return None

def test_user_manager():
    """Test user manager functionality"""
    try:
        print("✅ User manager imported successfully")
        # Test with a fake user ID
        fake_user_id = "test-user-123"
        result = user_manager.update_reading_progress(fake_user_id, 1, 0.5)
        print(f"✅ User manager test result: {result}")
        return True
    except Exception as e:
        print(f"❌ Error in user manager: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Article Route Components")
    print("=" * 40)
    
    print("\n1. Testing database query...")
    article = test_article_query()
    
    print("\n2. Testing user manager...")
    user_manager_ok = test_user_manager()
    
    print("\n3. Summary:")
    if article and user_manager_ok:
        print("✅ All components working - issue might be in Flask app")
    else:
        print("❌ Found issues with components")

