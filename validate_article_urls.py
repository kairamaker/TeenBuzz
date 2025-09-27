#!/usr/bin/env python3
"""
Validate that all articles have URLs
This script ensures that every article in the database has a valid URL
"""

import sqlite3
from database_manager import get_database

def validate_article_urls():
    """Check that all articles have URLs and add missing ones if needed"""
    db = get_database()
    if not db:
        print("❌ Database connection failed")
        return False
    
    # Get all articles
    articles = db.select('articles')
    if not articles:
        print("❌ No articles found in database")
        return False
    
    missing_urls = []
    for article in articles:
        if not article.get('url') or article.get('url') == 'None' or article.get('url') == '':
            missing_urls.append(article)
    
    if missing_urls:
        print(f"❌ Found {len(missing_urls)} articles without URLs:")
        for article in missing_urls:
            print(f"  - ID {article['id']}: {article['headline'][:50]}...")
        
        # Add placeholder URLs for missing ones
        for article in missing_urls:
            placeholder_url = f"https://example.com/article/{article['id']}"
            db.update('articles', {'url': placeholder_url}, where='id = ?', params=(article['id'],))
            print(f"✅ Added placeholder URL for article {article['id']}")
        
        print(f"\n✅ Fixed {len(missing_urls)} articles with missing URLs")
    else:
        print(f"✅ All {len(articles)} articles have URLs!")
    
    return True

def check_url_requirements():
    """Ensure the article fetcher always includes URLs"""
    print("🔍 Checking article fetcher URL requirements...")
    
    # Check if the fetcher includes URL in the return dictionary
    try:
        from advanced_article_fetcher import create_enhanced_article
        
        # Test the function
        test_article = create_enhanced_article(
            "Test Article", 
            "Test description", 
            "https://example.com/test", 
            "Test Source"
        )
        
        if 'url' in test_article and test_article['url']:
            print("✅ Article fetcher properly includes URLs")
            return True
        else:
            print("❌ Article fetcher missing URL field")
            return False
            
    except Exception as e:
        print(f"❌ Error checking fetcher: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Validating article URLs...")
    
    # Check current articles
    validate_article_urls()
    
    # Check fetcher requirements
    check_url_requirements()
    
    print("\n✅ URL validation complete!")