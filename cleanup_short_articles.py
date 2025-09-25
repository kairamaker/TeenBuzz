#!/usr/bin/env python3
"""
Clean up short articles - keep only articles with 1000+ words
"""

from database_manager import get_database
from datetime import datetime

def cleanup_short_articles():
    """Remove articles with less than 1000 words"""
    db = get_database()
    if not db:
        print("❌ Database connection failed")
        return False
    
    print("🧹 Starting cleanup of short articles...")
    
    try:
        # Get all articles
        all_articles = db.select('articles')
        print(f"📊 Found {len(all_articles)} total articles")
        
        short_articles = []
        long_articles = []
        
        # Categorize articles by length
        for article in all_articles:
            content = article.get('content', '')
            word_count = len(content.split())
            
            if word_count < 1000:
                short_articles.append({
                    'id': article['id'],
                    'headline': article['headline'],
                    'word_count': word_count
                })
            else:
                long_articles.append({
                    'id': article['id'],
                    'headline': article['headline'],
                    'word_count': word_count
                })
        
        print(f"📏 Analysis:")
        print(f"  📄 Short articles (< 1000 words): {len(short_articles)}")
        print(f"  📚 Long articles (≥ 1000 words): {len(long_articles)}")
        
        if not short_articles:
            print("✅ No short articles to remove!")
            return True
        
        # Show which articles will be removed
        print(f"\n🗑️  Articles to be removed:")
        for article in short_articles:
            print(f"  - {article['headline'][:60]}... ({article['word_count']} words)")
        
        # Confirm deletion
        print(f"\n⚠️  This will permanently delete {len(short_articles)} short articles.")
        print("✅ Proceeding with cleanup...")
        
        # Delete short articles
        deleted_count = 0
        for article in short_articles:
            try:
                # Delete from articles table
                db.execute_query("DELETE FROM articles WHERE id = ?", (article['id'],))
                
                # Also clean up related data
                db.execute_query("DELETE FROM reading_history WHERE article_id = ?", (article['id'],))
                db.execute_query("DELETE FROM article_likes WHERE article_id = ?", (article['id'],))
                db.execute_query("DELETE FROM article_bookmarks WHERE article_id = ?", (article['id'],))
                db.execute_query("DELETE FROM comments WHERE article_id = ?", (article['id'],))
                
                deleted_count += 1
                print(f"  🗑️  Deleted: {article['headline'][:50]}...")
                
            except Exception as e:
                print(f"  ❌ Error deleting article {article['id']}: {e}")
        
        print(f"\n📊 Cleanup Results:")
        print(f"  🗑️  Deleted: {deleted_count} short articles")
        print(f"  📚 Remaining: {len(long_articles)} long articles")
        
        # Show remaining articles
        print(f"\n📚 Remaining long articles:")
        for article in long_articles:
            print(f"  ✅ {article['headline'][:60]}... ({article['word_count']} words)")
        
        print("🎉 Cleanup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False

if __name__ == "__main__":
    cleanup_short_articles()

