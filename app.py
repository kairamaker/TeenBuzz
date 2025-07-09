from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from supabase.client import create_client, Client
import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta
import json
import random
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.email = user_data.get('email')
        self.is_admin = user_data.get('is_admin', False)
        self.created_at = user_data.get('created_at')

@login_manager.user_loader
def load_user(user_id):
    if not supabase:
        return None
    try:
        result = supabase.table('users').select('*').eq('id', user_id).single().execute()
        if result.data:
            return User(result.data)
    except:
        pass
    return None

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

def format_date(date_string):
    """Format date string to DD/MM/YYYY format"""
    try:
        if not date_string:
            return "Unknown"
        # Parse the ISO format date string
        date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date_obj.strftime('%d/%m/%Y')
    except:
        return "Unknown"

@app.route('/')
def home():
    """Home page with latest articles"""
    try:
        if not supabase:
            flash('Database not configured. Please set up your Supabase credentials in .env file.', 'error')
            return render_template('index.html', 
                                 today_articles=[],
                                 recent_articles=[],
                                 categories=NEWS_CATEGORIES,
                                 categories_with_articles=[],
                                 get_category_icon=get_category_icon,
                                 format_date=format_date,
                                 current_category='All',
                                 page_title='Latest News',
                                 current_date=datetime.now().strftime('%B %d, %Y'))
        
        # Get today's articles
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time()).isoformat()
        today_end = datetime.combine(today, datetime.max.time()).isoformat()
        today_result = supabase.table('articles').select('*').gte('created_at', today_start).lte('created_at', today_end).order('created_at', desc=True).execute()
        today_articles = today_result.data or []

        # Get all articles (limited to 8-10)
        all_articles_result = supabase.table('articles').select('*').order('created_at', desc=True).limit(10).execute()
        all_articles = all_articles_result.data or []

        # Get categories that have articles
        all_articles_combined = today_articles + all_articles
        categories_with_articles = []
        if all_articles_combined:
            article_categories = set(article['category'] for article in all_articles_combined)
            categories_with_articles = [cat for cat in NEWS_CATEGORIES if cat in article_categories]
        
        return render_template('index.html', 
                             today_articles=today_articles,
                             all_articles=all_articles,
                             categories=NEWS_CATEGORIES,
                             categories_with_articles=categories_with_articles,
                             get_category_icon=get_category_icon,
                             format_date=format_date,
                             current_category='All',
                             page_title='Latest News',
                             current_date=datetime.now().strftime('%B %d, %Y'))
    except Exception as e:
        flash(f'Error loading articles: {str(e)}', 'error')
        return render_template('index.html', 
                             today_articles=[],
                             all_articles=[],
                             categories=NEWS_CATEGORIES,
                             categories_with_articles=[],
                             get_category_icon=get_category_icon,
                             format_date=format_date,
                             current_category='All',
                             page_title='Latest News',
                             current_date=datetime.now().strftime('%B %d, %Y'))

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
        
        # Get today's articles for this category
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time()).isoformat()
        today_end = datetime.combine(today, datetime.max.time()).isoformat()
        
        today_result = supabase.table('articles').select('*').eq('category', category).gte('created_at', today_start).lte('created_at', today_end).order('created_at', desc=True).execute()
        today_articles = today_result.data or []
        
        # Get categories that have articles
        categories_with_articles = []
        if articles:
            article_categories = set(article['category'] for article in articles)
            categories_with_articles = [cat for cat in NEWS_CATEGORIES if cat in article_categories]
        
        return render_template('index.html',
                             articles=articles,
                             today_articles=today_articles,
                             categories=NEWS_CATEGORIES,
                             categories_with_articles=categories_with_articles,
                             get_category_icon=get_category_icon,
                             current_category=category,
                             page_title=f'{category} News',
                             current_date=datetime.now().strftime('%B %d, %Y'))
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
@login_required
def admin_panel():
    """Admin panel for managing articles"""
    # Check if user is admin
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
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
@login_required
def fetch_and_store_news():
    """Fetch news from Perplexity and store in Supabase"""
    # Check if user is admin
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
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
@login_required
def test_supabase():
    """Test Supabase connection"""
    # Check if user is admin
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    if not supabase:
        flash('Supabase not configured. Please add your credentials to .env file.', 'error')
    else:
        try:
            result = supabase.table('articles').select('*').limit(1).execute()
            flash('Supabase connection successful!', 'success')
        except Exception as e:
            flash(f'Supabase connection failed: {str(e)}', 'error')
    
    return redirect(url_for('admin_panel'))

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please enter both email and password', 'error')
            return render_template('login.html')
        
        try:
            if not supabase:
                flash('Database not configured', 'error')
                return render_template('login.html')
            
            # Get user from database
            result = supabase.table('users').select('*').eq('email', email).single().execute()
            user_data = result.data
            
            if user_data and check_password_hash(user_data['password_hash'], password):
                user = User(user_data)
                login_user(user)
                
                # Update last login
                supabase.table('users').update({'last_login': datetime.now().isoformat()}).eq('id', user_data['id']).execute()
                
                flash(f'Welcome back, {user_data.get("name", email)}!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid email or password', 'error')
                
        except Exception as e:
            flash(f'Login error: {str(e)}', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        topics = request.form.getlist('topics')
        
        # Validation
        if not name or not email or not password:
            flash('Please fill in all required fields', 'error')
            return render_template('register.html', categories=NEWS_CATEGORIES, get_category_icon=get_category_icon)
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html', categories=NEWS_CATEGORIES, get_category_icon=get_category_icon)
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html', categories=NEWS_CATEGORIES, get_category_icon=get_category_icon)
        
        if not topics:
            flash('Please select at least one category of interest', 'error')
            return render_template('register.html', categories=NEWS_CATEGORIES, get_category_icon=get_category_icon)
        
        try:
            if not supabase:
                flash('Database not configured', 'error')
                return render_template('register.html', categories=NEWS_CATEGORIES, get_category_icon=get_category_icon)
            
            # Check if email already exists
            result = supabase.table('users').select('id').eq('email', email).execute()
            if result.data:
                flash('Email already registered', 'error')
                return render_template('register.html', categories=NEWS_CATEGORIES, get_category_icon=get_category_icon)
            
            # Create new user
            password_hash = generate_password_hash(password)
            user_data = {
                'name': name,
                'email': email,
                'password_hash': password_hash,
                'topics_of_interest': topics,
                'created_at': datetime.now().isoformat()
            }
            
            result = supabase.table('users').insert(user_data).execute()
            new_user = result.data[0]
            
            # Log in the new user
            user = User(new_user)
            login_user(user)
            
            flash(f'Account created successfully! Welcome, {name}!', 'success')
            return redirect(url_for('home'))
            
        except Exception as e:
            flash(f'Registration error: {str(e)}', 'error')
    
    return render_template('register.html', categories=NEWS_CATEGORIES, get_category_icon=get_category_icon)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    """User profile page showing their drawn articles"""
    try:
        if not supabase:
            flash('Database not configured', 'error')
            return redirect(url_for('home'))
        
        # Get user's drawn articles
        result = supabase.table('articles').select('*').eq('drawn_by_user_id', current_user.id).order('created_at', desc=True).execute()
        user_articles = result.data or []
        
        # Get user's draw history
        draw_result = supabase.table('user_draws').select('*').eq('user_id', current_user.id).order('drawn_at', desc=True).limit(10).execute()
        draw_history = draw_result.data or []
        
        return render_template('profile.html', 
                             user=current_user,
                             articles=user_articles,
                             draw_history=draw_history)
    except Exception as e:
        flash(f'Error loading profile: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/categories')
def categories_page():
    """Categories page with filtering options"""
    try:
        if not supabase:
            flash('Database not configured. Please set up your Supabase credentials in .env file.', 'error')
            return render_template('categories.html', 
                                 categories=NEWS_CATEGORIES,
                                 articles_by_category={},
                                 all_articles=[],
                                 get_category_icon=get_category_icon,
                                 format_date=format_date,
                                 current_date=datetime.now().strftime('%B %d, %Y'))
        
        # Get all articles grouped by category
        result = supabase.table('articles').select('*').order('created_at', desc=True).execute()
        all_articles = result.data or []
        
        # Group articles by category
        articles_by_category = {}
        for category in NEWS_CATEGORIES:
            articles_by_category[category] = []
        
        for article in all_articles:
            if article['category'] in articles_by_category:
                articles_by_category[article['category']].append(article)
        
        return render_template('categories.html', 
                             categories=NEWS_CATEGORIES,
                             articles_by_category=articles_by_category,
                             all_articles=all_articles,
                             get_category_icon=get_category_icon,
                             format_date=format_date,
                             current_date=datetime.now().strftime('%B %d, %Y'))
    except Exception as e:
        flash(f'Error loading categories: {str(e)}', 'error')
        return render_template('categories.html', 
                             categories=NEWS_CATEGORIES,
                             articles_by_category={},
                             all_articles=[],
                             get_category_icon=get_category_icon,
                             format_date=format_date,
                             current_date=datetime.now().strftime('%B %d, %Y'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Please enter your email address', 'error')
            return render_template('forgot_password.html')
        
        try:
            if not supabase:
                flash('Database not configured', 'error')
                return render_template('forgot_password.html')
            
            # Check if email exists
            result = supabase.table('users').select('id, username').eq('email', email).single().execute()
            
            if result.data:
                # In a real app, you would send a password reset email here
                # For now, we'll just show a success message
                flash(f'Password reset instructions have been sent to {email}', 'success')
                return redirect(url_for('login'))
            else:
                flash('Email not found in our system', 'error')
                
        except Exception as e:
            flash(f'Error processing request: {str(e)}', 'error')
    
    return render_template('forgot_password.html')

@app.route('/draw-article', methods=['POST'])
@login_required
def draw_article():
    """Draw a new article for the logged-in user"""
    try:
        if not supabase:
            return jsonify({'success': False, 'error': 'Database not configured'})
        
        # Check rate limiting (max 1 article per 5 minutes)
        five_minutes_ago = (datetime.now() - timedelta(minutes=5)).isoformat()
        recent_draws = supabase.table('user_draws').select('*').eq('user_id', current_user.id).gte('drawn_at', five_minutes_ago).execute()
        
        if recent_draws.data and len(recent_draws.data) >= 1:
            return jsonify({'success': False, 'error': 'You can only draw one article every 5 minutes. Please wait a bit!'})
        
        # Get random category and topic
        category = random.choice(NEWS_CATEGORIES)
        topics = {
            'Technology': ['AI news', 'social media updates', 'new apps', 'tech trends'],
            'Entertainment': ['movie releases', 'celebrity news', 'TV shows', 'music news'],
            'Sports': ['sports highlights', 'athlete news', 'game results', 'sports trends'],
            'Health': ['teen health', 'wellness tips', 'mental health', 'fitness'],
            'Environment': ['climate change', 'sustainability', 'environmental news'],
            'Education': ['school news', 'study tips', 'college prep', 'education trends'],
            'Social Issues': ['social justice', 'teen activism', 'community news'],
            'Science': ['scientific discoveries', 'space news', 'research findings'],
            'Gaming': ['video games', 'esports', 'gaming news', 'new releases'],
            'Music': ['music releases', 'artist news', 'concert updates']
        }
        
        topic = random.choice(topics.get(category, ['trending news']))
        
        # Fetch article from Perplexity
        article_data = fetch_news_from_perplexity(topic, category)
        
        # Store article in database
        article_result = supabase.table('articles').insert({
            'headline': article_data['headline'],
            'content': article_data['content'],
            'source': article_data['source'],
            'original_url': article_data.get('original_url', ''),
            'category': article_data['category'],
            'relevance': article_data['relevance'],
            'drawn_by_user_id': current_user.id,
            'created_at': datetime.now().isoformat()
        }).execute()
        
        new_article = article_result.data[0]
        
        # Record the draw
        supabase.table('user_draws').insert({
            'user_id': current_user.id,
            'article_id': new_article['id'],
            'drawn_at': datetime.now().isoformat()
        }).execute()
        
        return jsonify({
            'success': True,
            'article': {
                'id': new_article['id'],
                'headline': new_article['headline'],
                'content': new_article['content'][:200] + '...' if len(new_article['content']) > 200 else new_article['content'],
                'category': new_article['category'],
                'source': new_article['source'],
                'original_url': new_article.get('original_url', ''),
                'created_at': new_article['created_at']
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000) 