#!/usr/bin/env python3
"""
Check auto-fetch logs and database for potential duplicate issues
"""

import os
from dotenv import load_dotenv
from supabase.client import create_client
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def check_auto_fetch_status():
    """Check the status of auto-fetch and potential issues"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Check today's articles
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time()).isoformat()
        today_end = datetime.combine(today, datetime.max.time()).isoformat()
        
        today_result = supabase.table('articles').select('*').gte('created_at', today_start).lte('created_at', today_end).execute()
        today_articles = today_result.data or []
        
        print(f"📅 Today's articles ({len(today_articles)}):")
        print("-" * 50)
        
        for i, article in enumerate(today_articles, 1):
            print(f"{i}. {article['headline']}")
            print(f"   ID: {article['id']}, Category: {article['category']}")
            print(f"   Created: {article['created_at']}")
            print()
        
        # Check if daily fetch limit is working
        if len(today_articles) > 5:
            print(f"⚠️  WARNING: Found {len(today_articles)} articles today (should be max 5)")
        else:
            print(f"✅ Daily fetch limit working correctly ({len(today_articles)} articles today)")
        
        # Check for any recent duplicate creation patterns
        print("\n🔍 Checking for potential duplicate patterns...")
        
        # Group by source and category to see if same source/category combinations exist
        source_category_groups = {}
        for article in today_articles:
            key = f"{article['source']}_{article['category']}"
            if key not in source_category_groups:
                source_category_groups[key] = []
            source_category_groups[key].append(article)
        
        potential_issues = []
        for key, articles in source_category_groups.items():
            if len(articles) > 1:
                potential_issues.append({
                    'source_category': key,
                    'count': len(articles),
                    'articles': articles
                })
        
        if potential_issues:
            print("⚠️  Found potential issues:")
            for issue in potential_issues:
                print(f"   - {issue['source_category']}: {issue['count']} articles")
                for article in issue['articles']:
                    print(f"     * {article['headline']} (ID: {article['id']})")
        else:
            print("✅ No obvious duplicate patterns found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in check_auto_fetch_status: {str(e)}")
        return False

def check_log_file():
    """Check if daily_fetch.log exists and show recent entries"""
    log_file = "daily_fetch.log"
    
    if os.path.exists(log_file):
        print(f"\n📝 Recent log entries from {log_file}:")
        print("-" * 50)
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Show last 20 lines
                for line in lines[-20:]:
                    print(line.strip())
        except Exception as e:
            print(f"❌ Error reading log file: {str(e)}")
    else:
        print(f"\n📝 No log file found at {log_file}")

if __name__ == "__main__":
    print("🚀 Starting TeenBuzz Auto-Fetch Status Check...")
    
    check_auto_fetch_status()
    check_log_file() 