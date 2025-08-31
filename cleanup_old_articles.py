#!/usr/bin/env python3
"""
Script to clean up old articles and keep only recent ones
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase.client import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

def analyze_articles():
    """Analyze articles without deleting any - keep all for user reference"""
    
    print("📊 Analyzing articles (keeping all for user reference)...")
    
    try:
        # Get all articles
        all_articles = supabase.table('articles').select('id, headline, created_at, source').execute()
        
        print(f"📰 Total articles in database: {len(all_articles.data)}")
        
        # Analyze by date
        today = datetime.now().date()
        recent_articles = 0
        week_old_articles = 0
        month_old_articles = 0
        older_articles = 0
        
        for article in all_articles.data:
            created_date = datetime.fromisoformat(article['created_at'].replace('Z', '+00:00')).date()
            days_old = (today - created_date).days
            
            if days_old <= 2:
                recent_articles += 1
            elif days_old <= 7:
                week_old_articles += 1
            elif days_old <= 30:
                month_old_articles += 1
            else:
                older_articles += 1
        
        print(f"📅 Recent articles (last 2 days): {recent_articles}")
        print(f"📅 Week-old articles (3-7 days): {week_old_articles}")
        print(f"📅 Month-old articles (8-30 days): {month_old_articles}")
        print(f"📅 Older articles (30+ days): {older_articles}")
        
        # Show recent articles
        recent_cutoff = (datetime.now() - timedelta(days=2)).isoformat()
        recent_articles_list = supabase.table('articles').select('id, headline, created_at, source').gte('created_at', recent_cutoff).order('created_at', desc=True).execute()
        
        print(f"\n📰 Recent articles (last 2 days):")
        for article in recent_articles_list.data:
            date_str = article['created_at'][:10]
            print(f"  - {date_str}: {article['headline'][:50]}... (Source: {article['source']})")
            
    except Exception as e:
        print(f"❌ Error analyzing articles: {e}")
        
        # Show current article count
        all_articles = supabase.table('articles').select('id').execute()
        print(f"📰 Total articles remaining: {len(all_articles.data)}")
        
        # Show recent articles
        recent_cutoff = (datetime.now() - timedelta(days=2)).isoformat()
        recent_articles = supabase.table('articles').select('id, headline, created_at').gte('created_at', recent_cutoff).execute()
        
        print(f"📅 Recent articles (last 2 days): {len(recent_articles.data)}")
        for article in recent_articles.data:
            date_str = article['created_at'][:10]
            print(f"  - {date_str}: {article['headline'][:50]}...")
            
    except Exception as e:
        print(f"❌ Error analyzing articles: {e}")

def show_article_sources():
    """Show current article sources"""
    
    print("\n📋 Current Article Sources:")
    print("=" * 40)
    
    try:
        result = supabase.table('articles').select('source').execute()
        
        sources = {}
        for article in result.data:
            source = article.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            print(f"- {source}: {count} articles")
            
    except Exception as e:
        print(f"❌ Error getting sources: {e}")

if __name__ == "__main__":
    print("🚀 TeenBuzz Article Analysis")
    print("=" * 50)
    
    analyze_articles()
    show_article_sources()
    
    print("\n✅ Analysis completed!")
