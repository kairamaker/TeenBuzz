#!/usr/bin/env python3
"""
Automatic daily article fetching script for TeenBuzz
Fetches 5 trending news articles daily and stores them in the database
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

# News sources for Perplexity to search
NEWS_SOURCES = [
    'The Guardian',
    'New York Times', 
    'BBC News',
    'CNN',
    'Yahoo News',
    'Teen Vogue',
    'BuzzFeed',
    'NPR News'
]

def fetch_news_from_perplexity(topic, category):
    """Fetch and rewrite news using Perplexity API"""
    if not PERPLEXITY_API_KEY or PERPLEXITY_API_KEY.startswith('your_'):
        raise Exception('Perplexity API key not configured.')
    
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    source = random.choice(NEWS_SOURCES)
    system_content = f"""
    You are a professional news editor specializing in making news accessible and engaging for teenagers (ages 13-18). Your job is to rewrite news articles following these strict guidelines:
    CONTENT GUARDRAILS (NON-NEGOTIABLES):
    ✅ Maintain factual accuracy - No speculation or exaggeration. Stick to facts from the original article.
    ✅ Explain WHY this matters to teens specifically 
    ✅ Provide context and background information
    ✅ Connect to their world (school, social media, future careers, social issues they care about)
    ✅ Keep content appropriate for ages 13-18
    ✅ No graphic violence, explicit content, or inappropriate material
    ✅ Avoid political bias - present facts neutrally
    ✅ Include diverse perspectives when relevant
    LANGUAGE REQUIREMENTS:
    ✅ Use conversational, engaging tone, Friendly and upbeat: like you're talking to a smart friend.
    ✅ Explain technical terms in simple language. Break down technical terms into easy explanations.
    ✅ Use active voice and shorter sentences (max 20 words)
    ✅ Include relevant pop culture or social media references when appropriate
    ✅ Use "you" to directly address readers
    ✅ Keep paragraphs short (5-7 sentences max)
    STRUCTURE REQUIREMENTS:
    📰 HEADLINE: Under 80 characters, catchy but not clickbait, clear and informative
    📝 CONTENT: Exactly 5-10 paragraphs, 500 words total
    🎯 HOOK: Start with the most surprising or relevant takeaway for teens
    HEADLINE EXAMPLES:
    ❌ "Government Officials Discuss Economic Policy Changes"
    ✅ "New Laws Could Affect Your First Job and College Costs"
    ❌ "Tech Company Announces Quarterly Results"
    ✅ "TikTok's Parent Company Just Made Billions - Here's How"
    ❌ "Federal Reserve Adjusts Interest Rates"
    ✅ "Why the Fed's Decision Could Impact Your Dream Job or Student Loans"
    ❌ "Climate Report Released by UN"
    ✅ "The Planet's in Trouble – What Teens Need to Know From the New UN Report"
    TASK: Find a recent news story about {topic} from {source} or other reputable sources and rewrite it for teenagers following the guidelines above.
    Format your response as JSON with these exact fields:
    {{
        "headline": "Your catchy headline under 80 characters",
        "content": "Your 5-10 paragraph article, exactly 500 words",
        "source": "Original source name (e.g., The Guardian, BBC News)",
        "original_url": "URL of the original article you found",
        "relevance": "Why this matters to teens specifically",
        "category": "{category}"
    }}
    """
    user_content = f"Find and rewrite a recent news article about {topic} for teenagers."
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
                    return {
                        'headline': article_data.get('headline', f'Latest {category} News'),
                        'content': article_data.get('content', content),
                        'source': article_data.get('source', source),
                        'original_url': article_data.get('original_url', ''),
                        'category': category,
                        'relevance': article_data.get('relevance', 'Relevant to teens')
                    }
                except json.JSONDecodeError:
                    return {
                        'headline': f'Latest {category} News',
                        'content': content,
                        'source': source,
                        'original_url': '',
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

def get_daily_topics():
    """Get 5 trending topics for today"""
    topics = [
        "trending news today",
        "breaking news today", 
        "top stories today",
        "viral news today",
        "important news today"
    ]
    return topics

def auto_fetch_daily_articles():
    """Automatically fetch 5 daily articles"""
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
        
        print("📰 Starting daily article fetch...")
        
        # Get daily topics
        topics = get_daily_topics()
        categories = NEWS_CATEGORIES.copy()
        
        articles_fetched = 0
        max_attempts = 10  # Prevent infinite loops
        
        for attempt in range(max_attempts):
            if articles_fetched >= 5:
                break
                
            topic = random.choice(topics)
            category = random.choice(categories)
            
            try:
                print(f"🔄 Fetching article {articles_fetched + 1}/5: {category} - {topic}")
                
                # Fetch article from Perplexity
                article_data = fetch_news_from_perplexity(topic, category)
                
                # Store in Supabase
                result = supabase.table('articles').insert({
                    'headline': article_data['headline'],
                    'content': article_data['content'],
                    'source': article_data['source'],
                    'original_url': article_data.get('original_url', ''),
                    'category': article_data['category'],
                    'relevance': article_data['relevance'],
                    'created_at': datetime.now().isoformat()
                }).execute()
                
                if result.data:
                    articles_fetched += 1
                    print(f"✅ Successfully stored: {article_data['headline']}")
                else:
                    print(f"⚠️ Failed to store article")
                    
            except Exception as e:
                print(f"❌ Error fetching article: {str(e)}")
                continue
        
        print(f"🎉 Daily fetch complete! Successfully fetched {articles_fetched} articles.")
        return True
        
    except Exception as e:
        print(f"❌ Error in auto_fetch_daily_articles: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting TeenBuzz Daily Article Fetch...")
    success = auto_fetch_daily_articles()
    if success:
        print("✅ Daily fetch completed successfully!")
    else:
        print("❌ Daily fetch failed.")
        sys.exit(1) 