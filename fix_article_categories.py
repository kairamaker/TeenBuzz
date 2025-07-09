#!/usr/bin/env python3
"""
Fix article categories to be more relevant to their content
"""

import os
from dotenv import load_dotenv
from supabase.client import create_client

# Load environment variables
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Category mapping based on article content
CATEGORY_FIXES = {
    # Article ID: Correct Category
    17: "Social Issues",  # Philly Strike - already correct
    16: "Social Issues",  # Viral challenges - should be social issues, not education
    15: "Environment",    # Texas floods - should be environment, not social issues
    14: "Environment",    # Texas floods - should be environment, not music
    13: "Health",         # Mental health hotline - should be health, not music
    12: "Education",      # Teens changing world - should be education, not social issues
    11: "Health",         # Sleep study - should be health, not science
    10: "Technology",     # Apple Intelligence - already correct
    9: "Health",          # Social media brain development - should be health, not science
}

def fix_article_categories():
    """Fix article categories to be more relevant"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        print("🔧 Fixing article categories...")
        
        for article_id, correct_category in CATEGORY_FIXES.items():
            try:
                # Update the article category
                result = supabase.table('articles').update({
                    'category': correct_category
                }).eq('id', article_id).execute()
                
                if result.data:
                    print(f"✅ Fixed Article {article_id}: {correct_category}")
                else:
                    print(f"⚠️  No changes for Article {article_id}")
                    
            except Exception as e:
                print(f"❌ Error fixing Article {article_id}: {str(e)}")
        
        print("🎉 Category fixes completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in fix_article_categories: {str(e)}")
        return False

def show_updated_articles():
    """Show all articles with their updated categories"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Get all articles
        result = supabase.table('articles').select('*').order('created_at', desc=True).execute()
        articles = result.data or []
        
        print(f"📊 Found {len(articles)} articles in database:")
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
    print("🚀 Starting TeenBuzz Article Category Fix...")
    
    # Fix the categories
    success = fix_article_categories()
    
    if success:
        print("\n📋 Updated articles:")
        show_updated_articles()
    else:
        print("❌ Category fix failed.") 