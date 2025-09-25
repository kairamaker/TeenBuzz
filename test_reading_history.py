#!/usr/bin/env python3
"""
Test Reading History System for TeenBuzz
"""

from database_manager import get_database
from user_management import user_manager
import json

def test_reading_history():
    """Test the reading history functionality"""
    print("🧪 Testing Reading History System")
    print("=" * 40)
    
    # Get database connection
    db = get_database()
    if not db:
        print("❌ Database not initialized")
        return False
    
    # Get a test user
    users = db.select('users', limit=1)
    if not users:
        print("❌ No users found in database")
        return False
    
    test_user = users[0]
    user_id = test_user['id']
    print(f"✅ Testing with user: {test_user['username']} (ID: {user_id})")
    
    # Test 1: Get continue reading articles
    print("\n1. Testing get_continue_reading_articles...")
    continue_reading = user_manager.get_continue_reading_articles(user_id, limit=5)
    print(f"   Found {len(continue_reading)} continue reading articles:")
    for article in continue_reading:
        progress = article.get('reading_progress', 0) * 100
        print(f"   - {article['headline'][:50]}... ({progress:.0f}% read)")
    
    # Test 2: Update reading progress
    print("\n2. Testing update_reading_progress...")
    if continue_reading:
        test_article = continue_reading[0]
        article_id = test_article['id']
        new_progress = 0.85  # 85%
        
        success, message = user_manager.update_reading_progress(user_id, article_id, new_progress)
        if success:
            print(f"   ✅ Updated progress to {new_progress*100:.0f}%: {message}")
        else:
            print(f"   ❌ Failed to update progress: {message}")
    
    # Test 3: Get reading history
    print("\n3. Testing get_user_reading_history...")
    history = user_manager.get_user_reading_history(user_id, limit=5)
    print(f"   Found {len(history)} reading history records:")
    for record in history:
        progress = record.get('progress_percentage', 0) * 100
        print(f"   - {record['headline'][:50]}... ({progress:.0f}% read)")
    
    # Test 4: Check database directly
    print("\n4. Testing database queries...")
    try:
        reading_records = db.select('reading_history', where='user_id = ?', params=(str(user_id),), limit=5)
        print(f"   ✅ Database query successful: {len(reading_records)} records")
        for record in reading_records:
            progress = record.get('progress_percentage', 0) * 100
            print(f"   - Article {record['article_id']}: {progress:.0f}% read")
    except Exception as e:
        print(f"   ❌ Database query failed: {e}")
    
    print("\n🎉 Reading History System Test Complete!")
    return True

def test_web_endpoints():
    """Test web endpoints for reading history"""
    print("\n🌐 Testing Web Endpoints")
    print("=" * 30)
    
    import requests
    
    base_url = "http://localhost:5003"
    
    # Test homepage
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Homepage accessible")
            if "Continue Reading" in response.text:
                print("✅ Continue Reading section found in homepage")
            else:
                print("⚠️  Continue Reading section not found")
        else:
            print(f"❌ Homepage returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Homepage test failed: {e}")
    
    # Test article page
    try:
        response = requests.get(f"{base_url}/article/1")
        if response.status_code == 200:
            print("✅ Article page accessible")
            if "reading-progress" in response.text:
                print("✅ Reading progress indicator found")
            else:
                print("⚠️  Reading progress indicator not found")
        else:
            print(f"❌ Article page returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Article page test failed: {e}")

if __name__ == '__main__':
    test_reading_history()
    test_web_endpoints()
    
    print("\n📋 Next Steps:")
    print("1. Login to the app: http://localhost:5003/login")
    print("2. View an article to start tracking progress")
    print("3. Check the homepage for 'Continue Reading' section")
    print("4. Scroll through articles to see progress updates")

