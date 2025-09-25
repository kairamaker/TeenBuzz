#!/usr/bin/env python3
"""
Setup Reading History System for TeenBuzz
Creates the reading_history table and adds sample data
"""

from database_manager import get_database
from datetime import datetime
import random

def setup_reading_history():
    """Create reading_history table and add sample data"""
    db = get_database()
    if not db:
        print("❌ Database not initialized. Cannot setup reading history.")
        return False

    print("🔄 Setting up reading history system...")
    
    # Create reading_history table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS reading_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        article_id INTEGER NOT NULL,
        progress_percentage REAL DEFAULT 0.0,
        last_read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (article_id) REFERENCES articles(id),
        UNIQUE(user_id, article_id)
    )
    """
    
    try:
        db.execute_query(create_table_sql)
        print("✅ Created reading_history table")
    except Exception as e:
        print(f"❌ Error creating reading_history table: {e}")
        return False
    
    # Create index for better performance
    try:
        db.execute_query("CREATE INDEX IF NOT EXISTS idx_reading_history_user_id ON reading_history(user_id)")
        db.execute_query("CREATE INDEX IF NOT EXISTS idx_reading_history_article_id ON reading_history(article_id)")
        db.execute_query("CREATE INDEX IF NOT EXISTS idx_reading_history_last_read ON reading_history(last_read_at)")
        print("✅ Created indexes for reading_history table")
    except Exception as e:
        print(f"⚠️  Warning: Could not create indexes: {e}")
    
    # Add sample reading history data
    print("\n📚 Adding sample reading history data...")
    
    # Get existing users and articles
    users = db.select('users', limit=10)
    articles = db.select('articles', limit=10)
    
    if not users or not articles:
        print("⚠️  No users or articles found. Skipping sample data.")
        return True
    
    sample_reading_history = []
    
    # Create reading history for each user with some articles
    for user in users[:3]:  # Use first 3 users
        user_id = user['id']
        if not user_id:
            continue
            
        # Each user has read 2-4 articles with different progress levels
        num_articles = random.randint(2, 4)
        selected_articles = random.sample(articles, min(num_articles, len(articles)))
        
        for article in selected_articles:
            # Random progress between 25% and 95% (not 100% to show "Continue Reading")
            progress = round(random.uniform(0.25, 0.95), 2)
            
            # Random last read time (within last 7 days)
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            last_read = datetime.now().replace(hour=hours_ago, minute=random.randint(0, 59), second=0, microsecond=0)
            last_read = last_read.replace(day=last_read.day - days_ago)
            
            reading_record = {
                'user_id': str(user_id),
                'article_id': article['id'],
                'progress_percentage': progress,
                'last_read_at': last_read.isoformat(),
                'created_at': last_read.isoformat(),
                'updated_at': last_read.isoformat()
            }
            
            sample_reading_history.append(reading_record)
    
    # Insert sample data
    for record in sample_reading_history:
        try:
            db.insert('reading_history', record)
            print(f"  ✅ Added reading history: User {record['user_id']} read {progress*100:.0f}% of article {record['article_id']}")
        except Exception as e:
            print(f"  ⚠️  Could not insert reading history record: {e}")
    
    print(f"\n✅ Reading history setup complete!")
    print(f"   - Created reading_history table")
    print(f"   - Added {len(sample_reading_history)} sample reading records")
    print(f"   - Users have partial reading progress (25-95%)")
    
    return True

def verify_reading_history():
    """Verify the reading history setup"""
    db = get_database()
    if not db:
        return False
    
    print("\n🔍 Verifying reading history setup...")
    
    # Check table structure
    try:
        schema = db.execute_query("PRAGMA table_info(reading_history)")
        print(f"✅ reading_history table has {len(schema)} columns:")
        for column in schema:
            print(f"   - {column[1]} ({column[2]})")
    except Exception as e:
        print(f"❌ Error checking table schema: {e}")
        return False
    
    # Check sample data
    try:
        records = db.select('reading_history', limit=5)
        print(f"\n✅ Found {len(records)} reading history records:")
        for record in records:
            print(f"   - User {record['user_id']}: Article {record['article_id']} ({record['progress_percentage']*100:.0f}% read)")
    except Exception as e:
        print(f"❌ Error checking sample data: {e}")
        return False
    
    return True

if __name__ == '__main__':
    print("🚀 Setting up Reading History System for TeenBuzz")
    print("=" * 50)
    
    success = setup_reading_history()
    if success:
        verify_reading_history()
        print("\n🎉 Reading history system is ready!")
        print("\nNext steps:")
        print("1. Update article view route to track reading progress")
        print("2. Modify homepage to show 'Continue Reading' section")
        print("3. Add progress tracking to article template")
    else:
        print("\n❌ Failed to setup reading history system")

