#!/usr/bin/env python3
"""
Script to validate and fix article URLs
"""

import os
import requests
from dotenv import load_dotenv
from supabase.client import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

def validate_url(url):
    """Check if a URL is valid and accessible"""
    if not url or url.strip() == '':
        return False, "Empty URL"
    
    # Ensure URL has protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            return True, "Valid"
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Error: {str(e)}"

def fix_article_urls():
    """Validate and fix article URLs"""
    
    print("🔍 Validating article URLs...")
    
    try:
        # Get all articles with URLs
        result = supabase.table('articles').select('id, headline, original_url, source').execute()
        
        if not result.data:
            print("No articles found")
            return
        
        print(f"📰 Found {len(result.data)} articles to validate")
        
        valid_count = 0
        invalid_count = 0
        fixed_count = 0
        
        for article in result.data:
            article_id = article['id']
            headline = article['headline']
            original_url = article.get('original_url', '')
            source = article.get('source', 'Unknown')
            
            print(f"\n🔍 Article {article_id}: {headline[:50]}...")
            print(f"   Source: {source}")
            print(f"   URL: {original_url}")
            
            if not original_url or original_url.strip() == '':
                print("   ❌ No URL provided")
                invalid_count += 1
                continue
            
            # Fix URL if needed
            fixed_url = original_url
            if not original_url.startswith(('http://', 'https://')):
                fixed_url = 'https://' + original_url
                print(f"   🔧 Fixed URL: {fixed_url}")
                fixed_count += 1
            
            # Validate URL
            is_valid, status = validate_url(fixed_url)
            
            if is_valid:
                print("   ✅ URL is valid")
                valid_count += 1
                
                # Update database if URL was fixed
                if fixed_url != original_url:
                    try:
                        supabase.table('articles').update({
                            'original_url': fixed_url
                        }).eq('id', article_id).execute()
                        print("   💾 Updated database with fixed URL")
                    except Exception as e:
                        print(f"   ❌ Failed to update database: {e}")
            else:
                print(f"   ❌ URL is invalid: {status}")
                invalid_count += 1
        
        print(f"\n📊 Validation Summary:")
        print(f"   ✅ Valid URLs: {valid_count}")
        print(f"   ❌ Invalid URLs: {invalid_count}")
        print(f"   🔧 Fixed URLs: {fixed_count}")
        
        if invalid_count > 0:
            print(f"\n💡 Recommendations:")
            print(f"   - {invalid_count} articles have invalid URLs")
            print(f"   - Consider updating these with valid source URLs")
            print(f"   - Or remove the 'Read Original' button for these articles")
        
    except Exception as e:
        print(f"❌ Error validating URLs: {e}")

def show_url_statistics():
    """Show statistics about article URLs"""
    
    print("\n📋 Article URL Statistics:")
    print("=" * 40)
    
    try:
        result = supabase.table('articles').select('original_url, source').execute()
        
        total_articles = len(result.data)
        articles_with_urls = 0
        articles_without_urls = 0
        
        for article in result.data:
            if article.get('original_url') and article['original_url'].strip():
                articles_with_urls += 1
            else:
                articles_without_urls += 1
        
        print(f"📰 Total articles: {total_articles}")
        print(f"🔗 Articles with URLs: {articles_with_urls}")
        print(f"❌ Articles without URLs: {articles_without_urls}")
        print(f"📊 URL coverage: {(articles_with_urls/total_articles*100):.1f}%")
        
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")

if __name__ == "__main__":
    print("🚀 TeenBuzz URL Validator")
    print("=" * 50)
    
    show_url_statistics()
    fix_article_urls()
    
    print("\n✅ URL validation completed!")
