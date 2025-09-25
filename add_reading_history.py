#!/usr/bin/env python3
"""
Add reading history for current articles to test Continue Reading functionality
"""

from database_manager import get_database
from datetime import datetime

def add_reading_history():
    """Add reading history for current articles"""
    db = get_database()
    if not db:
        print("❌ Database connection failed")
        return False
    
    print("📖 Adding reading history for current articles...")
    
    try:
        # Get admin user ID
        admin_users = db.select('users', where='username = ?', params=('admin',), limit=1)
        if not admin_users:
            print("❌ Admin user not found")
            return False
        
        admin_id = admin_users[0]['id']
        print(f"✅ Found admin user: {admin_id}")
        
        # Get current articles
        articles = db.select('articles')
        if not articles:
            print("❌ No articles found")
            return False
        
        print(f"📚 Found {len(articles)} articles")
        
        # Add reading history for first 3 articles with different progress levels
        reading_history_data = [
            {'article_id': articles[0]['id'], 'progress_percentage': 0.25, 'description': '25% read'},
            {'article_id': articles[1]['id'], 'progress_percentage': 0.60, 'description': '60% read'},
            {'article_id': articles[2]['id'], 'progress_percentage': 0.85, 'description': '85% read'}
        ]
        
        for data in reading_history_data:
            # Check if reading history already exists
            existing = db.select('reading_history', 
                               where='user_id = ? AND article_id = ?', 
                               params=(admin_id, data['article_id']), 
                               limit=1)
            
            if existing:
                print(f"⏭️  Reading history already exists for article {data['article_id']}")
                continue
            
            # Create reading history record
            history_record = {
                'user_id': admin_id,
                'article_id': data['article_id'],
                'progress_percentage': data['progress_percentage'],
                'last_read_at': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Insert reading history
            history_id = db.insert('reading_history', history_record)
            print(f"✅ Added reading history: Article {data['article_id']} - {data['description']}")
        
        # Test the continue reading functionality
        print(f"\n🧪 Testing continue reading functionality...")
        from user_management import user_manager
        continue_reading = user_manager.get_continue_reading_articles(admin_id, limit=5)
        
        print(f"📖 Continue reading articles found: {len(continue_reading)}")
        for article in continue_reading:
            print(f"  - {article['headline'][:50]}... ({article['reading_progress']:.1%} progress)")
        
        print("🎉 Reading history added successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error adding reading history: {e}")
        return False

if __name__ == "__main__":
    add_reading_history()

