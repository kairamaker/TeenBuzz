#!/usr/bin/env python3
"""
Scheduled Article Fetcher for TeenBuzz
Runs automatically to fetch fresh articles daily
"""

import schedule
import time
import logging
from datetime import datetime
from advanced_article_fetcher import fetch_real_articles, add_articles_to_database

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('article_fetch.log'),
        logging.StreamHandler()
    ]
)

def daily_article_fetch():
    """Fetch articles daily"""
    logging.info("🚀 Starting daily article fetch...")
    
    try:
        # Fetch articles
        articles = fetch_real_articles()
        
        if articles:
            # Add to database
            success = add_articles_to_database(articles)
            
            if success:
                logging.info(f"✅ Daily fetch completed successfully! Added {len(articles)} articles.")
            else:
                logging.error("❌ Failed to add articles to database")
        else:
            logging.warning("⚠️ No articles fetched today")
            
    except Exception as e:
        logging.error(f"❌ Error in daily fetch: {e}")

def cleanup_old_articles():
    """Remove articles older than 30 days"""
    from database_manager import get_database
    
    logging.info("🧹 Starting article cleanup...")
    
    try:
        db = get_database()
        if not db:
            logging.error("❌ Database connection failed")
            return
        
        # Calculate date 30 days ago
        thirty_days_ago = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        thirty_days_ago = thirty_days_ago.replace(day=thirty_days_ago.day - 30)
        
        # Delete old articles
        result = db.execute_query(
            "DELETE FROM articles WHERE created_at < ?",
            (thirty_days_ago.isoformat(),)
        )
        
        logging.info(f"✅ Cleanup completed. Removed old articles.")
        
    except Exception as e:
        logging.error(f"❌ Error in cleanup: {e}")

def main():
    """Main scheduler function"""
    logging.info("📅 Starting TeenBuzz Article Scheduler...")
    
    # Schedule daily article fetch at 6 AM
    schedule.every().day.at("06:00").do(daily_article_fetch)
    
    # Schedule weekly cleanup on Sundays at 2 AM
    schedule.every().sunday.at("02:00").do(cleanup_old_articles)
    
    # Run initial fetch
    logging.info("🔄 Running initial article fetch...")
    daily_article_fetch()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()

