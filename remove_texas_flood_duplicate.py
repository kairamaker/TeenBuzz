#!/usr/bin/env python3
"""
Remove the duplicate Texas flood article
Keep the more recent one (ID: 15) and remove the older one (ID: 14)
"""

import os
from dotenv import load_dotenv
from supabase.client import create_client

# Load environment variables
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def remove_duplicate_texas_flood():
    """Remove the duplicate Texas flood article"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Remove the older Texas flood article (ID: 14)
        article_id_to_remove = 14
        
        print(f"🗑️  Removing duplicate Texas flood article (ID: {article_id_to_remove})...")
        
        result = supabase.table('articles').delete().eq('id', article_id_to_remove).execute()
        
        if result.data:
            print(f"✅ Successfully removed article ID: {article_id_to_remove}")
        else:
            print(f"⚠️  No article found with ID: {article_id_to_remove}")
        
        # Show remaining articles
        remaining_result = supabase.table('articles').select('*').order('created_at', desc=True).execute()
        remaining_articles = remaining_result.data or []
        
        print(f"\n📋 Remaining articles ({len(remaining_articles)} total):")
        print("-" * 50)
        
        for i, article in enumerate(remaining_articles, 1):
            print(f"{i}. ID: {article['id']}")
            print(f"   Headline: {article['headline']}")
            print(f"   Category: {article['category']}")
            print(f"   Source: {article['source']}")
            print(f"   Created: {article['created_at']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error in remove_duplicate_texas_flood: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting TeenBuzz Duplicate Texas Flood Article Removal...")
    remove_duplicate_texas_flood() 