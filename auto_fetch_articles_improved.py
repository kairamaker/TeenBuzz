#!/usr/bin/env python3
"""
Improved automatic daily article fetching script for TeenBuzz
Fetches 5 current news articles daily from reliable sources
"""

import os
import sys
import requests
import json
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase.client import create_client

# Load environment variables
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')

# News categories for teens
NEWS_CATEGORIES = [
    'Technology',
    'Entertainment', 
    'Sports',
    'Health',
    'Environment',
    'Education',
    'Social Issues',
    'Science',
    'Gaming',
    'Music'
]

# CURATED RELIABLE NEWS SOURCES (5-7 sources only)
RELIABLE_NEWS_SOURCES = [
    'BBC News',
    'CNN',
    'The Guardian',
    'NPR News',
    'Reuters',
    'Associated Press',
    'Yahoo News'
]

def fetch_current_news_from_perplexity(topic, category):
    """Fetch and rewrite CURRENT news using Perplexity API"""
    if not PERPLEXITY_API_KEY or PERPLEXITY_API_KEY.startswith('your_'):
        raise Exception('Perplexity API key not configured.')
    
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    source = random.choice(RELIABLE_NEWS_SOURCES)
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    system_content = f"""
    You are a professional news editor specializing in making CURRENT news accessible and engaging for teenagers (ages 13-18). Your job is to find and rewrite RECENT news articles following these strict guidelines:
    
    CRITICAL REQUIREMENTS:
    ✅ ONLY find news from {yesterday} or {today} (last 24-48 hours)
    ✅ Use ONLY these reliable sources: {', '.join(RELIABLE_NEWS_SOURCES)}
    ✅ Verify the article is CURRENT and RECENT
    ✅ Include the EXACT publish date from the original article
    
    CONTENT GUARDRAILS:
    ✅ Maintain factual accuracy - No speculation or exaggeration
    ✅ Explain WHY this matters to teens specifically 
    ✅ Provide context and background information
    ✅ Connect to their world (school, social media, future careers)
    ✅ Keep content appropriate for ages 13-18
    ✅ No graphic violence, explicit content, or inappropriate material
    ✅ Avoid political bias - present facts neutrally
    
    LANGUAGE REQUIREMENTS:
    ✅ Use conversational, engaging tone
    ✅ Explain technical terms in simple language
    ✅ Use active voice and shorter sentences (max 20 words)
    ✅ Include relevant pop culture references when appropriate
    ✅ Use "you" to directly address readers
    ✅ Keep paragraphs short (5-7 sentences max)
    
    STRUCTURE REQUIREMENTS:
    📰 HEADLINE: Under 80 characters, catchy but not clickbait
    📝 CONTENT: Exactly 5-10 paragraphs, 500 words total
    🎯 HOOK: Start with the most surprising or relevant takeaway for teens
    
    TASK: Find a RECENT news story about {topic} from {source} or other reliable sources from {yesterday} or {today} and rewrite it for teenagers.
    
    Format your response as JSON with these exact fields:
    {{
        "headline": "Your catchy headline under 80 characters",
        "content": "Your 5-10 paragraph article, exactly 500 words",
        "source": "Original source name (e.g., BBC News, CNN)",
        "original_url": "URL of the original article you found",
        "original_title": "EXACT original article headline from the source",
        "original_author": "Author name from the original article (if available)",
        "publish_date": "EXACT publish date from original article (YYYY-MM-DD format)",
        "relevance": "Why this matters to teens specifically",
        "category": "{category}"
    }}
    """
    
    user_content = f"Find and rewrite a RECENT news article about {topic} from {yesterday} or {today} for teenagers. Only use reliable sources and ensure the article is current."
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and result["choices"] and "message" in result["choices"][0]:
                content = result["choices"][0]["message"]["content"]
                try:
                    article_data = json.loads(content)
                    
                    # Validate that we have a recent article
                    publish_date = article_data.get('publish_date', '')
                    if publish_date:
                        try:
                            pub_date = datetime.strptime(publish_date, '%Y-%m-%d').date()
                            today_date = datetime.now().date()
                            if (today_date - pub_date).days > 2:
                                raise Exception(f'Article too old: {publish_date}')
                        except ValueError:
                            pass  # Continue if date parsing fails
                    
                    return {
                        'headline': article_data.get('headline', f'Latest {category} News'),
                        'content': article_data.get('content', content),
                        'source': article_data.get('source', source),
                        'original_url': article_data.get('original_url', ''),
                        'original_title': article_data.get('original_title', ''),
                        'original_author': article_data.get('original_author', ''),
                        'publish_date': article_data.get('publish_date', ''),
                        'category': category,
                        'relevance': article_data.get('relevance', 'Relevant to teens')
                    }
                except json.JSONDecodeError:
                    return {
                        'headline': f'Latest {category} News',
                        'content': content,
                        'source': source,
                        'original_url': '',
                        'original_title': '',
                        'original_author': '',
                        'publish_date': today,
                        'category': category,
                        'relevance': 'Current news for teens'
                    }
            else:
                raise Exception(f'Perplexity API returned unexpected structure: {result}')
        elif response.status_code == 401:
            raise Exception('401 Unauthorized: Your API key is invalid or does not have access.')
        else:
            raise Exception(f'Perplexity API error: {response.status_code} - {response.text}')
    except Exception as e:
        raise Exception(f'Failed to fetch news: {str(e)}')

def get_current_topics():
    """Get current trending topics for today"""
    topics = [
        "breaking news today",
        "trending news today", 
        "top stories today",
        "viral news today",
        "important news today",
        "latest developments today",
        "current events today"
    ]
    return topics

def auto_fetch_current_articles():
    """Automatically fetch 5 CURRENT daily articles"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Check if we already fetched articles today
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time()).isoformat()
        today_end = datetime.combine(today, datetime.max.time()).isoformat()
        
        existing_articles = supabase.table('articles').select('id').gte('created_at', today_start).lte('created_at', today_end).execute()
        
        if existing_articles.data and len(existing_articles.data) >= 5:
            print(f"✅ Already fetched {len(existing_articles.data)} articles today. Skipping.")
            return True
        
        print("📰 Starting CURRENT daily article fetch...")
        print(f"🎯 Using sources: {', '.join(RELIABLE_NEWS_SOURCES)}")
        
        # Get current topics
        topics = get_current_topics()
        categories = NEWS_CATEGORIES.copy()
        
        articles_fetched = 0
        max_attempts = 15  # Increased attempts for current news
        used_categories = set()
        
        for attempt in range(max_attempts):
            if articles_fetched >= 5:
                break
                
            topic = random.choice(topics)
            
            # Try to use different categories
            available_categories = [cat for cat in categories if cat not in used_categories]
            if not available_categories:
                available_categories = categories
                used_categories.clear()
            
            category = random.choice(available_categories)
            used_categories.add(category)
            
            try:
                print(f"🔄 Fetching article {articles_fetched + 1}/5: {category} - {topic}")
                
                article_data = fetch_current_news_from_perplexity(topic, category)
                
                # Store article in database
                article_record = {
                    'headline': article_data['headline'],
                    'content': article_data['content'],
                    'category': article_data['category'],
                    'source': article_data['source'],
                    'original_url': article_data['original_url'],
                    'original_title': article_data['original_title'],
                    'original_author': article_data['original_author'],
                    'publish_date': article_data['publish_date'],
                    'created_at': datetime.now().isoformat()
                }
                
                result = supabase.table('articles').insert(article_record).execute()
                
                if result.data:
                    print(f"✅ Article {articles_fetched + 1} saved: {article_data['headline'][:50]}...")
                    print(f"   Source: {article_data['source']}")
                    print(f"   Publish Date: {article_data['publish_date']}")
                    articles_fetched += 1
                else:
                    print(f"❌ Failed to save article {articles_fetched + 1}")
                    
            except Exception as e:
                print(f"❌ Error fetching article {articles_fetched + 1}: {str(e)}")
                continue
        
        print(f"🎉 Successfully fetched {articles_fetched} current articles!")
        return True
        
    except Exception as e:
        print(f"❌ Auto-fetch error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 TeenBuzz Current Article Fetcher")
    print("=" * 50)
    success = auto_fetch_current_articles()
    if success:
        print("✅ Daily article fetch completed successfully!")
    else:
        print("❌ Daily article fetch failed!")
        sys.exit(1)
