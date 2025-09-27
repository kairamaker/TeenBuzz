#!/usr/bin/env python3
"""
Setup Railway Database with Articles
This script will populate the Railway database with articles
"""

import os
import sys
from database_manager import get_database
from advanced_article_fetcher import fetch_real_articles, add_articles_to_database

def setup_railway_database():
    """Setup the Railway database with articles"""
    print("🚀 Setting up Railway database...")
    
    try:
        # Get database connection
        db = get_database()
        if not db:
            print("❌ Could not connect to database")
            return False
        
        print("✅ Connected to database")
        
        # Check if articles already exist
        existing_articles = db.select('articles', limit=1)
        if existing_articles:
            print(f"📰 Database already has {len(existing_articles)} articles")
            return True
        
        print("📡 Fetching real articles...")
        
        # Fetch articles from news sources
        articles = fetch_real_articles()
        
        if not articles:
            print("❌ No articles fetched")
            return False
        
        print(f"✅ Fetched {len(articles)} articles")
        
        # Add articles to database
        success = add_articles_to_database(articles)
        
        if success:
            print("✅ Successfully added articles to Railway database")
            return True
        else:
            print("❌ Failed to add articles to database")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

if __name__ == '__main__':
    success = setup_railway_database()
    if success:
        print("🎉 Railway database setup complete!")
    else:
        print("💥 Railway database setup failed!")
        sys.exit(1)
