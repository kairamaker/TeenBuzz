#!/usr/bin/env python3
"""
Test script to add reading progress data for testing Continue Reading functionality
"""

from database_manager import get_database
from datetime import datetime
import random

def add_test_reading_progress():
    """Add some test reading progress data"""
    db = get_database()
    if not db:
        print("❌ Database connection failed")
        return False
    
    # Get a test user (assuming user ID 1 exists)
    users = db.select('users', limit=1)
    if not users:
        print("❌ No users found in database")
        return False
    
    user_id = users[0]['id']
    print(f"✅ Using test user ID: {user_id}")
    
    # Get some articles
    articles = db.select('articles', limit=5)
    if not articles:
        print("❌ No articles found in database")
        return False
    
    print(f"✅ Found {len(articles)} articles")
    
    # Add reading progress for some articles
    for i, article in enumerate(articles[:3]):
        article_id = article['id']
        
        # Create different progress levels
        if i == 0:
            progress = 0.25  # 25% read
        elif i == 1:
            progress = 0.60  # 60% read
        else:
            progress = 0.85  # 85% read
        
        # Check if reading history already exists
        existing = db.select('reading_history', 
                           where='user_id = ? AND article_id = ?', 
                           params=(str(user_id), article_id), 
                           limit=1)
        
        if existing:
            # Update existing record
            db.update('reading_history', 
                     {'progress_percentage': progress, 
                      'last_read_at': datetime.now().isoformat(),
                      'updated_at': datetime.now().isoformat()}, 
                     'user_id = ? AND article_id = ?', 
                     (str(user_id), article_id))
            print(f"📖 Updated reading progress for article '{article['headline'][:50]}...' to {progress*100:.0f}%")
        else:
            # Create new record
            reading_data = {
                'user_id': str(user_id),
                'article_id': article_id,
                'progress_percentage': progress,
                'last_read_at': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            db.insert('reading_history', reading_data)
            print(f"📖 Added reading progress for article '{article['headline'][:50]}...' at {progress*100:.0f}%")
    
    print("🎉 Test reading progress data added successfully!")
    print(f"💡 Now log in as user '{users[0]['username']}' to see the Continue Reading section")
    return True

if __name__ == "__main__":
    add_test_reading_progress()

