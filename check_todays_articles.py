#!/usr/bin/env python3
"""
Script to check today's articles and diagnose the "no articles found" issue
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase.client import create_client

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def check_todays_articles():
    """Check what articles exist for today"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Get current date info
        now = datetime.now()
        today = now.date()
        today_start = datetime.combine(today, datetime.min.time()).isoformat()
        today_end = datetime.combine(today, datetime.max.time()).isoformat()
        
        print(f"📅 Checking for articles on: {today}")
        print(f"🕐 Time range: {today_start} to {today_end}")
        print(f"🌍 Current timezone: {now.astimezone().tzinfo}")
        
        # Check articles created today
        today_articles = supabase.table('articles').select('id, headline, created_at').gte('created_at', today_start).lte('created_at', today_end).execute()
        
        print(f"\n📰 Articles found for today: {len(today_articles.data)}")
        
        if today_articles.data:
            print("\nToday's articles:")
            for article in today_articles.data:
                print(f"  • {article['headline']} (ID: {article['id']})")
                print(f"    Created: {article['created_at']}")
        else:
            print("❌ No articles found for today")
        
        # Check recent articles (last 7 days)
        week_ago = (now - timedelta(days=7)).isoformat()
        recent_articles = supabase.table('articles').select('id, headline, created_at').gte('created_at', week_ago).order('created_at', desc=True).execute()
        
        print(f"\n📰 Recent articles (last 7 days): {len(recent_articles.data)}")
        
        if recent_articles.data:
            print("\nRecent articles:")
            for article in recent_articles.data[:5]:  # Show first 5
                print(f"  • {article['headline']} (ID: {article['id']})")
                print(f"    Created: {article['created_at']}")
        
        # Check total articles
        all_articles = supabase.table('articles').select('id').execute()
        print(f"\n📊 Total articles in database: {len(all_articles.data)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking articles: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Checking TeenBuzz articles...")
    check_todays_articles() 