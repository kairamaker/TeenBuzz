from flask import Flask, request, render_template, redirect, url_for, flash
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import json
import random

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')

# Initialize Supabase client only if credentials are provided
supabase = None
if SUPABASE_URL and SUPABASE_KEY and not SUPABASE_URL.startswith('your_'):
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Warning: Could not initialize Supabase client: {e}")
        supabase = None

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

def get_category_icon(category):
    """Get icon class for category"""
    icons = {
        'Technology': 'fas fa-laptop-code',
        'Entertainment': 'fas fa-film',
        'Sports': 'fas fa-basketball-ball',
        'Health': 'fas fa-heartbeat',
        'Environment': 'fas fa-leaf',
        'Education': 'fas fa-graduation-cap',
        'Social Issues': 'fas fa-users',
        'Science': 'fas fa-flask',
        'Gaming': 'fas fa-gamepad',
        'Music': 'fas fa-music'
    }
    return icons.get(category, 'fas fa-newspaper')

@app.route('/')
def home():
    """Home page with latest articles"""
    try:
        if not supabase:
            flash('Database not configured. Please set up your Supabase credentials in .env file.', 'error')
            return render_template('index.html', 
                                 articles=[],
                                 categories=NEWS_CATEGORIES,
                                 get_category_icon=get_category_icon,
                                 current_category='All',
                                 page_title='Latest News')
        
        # Get latest articles
        result = supabase.table('articles').select('*').order('created_at', desc=True).limit(9).execute()
        articles = result.data or []
        
        return render_template('index.html', 
                             articles=articles,
                             categories=NEWS_CATEGORIES,
                             get_category_icon=get_category_icon,
                             current_category='All',
                             page_title='Latest News')
    except Exception as e:
        flash(f'Error loading articles: {str(e)}', 'error')
        return render_template('index.html', 
                             articles=[],
                             categories=NEWS_CATEGORIES,
                             get_category_icon=get_category_icon,
                             current_category='All',
                             page_title='Latest News')

@app.route('/category/<category>')
def category_articles(category):
    """Show articles for a specific category"""
    try:
        if not supabase:
            flash('Database not configured. Please set up your Supabase credentials.', 'error')
            return redirect(url_for('home'))
        
        # Get articles by category
        result = supabase.table('articles').select('*').eq('category', category).order('created_at', desc=True).limit(9).execute()
        articles = result.data or []
        
        return render_template('index.html',
                             articles=articles,
                             categories=NEWS_CATEGORIES,
                             get_category_icon=get_category_icon,
                             current_category=category,
                             page_title=f'{category} News')
    except Exception as e:
        flash(f'Error loading {category} articles: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/article/<int:article_id>')
def view_article(article_id):
    """View a specific article"""
    try:
        if not supabase:
            flash('Database not configured. Please set up your Supabase credentials.', 'error')
            return redirect(url_for('home'))
        
        result = supabase.table('articles').select('*').eq('id', article_id).single().execute()
        article = result.data
        
        if not article:
            flash('Article not found', 'error')
            return redirect(url_for('home'))
            
        return render_template('article.html', article=article)
    except Exception as e:
        flash(f'Error loading article: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/admin')
def admin_panel():
    """Admin panel for managing articles"""
    try:
        if not supabase:
            flash('Database not configured. Please set up your Supabase credentials in .env file.', 'error')
            return render_template('admin.html', 
                                 articles=[],
                                 categories=NEWS_CATEGORIES)
        
        # Get recent articles for admin view
        result = supabase.table('articles').select('*').order('created_at', desc=True).limit(10).execute()
        articles = result.data or []
        
        return render_template('admin.html', 
                             articles=articles,
                             categories=NEWS_CATEGORIES)
    except Exception as e:
        flash(f'Error loading admin panel: {str(e)}', 'error')
        return render_template('admin.html', 
                             articles=[],
                             categories=NEWS_CATEGORIES)

def fetch_news_from_perplexity(topic, category):
    """Fetch and rewrite news using Perplexity API with robust error handling and correct format"""
    if not PERPLEXITY_API_KEY or PERPLEXITY_API_KEY.startswith('your_'):
        raise Exception('Perplexity API key not configured. Please add it to your .env file.')
    
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
            raise Exception('401 Unauthorized: Your API key is invalid or does not have access. Please check your Perplexity account and API key.')
        else:
            raise Exception(f'Perplexity API error: {response.status_code} - {response.text}')
    except Exception as e:
        raise Exception(f'Failed to fetch news: {str(e)}')

@app.route('/admin/fetch-news', methods=['POST'])
def fetch_and_store_news():
    """Fetch news from Perplexity and store in Supabase"""
    try:
        if not supabase:
            flash('Database not configured. Please set up your Supabase credentials.', 'error')
            return redirect(url_for('admin_panel'))
        
        topic = request.form.get('topic', 'trending news')
        category = request.form.get('category', 'Technology')
        
        if not topic.strip():
            flash('Please enter a news topic', 'error')
            return redirect(url_for('admin_panel'))
        
        # Fetch news from Perplexity
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
        
        flash(f'Successfully fetched and stored article: {article_data["headline"]}', 'success')
        
    except Exception as e:
        flash(f'Error fetching news: {str(e)}', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/test-supabase')
def test_supabase():
    """Test Supabase connection"""
    if not supabase:
        flash('Supabase not configured. Please add your credentials to .env file.', 'error')
    else:
        try:
            result = supabase.table('articles').select('*').limit(1).execute()
            flash('Supabase connection successful!', 'success')
        except Exception as e:
            flash(f'Supabase connection failed: {str(e)}', 'error')
    
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000) 