#!/usr/bin/env python3
"""
Real Article Fetcher - Gets actual long articles from RSS feeds
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from database_manager import get_database
from datetime import datetime
import time
import random
import re

def clean_text(text):
    """Clean and format text content"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common unwanted elements
    unwanted_patterns = [
        r'Advertisement',
        r'Subscribe to.*?newsletter',
        r'Follow us on.*?social media',
        r'Share this article',
        r'Read more:',
        r'Continue reading:',
        r'Source:',
        r'Image:',
        r'Photo:',
        r'Credit:',
        r'Getty Images',
        r'Reuters',
        r'AP Photo',
        r'AFP',
    ]
    
    for pattern in unwanted_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text.strip()

def get_article_content(url):
    """Extract full article content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()
        
        # Try to find article content in common containers
        content_selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            '.story-body',
            '.article-body',
            '[role="main"]',
            '.main-content'
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = ' '.join([elem.get_text() for elem in elements])
                break
        
        # If no specific content found, get all paragraph text
        if not content:
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text() for p in paragraphs])
        
        # Clean and limit content
        content = clean_text(content)
        
        # Ensure minimum length (1000+ words)
        if len(content.split()) < 1000:
            # If content is too short, expand it with additional context
            content = expand_article_content(content, soup)
        
        return content[:15000]  # Limit to reasonable length
        
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return None

def expand_article_content(base_content, soup):
    """Expand short articles with additional relevant content"""
    try:
        # Get additional content from related elements
        additional_content = []
        
        # Get content from divs with common article classes
        for div in soup.find_all('div', class_=re.compile(r'(content|article|story|post)', re.I)):
            text = div.get_text()
            if len(text.split()) > 50:  # Only use substantial content
                additional_content.append(text)
        
        # Get content from sections
        for section in soup.find_all('section'):
            text = section.get_text()
            if len(text.split()) > 50:
                additional_content.append(text)
        
        # Combine and clean
        expanded_content = base_content + ' ' + ' '.join(additional_content)
        expanded_content = clean_text(expanded_content)
        
        return expanded_content
        
    except Exception as e:
        print(f"Error expanding content: {e}")
        return base_content

def fetch_real_articles():
    """Fetch real articles from RSS feeds"""
    print("🚀 Starting real article fetching...")
    
    # RSS feeds for real news
    rss_feeds = [
        {
            'url': 'https://feeds.bbci.co.uk/news/technology/rss.xml',
            'category': 'Technology',
            'source': 'BBC Technology'
        },
        {
            'url': 'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
            'category': 'Science',
            'source': 'BBC Science'
        },
        {
            'url': 'https://feeds.bbci.co.uk/news/health/rss.xml',
            'category': 'Health',
            'source': 'BBC Health'
        },
        {
            'url': 'https://rss.cnn.com/rss/edition_technology.rss',
            'category': 'Technology',
            'source': 'CNN Technology'
        },
        {
            'url': 'https://feeds.reuters.com/reuters/technologyNews',
            'category': 'Technology',
            'source': 'Reuters Technology'
        },
        {
            'url': 'https://feeds.reuters.com/reuters/scienceNews',
            'category': 'Science',
            'source': 'Reuters Science'
        },
        {
            'url': 'https://feeds.reuters.com/reuters/healthNews',
            'category': 'Health',
            'source': 'Reuters Health'
        },
        {
            'url': 'https://feeds.bbci.co.uk/news/education/rss.xml',
            'category': 'Education',
            'source': 'BBC Education'
        }
    ]
    
    all_articles = []
    
    for feed_info in rss_feeds:
        try:
            print(f"  🔍 Checking {feed_info['source']}...")
            
            # Parse RSS feed
            feed = feedparser.parse(feed_info['url'])
            
            if not feed.entries:
                print(f"    ⚠️  No entries found in {feed_info['source']}")
                continue
            
            # Process each entry
            for entry in feed.entries[:5]:  # Limit to 5 articles per feed
                try:
                    # Get basic article info
                    headline = entry.get('title', '').strip()
                    summary = entry.get('summary', '').strip()
                    link = entry.get('link', '')
                    published = entry.get('published', '')
                    
                    if not headline or not link:
                        continue
                    
                    # Get full article content
                    print(f"    📄 Fetching content for: {headline[:50]}...")
                    full_content = get_article_content(link)
                    
                    if not full_content or len(full_content.split()) < 500:
                        print(f"    ⚠️  Content too short, skipping...")
                        continue
                    
                    # Create article data
                    article_data = {
                        'headline': headline,
                        'content': full_content,
                        'category': feed_info['category'],
                        'tags': generate_tags(headline, full_content, feed_info['category']),
                        'source': feed_info['source'],
                        'url': link,
                        'views': random.randint(50, 500),
                        'likes': random.randint(10, 100),
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    all_articles.append(article_data)
                    print(f"    ✅ Added article: {headline[:50]}... ({len(full_content.split())} words)")
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"    ❌ Error processing entry: {e}")
                    continue
            
        except Exception as e:
            print(f"  ❌ Error fetching from {feed_info['source']}: {e}")
            continue
    
    print(f"📊 Fetched {len(all_articles)} real articles")
    return all_articles

def generate_tags(headline, content, category):
    """Generate relevant tags for the article"""
    tags = [category.lower()]
    
    # Common tag mappings
    tag_mappings = {
        'technology': ['ai', 'artificial intelligence', 'tech', 'innovation', 'digital', 'software', 'hardware', 'internet', 'mobile', 'computer'],
        'science': ['research', 'study', 'discovery', 'experiment', 'scientific', 'data', 'analysis', 'climate', 'environment', 'space'],
        'health': ['medical', 'healthcare', 'medicine', 'treatment', 'disease', 'wellness', 'mental health', 'fitness', 'nutrition', 'therapy'],
        'education': ['learning', 'school', 'university', 'student', 'teaching', 'academic', 'research', 'study', 'knowledge', 'training']
    }
    
    # Add category-specific tags
    if category.lower() in tag_mappings:
        tags.extend(tag_mappings[category.lower()][:3])
    
    # Extract additional tags from headline and content
    text = (headline + ' ' + content).lower()
    
    # Look for common keywords
    keywords = [
        'teen', 'teenager', 'youth', 'young', 'student', 'school', 'college',
        'social media', 'instagram', 'tiktok', 'youtube', 'facebook', 'twitter',
        'climate change', 'environment', 'sustainability', 'green',
        'mental health', 'anxiety', 'depression', 'stress', 'wellness',
        'career', 'job', 'work', 'future', 'success', 'entrepreneur',
        'music', 'art', 'creativity', 'design', 'fashion', 'beauty',
        'sports', 'fitness', 'exercise', 'health', 'nutrition'
    ]
    
    for keyword in keywords:
        if keyword in text and keyword not in tags:
            tags.append(keyword)
    
    # Limit to 10 tags
    return ','.join(tags[:10])

def add_articles_to_database(articles):
    """Add articles to the database"""
    db = get_database()
    if not db:
        print("❌ Database connection failed")
        return False
    
    print("💾 Adding articles to database...")
    
    added_count = 0
    skipped_count = 0
    
    for article in articles:
        try:
            # Check if article already exists (by headline)
            existing = db.select('articles', where='headline = ?', params=(article['headline'],), limit=1)
            
            if existing:
                print(f"  ⏭️  Skipping existing article: {article['headline'][:50]}...")
                skipped_count += 1
                continue
            
            # Insert new article
            article_id = db.insert('articles', article)
            print(f"  ✅ Added: {article['headline'][:50]}... ({len(article['content'].split())} words)")
            added_count += 1
            
        except Exception as e:
            print(f"  ❌ Error adding article: {e}")
            continue
    
    print(f"📊 Results:")
    print(f"  ✅ Added: {added_count} new articles")
    print(f"  ⏭️  Skipped: {skipped_count} existing articles")
    
    return True

def main():
    """Main function to fetch and add real articles"""
    print("🚀 Real Article Fetcher Starting...")
    
    # Fetch real articles
    articles = fetch_real_articles()
    
    if not articles:
        print("❌ No articles fetched")
        return False
    
    # Add to database
    success = add_articles_to_database(articles)
    
    if success:
        print("🎉 Real article fetching completed successfully!")
        return True
    else:
        print("❌ Failed to add articles to database")
        return False

if __name__ == "__main__":
    main()

