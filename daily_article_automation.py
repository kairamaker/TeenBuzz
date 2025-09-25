#!/usr/bin/env python3
"""
Daily Article Automation for TeenBuzz
Production-ready script for automated daily article fetching
"""

import os
import sys
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from advanced_article_fetcher import fetch_real_articles, add_articles_to_database
from database_manager import get_database

# Set up logging
def setup_logging():
    """Set up comprehensive logging"""
    log_dir = project_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Create log filename with date
    log_filename = log_dir / f"daily_fetch_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def cleanup_old_articles(days_to_keep=30):
    """Remove articles older than specified days"""
    logger = logging.getLogger(__name__)
    
    try:
        db = get_database()
        if not db:
            logger.error("❌ Database connection failed during cleanup")
            return False
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_iso = cutoff_date.isoformat()
        
        # Count articles to be deleted
        count_query = "SELECT COUNT(*) as count FROM articles WHERE created_at < ?"
        count_result = db.execute_query(count_query, (cutoff_iso,))
        articles_to_delete = count_result[0]['count']
        
        if articles_to_delete > 0:
            # Delete old articles
            delete_query = "DELETE FROM articles WHERE created_at < ?"
            db.execute_query(delete_query, (cutoff_iso,))
            
            logger.info(f"🧹 Cleaned up {articles_to_delete} articles older than {days_to_keep} days")
        else:
            logger.info("🧹 No old articles to clean up")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")
        return False

def get_database_stats():
    """Get current database statistics"""
    try:
        db = get_database()
        if not db:
            return None
        
        # Get total articles
        total_query = "SELECT COUNT(*) as count FROM articles"
        total_result = db.execute_query(total_query)
        total_articles = total_result[0]['count']
        
        # Get articles by category
        category_query = """
            SELECT category, COUNT(*) as count 
            FROM articles 
            WHERE category IS NOT NULL 
            GROUP BY category 
            ORDER BY count DESC
        """
        category_results = db.execute_query(category_query)
        
        # Get recent articles (last 24 hours)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        recent_query = "SELECT COUNT(*) as count FROM articles WHERE created_at > ?"
        recent_result = db.execute_query(recent_query, (yesterday,))
        recent_articles = recent_result[0]['count']
        
        return {
            'total_articles': total_articles,
            'recent_articles_24h': recent_articles,
            'categories': category_results
        }
        
    except Exception as e:
        logging.getLogger(__name__).error(f"❌ Error getting database stats: {e}")
        return None

def daily_article_fetch():
    """Main daily article fetching function"""
    logger = setup_logging()
    
    logger.info("🚀 Starting daily article automation...")
    logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get initial stats
    initial_stats = get_database_stats()
    if initial_stats:
        logger.info(f"📊 Initial stats: {initial_stats['total_articles']} total articles, {initial_stats['recent_articles_24h']} recent")
    
    try:
        # Fetch articles
        logger.info("📰 Fetching articles from RSS feeds...")
        articles = fetch_real_articles()
        
        if articles:
            logger.info(f"📊 Fetched {len(articles)} articles from RSS feeds")
            
            # Add to database
            logger.info("💾 Adding articles to database...")
            success = add_articles_to_database(articles)
            
            if success:
                logger.info(f"✅ Successfully added {len(articles)} new articles")
            else:
                logger.error("❌ Failed to add articles to database")
                return False
        else:
            logger.warning("⚠️ No articles fetched from RSS feeds")
            return False
        
        # Get final stats
        final_stats = get_database_stats()
        if final_stats:
            logger.info(f"📊 Final stats: {final_stats['total_articles']} total articles, {final_stats['recent_articles_24h']} recent")
            
            # Log category breakdown
            logger.info("📂 Category breakdown:")
            for category in final_stats['categories']:
                logger.info(f"  - {category['category']}: {category['count']} articles")
        
        # Cleanup old articles (weekly)
        if datetime.now().weekday() == 6:  # Sunday
            logger.info("🧹 Running weekly cleanup...")
            cleanup_old_articles(days_to_keep=30)
        
        logger.info("✅ Daily article automation completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in daily article fetch: {e}")
        return False

def main():
    """Main function"""
    try:
        success = daily_article_fetch()
        
        if success:
            print("✅ Daily automation completed successfully!")
            sys.exit(0)
        else:
            print("❌ Daily automation failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Daily automation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

