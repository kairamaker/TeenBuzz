#!/usr/bin/env python3
"""
Setup script for article features (likes, bookmarks, comments)
"""

from database_manager import get_database
from datetime import datetime

def setup_article_features():
    """Set up database tables for article features"""
    db = get_database()
    if not db:
        print("❌ Database connection failed")
        return False
    
    print("🔄 Setting up article features...")
    
    try:
        # Create article_likes table
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS article_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES articles(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE (article_id, user_id)
            )
        """)
        print("✅ Created article_likes table")
        
        # Create article_bookmarks table
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS article_bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES articles(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE (article_id, user_id)
            )
        """)
        print("✅ Created article_bookmarks table")
        
        # Create comments table
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                parent_id INTEGER,
                likes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES articles(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (parent_id) REFERENCES comments(id)
            )
        """)
        print("✅ Created comments table")
        
        # Create comment_likes table
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS comment_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comment_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (comment_id) REFERENCES comments(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE (comment_id, user_id)
            )
        """)
        print("✅ Created comment_likes table")
        
        # Create indexes for performance
        db.execute_query("CREATE INDEX IF NOT EXISTS idx_article_likes_article_id ON article_likes (article_id)")
        db.execute_query("CREATE INDEX IF NOT EXISTS idx_article_likes_user_id ON article_likes (user_id)")
        db.execute_query("CREATE INDEX IF NOT EXISTS idx_article_bookmarks_article_id ON article_bookmarks (article_id)")
        db.execute_query("CREATE INDEX IF NOT EXISTS idx_article_bookmarks_user_id ON article_bookmarks (user_id)")
        db.execute_query("CREATE INDEX IF NOT EXISTS idx_comments_article_id ON comments (article_id)")
        db.execute_query("CREATE INDEX IF NOT EXISTS idx_comments_user_id ON comments (user_id)")
        db.execute_query("CREATE INDEX IF NOT EXISTS idx_comments_parent_id ON comments (parent_id)")
        print("✅ Created indexes")
        
        print("🎉 Article features setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up article features: {e}")
        return False

if __name__ == "__main__":
    setup_article_features()

