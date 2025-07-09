#!/usr/bin/env python3
"""
Remove duplicate articles from the database
Keeps the most recent version of each article based on headline
"""

import os
from dotenv import load_dotenv
from supabase.client import create_client
from collections import defaultdict

# Load environment variables
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def find_and_remove_duplicates():
    """Find and remove duplicate articles"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Get all articles
        result = supabase.table('articles').select('*').order('created_at', desc=True).execute()
        articles = result.data or []
        
        print(f"📊 Found {len(articles)} total articles")
        
        # Group articles by headline
        headline_groups = defaultdict(list)
        for article in articles:
            headline = article['headline'].strip()
            headline_groups[headline].append(article)
        
        # Find duplicates
        duplicates_to_remove = []
        articles_to_keep = []
        
        for headline, articles_list in headline_groups.items():
            if len(articles_list) > 1:
                print(f"🔍 Found {len(articles_list)} duplicates for: '{headline}'")
                
                # Sort by creation date (newest first)
                articles_list.sort(key=lambda x: x['created_at'], reverse=True)
                
                # Keep the newest one
                articles_to_keep.append(articles_list[0])
                
                # Mark the rest for deletion
                for article in articles_list[1:]:
                    duplicates_to_remove.append(article['id'])
                    print(f"   ❌ Will remove ID {article['id']} (created: {article['created_at']})")
            else:
                articles_to_keep.append(articles_list[0])
        
        if not duplicates_to_remove:
            print("✅ No duplicates found!")
            return True
        
        print(f"\n🗑️  Removing {len(duplicates_to_remove)} duplicate articles...")
        
        # Remove duplicates
        for article_id in duplicates_to_remove:
            try:
                result = supabase.table('articles').delete().eq('id', article_id).execute()
                if result.data:
                    print(f"✅ Removed duplicate article ID: {article_id}")
                else:
                    print(f"⚠️  No article found with ID: {article_id}")
            except Exception as e:
                print(f"❌ Error removing article {article_id}: {str(e)}")
        
        print(f"\n🎉 Duplicate removal completed!")
        print(f"📊 Kept {len(articles_to_keep)} unique articles")
        print(f"🗑️  Removed {len(duplicates_to_remove)} duplicate articles")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in find_and_remove_duplicates: {str(e)}")
        return False

def show_remaining_articles():
    """Show all remaining articles"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Get all articles
        result = supabase.table('articles').select('*').order('created_at', desc=True).execute()
        articles = result.data or []
        
        print(f"\n📋 Remaining articles ({len(articles)} total):")
        print("-" * 50)
        
        for i, article in enumerate(articles, 1):
            print(f"{i}. ID: {article['id']}")
            print(f"   Headline: {article['headline']}")
            print(f"   Category: {article['category']}")
            print(f"   Source: {article['source']}")
            print(f"   Created: {article['created_at']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error showing articles: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting TeenBuzz Duplicate Article Removal...")
    
    # Remove duplicates
    success = find_and_remove_duplicates()
    
    if success:
        # Show remaining articles
        show_remaining_articles()
    else:
        print("❌ Duplicate removal failed.") 