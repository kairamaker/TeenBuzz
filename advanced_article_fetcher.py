#!/usr/bin/env python3
"""
Advanced Article Fetcher for TeenBuzz
Fetches real articles from multiple news sources and APIs
"""

import requests
import json
import random
import time
from datetime import datetime, timedelta
from database_manager import get_database

# Free news APIs (no key required)
FREE_NEWS_SOURCES = {
    "NewsAPI": {
        "url": "https://newsapi.org/v2/everything",
        "requires_key": True,
        "key": None  # You can add your free API key here
    },
    "NewsData": {
        "url": "https://newsdata.io/api/1/news",
        "requires_key": True,
        "key": None  # You can add your free API key here
    },
    "Guardian": {
        "url": "https://content.guardianapis.com/search",
        "requires_key": True,
        "key": None  # You can add your free API key here
    }
}

# RSS feeds (no API key required)
RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "https://feeds.bbci.co.uk/news/health/rss.xml",
    "https://rss.cnn.com/rss/edition.rss",
    "https://feeds.reuters.com/reuters/technologyNews",
    "https://feeds.reuters.com/reuters/scienceNews"
]

# Teen-focused topics
TEEN_TOPICS = [
    "technology", "AI", "artificial intelligence", "smartphone", "social media",
    "climate change", "environment", "sustainability", "renewable energy",
    "mental health", "wellness", "fitness", "nutrition", "sleep",
    "education", "school", "college", "university", "learning", "study",
    "gaming", "video games", "esports", "streaming", "youtube", "tiktok",
    "music", "concerts", "artists", "albums", "streaming",
    "sports", "football", "basketball", "soccer", "olympics",
    "space", "NASA", "space exploration", "astronomy", "science",
    "social issues", "equality", "diversity", "activism", "youth"
]

def fetch_from_rss_feed(feed_url):
    """Fetch articles from RSS feed"""
    try:
        import feedparser
        
        feed = feedparser.parse(feed_url)
        articles = []
        
        for entry in feed.entries[:5]:  # Limit to 5 articles per feed
            article = {
                "title": entry.get("title", ""),
                "description": entry.get("summary", ""),
                "url": entry.get("link", ""),
                "published": entry.get("published", ""),
                "source": "RSS Feed"
            }
            articles.append(article)
        
        return articles
        
    except ImportError:
        print("❌ feedparser not installed. Install with: pip install feedparser")
        return []
    except Exception as e:
        print(f"❌ Error fetching RSS feed {feed_url}: {e}")
        return []

def fetch_from_newsapi():
    """Fetch articles from NewsAPI (requires free API key)"""
    # This is a placeholder - you would need to get a free API key from newsapi.org
    # For now, we'll return mock data
    return []

def fetch_from_guardian():
    """Fetch articles from Guardian API (requires free API key)"""
    # This is a placeholder - you would need to get a free API key from the Guardian
    # For now, we'll return mock data
    return []

def create_enhanced_article(title, description, url, source, category=None):
    """Create a full article with enhanced content
    
    Args:
        title: Article headline
        description: Article description/summary
        url: REQUIRED - Original article URL (must not be None or empty)
        source: Article source/publication
        category: Article category (auto-detected if not provided)
    
    Returns:
        dict: Enhanced article with all required fields including URL
    """
    
    # Validate required URL
    if not url or url.strip() == '':
        raise ValueError("URL is required for all articles - cannot be None or empty")
    
    # Generate enhanced content based on the title and description
    enhanced_content = f"{description}\n\n"
    
    # Add more detailed content based on the topic
    if any(keyword in title.lower() for keyword in ["ai", "artificial intelligence", "technology"]):
        enhanced_content += """
Artificial intelligence continues to revolutionize various industries, from healthcare to education. Recent developments in machine learning and neural networks are making AI more accessible and practical for everyday applications.

Experts predict that AI will play an increasingly important role in how we work, learn, and interact with technology. For students and young people, understanding AI and its implications is becoming essential for future career success.

The rapid pace of AI development brings both opportunities and challenges. While AI can help solve complex problems and improve efficiency, it also raises important questions about privacy, job displacement, and ethical considerations.
"""
        category = "Technology"
        
    elif any(keyword in title.lower() for keyword in ["climate", "environment", "sustainability"]):
        enhanced_content += """
Environmental issues are becoming increasingly urgent as climate change impacts become more visible around the world. Young people are taking a leading role in advocating for environmental protection and sustainable practices.

From reducing carbon footprints to supporting renewable energy initiatives, there are many ways individuals can contribute to environmental conservation. Education and awareness are key to building a more sustainable future.

The next generation will inherit the consequences of today's environmental decisions, making it crucial for young people to be informed and engaged in environmental issues.
"""
        category = "Environment"
        
    elif any(keyword in title.lower() for keyword in ["health", "mental health", "wellness"]):
        enhanced_content += """
Mental health awareness has become increasingly important, especially among young people who face unique challenges in today's digital world. Understanding mental health and knowing how to seek help are essential life skills.

Regular exercise, proper nutrition, adequate sleep, and maintaining social connections are all important factors in maintaining good mental health. It's also important to recognize when professional help might be needed.

Creating supportive environments where young people feel comfortable discussing mental health issues is crucial for building resilience and promoting well-being.
"""
        category = "Health"
        
    elif any(keyword in title.lower() for keyword in ["education", "school", "learning", "study"]):
        enhanced_content += """
Education is evolving rapidly with new technologies and teaching methods. Students today have access to more resources and learning opportunities than ever before, but they also face new challenges in the digital age.

Effective study techniques, time management, and digital literacy are becoming increasingly important skills for academic success. Learning how to learn is just as important as learning specific subjects.

The future of education will likely involve more personalized learning experiences, greater use of technology, and a focus on developing critical thinking and problem-solving skills.
"""
        category = "Education"
        
    elif any(keyword in title.lower() for keyword in ["space", "nasa", "science", "research"]):
        enhanced_content += """
Space exploration continues to capture the imagination of people around the world, especially young people who dream of becoming astronauts or working in the space industry. Recent missions to Mars and beyond are opening up new possibilities for human space exploration.

Scientific research and discovery are fundamental to human progress. From understanding the origins of the universe to developing new technologies, science plays a crucial role in shaping our future.

For students interested in science, there are many exciting career opportunities in fields like astronomy, physics, engineering, and space technology.
"""
        category = "Science"
        
    else:
        enhanced_content += """
This story highlights important developments that affect young people and society as a whole. Staying informed about current events and understanding their implications is an important part of being an engaged citizen.

Critical thinking and media literacy are essential skills for navigating today's information-rich world. It's important to seek information from reliable sources and consider multiple perspectives on important issues.
"""
        category = category or "General"
    
    # Generate keywords based on content
    keywords = []
    for topic in TEEN_TOPICS:
        if topic.lower() in title.lower() or topic.lower() in enhanced_content.lower():
            keywords.append(topic)
    
    # Add some general keywords
    keywords.extend(["news", "current events", "youth", "teenagers", "students"])
    
    return {
        "headline": title,
        "content": enhanced_content,
        "category": category,
        "tags": ", ".join(keywords[:10]),  # Limit to 10 keywords
        "source": source,
        "url": url,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

def fetch_real_articles():
    """Fetch real articles from multiple sources"""
    all_articles = []
    
    print("📰 Fetching articles from RSS feeds...")
    
    # Fetch from RSS feeds
    for feed_url in RSS_FEEDS:
        print(f"  🔍 Checking {feed_url}")
        articles = fetch_from_rss_feed(feed_url)
        all_articles.extend(articles)
        time.sleep(1)  # Be respectful to the servers
    
    print(f"📊 Fetched {len(all_articles)} articles from RSS feeds")
    
    # Convert RSS articles to enhanced articles
    enhanced_articles = []
    for article in all_articles:
        if article["title"] and article["description"]:
            enhanced = create_enhanced_article(
                article["title"],
                article["description"],
                article["url"],
                article["source"]
            )
            enhanced_articles.append(enhanced)
    
    return enhanced_articles

def add_articles_to_database(articles):
    """Add articles to the database"""
    db = get_database()
    if not db:
        print("❌ Database connection failed")
        return False
    
    added_count = 0
    skipped_count = 0
    
    for article in articles:
        try:
            # Validate that article has required URL
            if not article.get('url') or article.get('url').strip() == '':
                print(f"❌ Skipping article without URL: {article['headline'][:50]}...")
                continue
            
            # Check if article already exists
            existing = db.select('articles', where='headline = ?', params=(article['headline'],), limit=1)
            if existing:
                skipped_count += 1
                continue
            
            # Insert article
            article_id = db.insert('articles', article)
            print(f"✅ Added: {article['headline'][:60]}...")
            added_count += 1
            
        except Exception as e:
            print(f"❌ Error adding article: {e}")
    
    print(f"\n📊 Results:")
    print(f"  ✅ Added: {added_count} new articles")
    print(f"  ⏭️  Skipped: {skipped_count} existing articles")
    
    return True

def main():
    """Main function"""
    print("🚀 Starting advanced article fetching...")
    
    # Fetch articles
    articles = fetch_real_articles()
    
    if not articles:
        print("❌ No articles fetched")
        return
    
    # Add to database
    print(f"\n💾 Adding {len(articles)} articles to database...")
    success = add_articles_to_database(articles)
    
    if success:
        print("✅ Article fetching completed successfully!")
    else:
        print("❌ Article fetching failed")

if __name__ == "__main__":
    main()

