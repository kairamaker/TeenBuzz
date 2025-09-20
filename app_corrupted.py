from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from supabase.client import create_client, Client
import os
from dotenv import load_dotenv
from database_manager import get_database, get_database_status
from auth_system import auth_manager, login_required, admin_required, get_current_user, is_authenticated, is_admin
import requests
import secrets
import time
from datetime import datetime, timedelta
import json
import random
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from threading import Thread, Lock

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Change this to a secure secret key

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

# Initialize database (local or cloud)
supabase = None
local_db = None

try:
    db_instance = get_database()
    
    if db_instance is None:
        # Use Supabase (cloud)
        if SUPABASE_URL and SUPABASE_KEY and not SUPABASE_URL.startswith('your_') and not SUPABASE_KEY.startswith('your_'):
            print(f"Initializing Supabase client with URL: {SUPABASE_URL}")
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            # Test the connection
            test_result = supabase.table('articles').select('*').limit(1).execute()
            print("✅ Supabase connection successful!")
        else:
            print("Supabase credentials not configured or are placeholders")
    else:
        # Use local database
        local_db = db_instance
        print(f"✅ Using local database: {get_database_status()}")
        
    except Exception as e:
    print(f"Warning: Could not initialize database: {e}")
        supabase = None
    local_db = None

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'teenbuzzteam@gmail.com'
app.config['MAIL_PASSWORD'] = 'wjpq dpoi ureg sdaa'
app.config['MAIL_DEFAULT_SENDER'] = 'teenbuzzteam@gmail.com'
mail = Mail(app)

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

@app.context_processor
def inject_template_helpers():
    return {
        'format_date': format_date,
        'get_category_icon': get_category_icon,
    }

# Track if we've done an automatic fetch for today to avoid repeated triggers
_last_auto_fetch_date_lock = Lock()
_last_auto_fetch_date = None

def _auto_fetch_if_needed_async():
    """Kick off a background fetch of up to 3 articles if none exist for today."""
    def _task():
        global _last_auto_fetch_date
        try:
            if not supabase:
                return
            # Check if already fetched today
            today = datetime.now().date()
            with _last_auto_fetch_date_lock:
                if _last_auto_fetch_date == today:
                    return
            # Check DB for today's articles
            today_start = datetime.combine(today, datetime.min.time()).isoformat()
            today_end = datetime.combine(today, datetime.max.time()).isoformat()
            existing_today = supabase.table('articles').select('id').gte('created_at', today_start).lte('created_at', today_end).execute()
            if existing_today.data:
                with _last_auto_fetch_date_lock:
                    _last_auto_fetch_date = today
                return
            # Require Perplexity key
            if not PERPLEXITY_API_KEY or PERPLEXITY_API_KEY.startswith('your_'):
                return
            # Fetch up to 3 articles using existing helper
            attempts = 0
            successes = 0
            used_categories = set()
            while attempts < 6 and successes < 3:
                attempts += 1
                try:
                    # Pick a category not used yet if possible
                    remaining = [c for c in NEWS_CATEGORIES if c not in used_categories] or NEWS_CATEGORIES
                    category = random.choice(remaining)
                    used_categories.add(category)
                    article_data = fetch_news_from_perplexity('top stories today', category)
                    supabase.table('articles').insert({
                        'headline': article_data['headline'],
                        'content': article_data['content'],
                        'source': article_data['source'],
                        'original_url': article_data.get('original_url', ''),
                        'category': article_data['category'],
                        'relevance': article_data['relevance'],
                        'created_at': datetime.now().isoformat()
                    }).execute()
                    successes += 1
                except Exception:
                    continue
            with _last_auto_fetch_date_lock:
                _last_auto_fetch_date = today
        except Exception:
            # Fail silently; homepage should still render
            pass
    Thread(target=_task, daemon=True).start()


def get_sample_articles():
    """Get sample articles for fallback"""
    return [
        {
            'id': 1,
            'headline': 'New AI Tools Help Students Study Smarter, Not Harder',
            'content': 'Students are discovering how artificial intelligence can revolutionize their study habits. From personalized learning plans to instant homework help, AI is making education more accessible and effective for teens everywhere. These tools are changing how students approach learning, making complex subjects more digestible and study sessions more efficient.',
            'category': 'Technology',
            'source': 'TechCrunch',
            'created_at': datetime.now().isoformat(),
            'views': 1250,
            'likes': 89
        },
        {
            'id': 2,
            'headline': 'Climate Change: What Teens Can Do to Make a Real Difference',
            'content': 'Young activists are leading the charge against climate change with innovative solutions and powerful voices. Learn about the practical steps you can take to protect our planet and inspire others to join the movement. From school strikes to social media campaigns, teens are proving that age is just a number when it comes to environmental action.',
            'category': 'Environment',
            'source': 'BBC News',
            'created_at': datetime.now().isoformat(),
            'views': 980,
            'likes': 76
        },
        {
            'id': 3,
            'headline': 'Mental Health Apps That Actually Help Teens Cope',
            'content': 'New mental health resources designed specifically for teenagers are making it easier to find support and build resilience. These apps offer everything from meditation guides to crisis support, helping teens navigate the challenges of modern life with better mental health tools and resources.',
            'category': 'Health',
            'source': 'NPR',
            'created_at': datetime.now().isoformat(),
            'views': 850,
            'likes': 64
        },
        {
            'id': 4,
            'headline': 'The Future of Social Media: What Teens Need to Know',
            'content': 'Social media platforms are evolving rapidly, and teens are at the forefront of these changes. From new privacy features to emerging platforms, understanding these shifts can help you navigate the digital world more safely and effectively.',
            'category': 'Technology',
            'source': 'Wired',
            'created_at': datetime.now().isoformat(),
            'views': 720,
            'likes': 58
        },
        {
            'id': 5,
            'headline': 'How Gen Z is Redefining Success in the Workplace',
            'content': 'Young people are changing what it means to have a successful career, prioritizing work-life balance, mental health, and meaningful work over traditional corporate ladders. This shift is reshaping entire industries and creating new opportunities.',
            'category': 'Social Issues',
            'source': 'Forbes',
            'created_at': datetime.now().isoformat(),
            'views': 680,
            'likes': 52
        },
        {
            'id': 6,
            'headline': 'The Science Behind Why Music Moves Us',
            'content': 'New research reveals how music affects our brains and emotions, especially during teenage years. Understanding these connections can help you use music more effectively for studying, relaxation, and emotional regulation.',
            'category': 'Science',
            'source': 'Scientific American',
            'created_at': datetime.now().isoformat(),
            'views': 590,
            'likes': 45
        }
    ]

def get_sample_categories():
    """Get sample categories for fallback"""
    return [
        {'name': 'Technology', 'description': 'Latest tech news and innovations', 'icon': 'fas fa-laptop-code'},
        {'name': 'Environment', 'description': 'Climate and environmental news', 'icon': 'fas fa-leaf'},
        {'name': 'Health', 'description': 'Health and wellness topics', 'icon': 'fas fa-heartbeat'},
        {'name': 'Social Issues', 'description': 'Social justice and community topics', 'icon': 'fas fa-users'},
        {'name': 'Science', 'description': 'Scientific discoveries and research', 'icon': 'fas fa-flask'}
    ]

def get_articles_from_db(limit=None, category=None, order_by='created_at', desc=True):
    """Get articles from either local or cloud database"""
    if local_db:
        # Use local database
        with local_db:
            query = "SELECT * FROM articles"
            params = []
            
            if category:
                query += " WHERE category = ?"
                params.append(category)
            
            if order_by:
                order_direction = "DESC" if desc else "ASC"
                query += f" ORDER BY {order_by} {order_direction}"
            
            if limit:
                query += f" LIMIT {limit}"
            
            return local_db.execute_query(query, tuple(params))
    else:
        # Use Supabase
        if not supabase:
            return []
        
        query = supabase.table('articles').select('*')
        
        if category:
            query = query.eq('category', category)
        
        if order_by:
            query = query.order(order_by, desc=desc)
        
        if limit:
            query = query.limit(limit)
        
        result = query.execute()
        return result.data or []

def insert_article_to_db(article_data):
    """Insert article into either local or cloud database"""
    if local_db:
        # Use local database
        with local_db:
            return local_db.insert('articles', article_data)
    else:
        # Use Supabase
        if not supabase:
            return None
        
        result = supabase.table('articles').insert(article_data).execute()
        return result.data[0] if result.data else None


@app.route('/')
def home():
    """Home page with latest articles"""
    try:
        # Use the configured database (local or cloud)
        if local_db:
            # Use local database
            flash(f'✅ Using local database: {get_database_status()}', 'success')
            articles = get_articles_from_db(limit=10)
            categories = local_db.select('categories')
            
            # Get "For You" articles (top 3 by views)
            for_you_articles = get_articles_from_db(limit=3, order_by='views', desc=True)
            
            # Get "Continue Reading" articles (recently viewed)
            continue_reading_articles = get_articles_from_db(limit=3, order_by='created_at', desc=True)
            
        elif supabase:
            # Use Supabase
            flash('✅ Connected to Supabase database', 'success')
            articles = get_articles_from_db(limit=10)
            categories = supabase.table('categories').select('*').execute().data or []
            
            # Get "For You" articles
            for_you_articles = get_articles_from_db(limit=3, order_by='views', desc=True)
            
            # Get "Continue Reading" articles  
            continue_reading_articles = get_articles_from_db(limit=3, order_by='created_at', desc=True)
            
        else:
            # Fallback to sample data
            flash('Database connection in progress. Showing sample articles while we connect to your database.', 'info')
            articles = get_sample_articles()
            categories = get_sample_categories()
            
            # Sample "For You" and "Continue Reading" articles
            for_you_articles = articles[:3]
            continue_reading_articles = articles[3:6]
        
        # Add reading progress for continue reading articles
        for article in continue_reading_articles:
            if 'read_progress' not in article:
                article['read_progress'] = 65
                article['last_read_time'] = '2 hours ago'
        
        return render_template('index_modern.html', 
                             articles=articles,
                             for_you_articles=for_you_articles,
                             continue_reading_articles=continue_reading_articles,
                             categories=NEWS_CATEGORIES,
                             get_category_icon=get_category_icon,
                             format_date=format_date,
                             current_category='All',
                             page_title='Latest News',
                             current_date=datetime.now().strftime('%B %d, %Y'))
    
    except Exception as e:
        print(f"Error in home route: {e}")
        # Fallback to sample data on any error
        flash('Using sample data due to an error.', 'warning')
        articles = get_sample_articles()
        for_you_articles = articles[:3]
        continue_reading_articles = articles[3:6]
        
        return render_template('index_modern.html',
                             articles=articles,
                             for_you_articles=for_you_articles,
                             continue_reading_articles=continue_reading_articles,
                             categories=NEWS_CATEGORIES,
                             get_category_icon=get_category_icon,
                             format_date=format_date,
                             current_category='All',
                             page_title='Latest News',
                             current_date=datetime.now().strftime('%B %d, %Y'))


@app.route('/trending')
def trending():
    """Trending articles page"""
    try:
        if local_db:
            # Use local database
            flash(f'✅ Using local database: {get_database_status()}', 'success')
            trending_articles = get_articles_from_db(limit=10, order_by='views', desc=True)
            
            # Add engagement scores for demo
            for i, article in enumerate(trending_articles):
                article['engagement_score'] = max(60, 95 - (i * 3))
                
        elif supabase:
            # Use Supabase
            flash('✅ Connected to Supabase database', 'success')
            trending_articles = get_articles_from_db(limit=10, order_by='views', desc=True)
            
            # Add engagement scores for demo
            for i, article in enumerate(trending_articles):
                article['engagement_score'] = max(60, 95 - (i * 3))
        else:
            # Fallback to sample data
            flash('Using sample trending data while database connection is being resolved.', 'info')
            trending_articles = get_sample_articles()
            
            # Add engagement scores for demo
            for i, article in enumerate(trending_articles):
                article['engagement_score'] = max(60, 95 - (i * 3))
        
        return render_template('trending.html',
                             trending_articles=trending_articles,
                             categories=NEWS_CATEGORIES,
                             get_category_icon=get_category_icon,
                             format_date=format_date,
                             current_date=datetime.now().strftime('%B %d, %Y'))
        
    except Exception as e:
        print(f"Error in trending route: {e}")
        # Fallback to sample data on any error
        flash('Using sample trending data due to an error.', 'warning')
        trending_articles = get_sample_articles()
        
        # Add engagement scores for demo
        for i, article in enumerate(trending_articles):
            article['engagement_score'] = max(60, 95 - (i * 3))
        
        return render_template('trending.html',
                             trending_articles=trending_articles,
                             categories=NEWS_CATEGORIES,
                             get_category_icon=get_category_icon,
                             format_date=format_date,
                             current_date=datetime.now().strftime('%B %d, %Y'))


@app.route('/search')
def search_articles():
    """Search articles page"""
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    date_filter = request.args.get('date', '')
    sort_by = request.args.get('sort', 'relevance')
    
    try:
        if local_db:
            # Use local database
            flash(f'✅ Using local database: {get_database_status()}', 'success')
            articles = get_articles_from_db(limit=20)
            
            # Apply filters
            if query:
                articles = [a for a in articles if query.lower() in a.get('headline', '').lower() or query.lower() in a.get('content', '').lower()]
            if category:
                articles = [a for a in articles if a.get('category') == category]
                
        elif supabase:
            # Use Supabase
            flash('✅ Connected to Supabase database', 'success')
            articles = get_articles_from_db(limit=20)
            
            # Apply filters
            if query:
                articles = [a for a in articles if query.lower() in a.get('headline', '').lower() or query.lower() in a.get('content', '').lower()]
            if category:
                articles = [a for a in articles if a.get('category') == category]
            else:
            # Fallback to sample data
            flash('Using sample search data while database connection is being resolved.', 'info')
            articles = get_sample_articles()
            
            # Apply filters
            if query:
                articles = [a for a in articles if query.lower() in a.get('headline', '').lower() or query.lower() in a.get('content', '').lower()]
            if category:
                articles = [a for a in articles if a.get('category') == category]
        
        return render_template('search.html',
                             articles=articles,
                             query=query,
                             selected_category=category,
                             selected_date=date_filter,
                             selected_sort=sort_by,
                             categories=NEWS_CATEGORIES,
                             get_category_icon=get_category_icon,
                             format_date=format_date,
                             current_date=datetime.now().strftime('%B %d, %Y'))
    
    except Exception as e:
        print(f"Error in search route: {e}")
        # Fallback to sample data on any error
        flash('Using sample search data due to an error.', 'warning')
        articles = get_sample_articles()
        
        return render_template('search.html',
                             articles=articles,
                             query=query,
                             selected_category=category,
                             selected_date=date_filter,
                             selected_sort=sort_by,
                             categories=NEWS_CATEGORIES,
                             get_category_icon=get_category_icon,
                             format_date=format_date,
                             current_date=datetime.now().strftime('%B %d, %Y'))


@app.route('/categories')
def categories_page():
    """Categories page with filtering options"""
    try:
        if not supabase:
            flash('Database connection in progress. DNS propagation may take a few hours. Using sample data until connection is established.', 'info')
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')
        
        if not username or not password:
            flash('Please fill in all fields', 'error')
            return render_template('login.html')
        
        # Attempt login
        success, message, user_data = auth_manager.login_user(username, password)
        
        if success:
            # Set session
            session['user_id'] = user_data['id']
            session['username'] = user_data['username']
            session['is_admin'] = user_data['is_admin']
            
            if remember_me:
                session.permanent = True
            
            flash(message, 'success')
            
            # Redirect to next page or home
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
            flash(message, 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([username, email, password, confirm_password]):
            flash('Please fill in all fields', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        # Attempt registration
        success, message = auth_manager.register_user(username, email, password)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout user"""
    auth_manager.logout_user()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = get_current_user()
    return render_template('profile.html', user=user)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Please enter your email address', 'error')
            return render_template('forgot_password.html')
        
        try:
            if auth_manager.db:
                with auth_manager.db:
                    # Find user by email
                    users = auth_manager.db.select('users', where='email = ?', params=(email,))
                    
                    if users:
                        user = users[0]
                        
                        # Generate reset token
                        reset_token = secrets.token_urlsafe(32)
                        expires_at = datetime.now() + timedelta(hours=1)
                        
                        # Store reset token
                        token_data = {
                            'user_id': user['id'],
                            'token': reset_token,
                            'expires_at': expires_at.isoformat(),
                            'used': False
                        }
                        
                        auth_manager.db.insert('password_reset_tokens', token_data)
                        
                        # Send email (in production, this would actually send)
                        reset_url = f"{request.url_root}reset-password/{reset_token}"
                        
                        try:
                            # For now, just flash the URL (in production, send email)
                            flash(f'Password reset link: {reset_url}', 'info')
                            flash('In production, this would be sent to your email', 'info')
    except Exception as e:
                            flash(f'Email sending failed: {str(e)}', 'error')
                        
                        flash('If an account with that email exists, a password reset link has been sent.', 'success')
                    else:
                        # Don't reveal if email exists or not
                        flash('If an account with that email exists, a password reset link has been sent.', 'success')
            else:
                flash('Database not available', 'error')
                
    except Exception as e:
            flash(f'Error processing request: {str(e)}', 'error')
    
            return render_template('forgot_password.html')
        
        try:
            if not supabase:
                flash('Database not configured', 'error')
                return render_template('forgot_password.html')
            
            # Check if email exists
            result = supabase.table('users').select('id, username').eq('email', email).single().execute()
            
            if result.data:
                user_id = result.data['id']
                
                # Generate secure reset token
                token = secrets.token_urlsafe(32)
                expires_at = (datetime.now() + timedelta(hours=1)).isoformat()
                
                # Store token in database
                supabase.table('password_reset_tokens').insert({
                    'user_id': user_id,
                    'token': token,
                    'expires_at': expires_at
                }).execute()
                
                # Generate reset link
                reset_link = url_for('reset_password', token=token, _external=True)
                
                # Send real email
                msg = Message("TeenBuzz Password Reset", recipients=[email])
                msg.body = f"""Hello!

To reset your password click the link below:

{reset_link}

This link expires in 1 hour.

If you didn't request this, please ignore this email.

Thank you,
Teen Buzz Team"""
                mail.send(msg)
                flash(f'Password reset instructions have been sent to {email}', 'success')
                return redirect(url_for('login'))
            else:
                flash('Email not found in our system', 'error')
                
        except Exception as e:
            flash(f'Error processing request: {str(e)}', 'error')
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password page"""
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not new_password or not confirm_password:
            flash('Please enter both new password and confirm password', 'error')
            return render_template('reset_password.html', token=token)

        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html', token=token)

        if len(new_password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('reset_password.html', token=token)

        try:
            if not auth_manager.db:
                flash('Database not available', 'error')
                return render_template('reset_password.html', token=token)

            # Verify token
            with auth_manager.db:
                tokens = auth_manager.db.select('password_reset_tokens', where='token = ? AND used = ?', params=(token, False))
                
                if not tokens:
                    flash('Password reset link is invalid or expired.', 'error')
                    return render_template('reset_password.html', token=token)
                
                token_data = tokens[0]
                
                # Check if token is expired
                expires_at = datetime.fromisoformat(token_data['expires_at'])
                if datetime.now() > expires_at:
                    flash('Password reset link has expired.', 'error')
                    return render_template('reset_password.html', token=token)
                
                # Validate new password
                is_valid, message = auth_manager.validate_password(new_password)
                if not is_valid:
                    flash(message, 'error')
                    return render_template('reset_password.html', token=token)
                
                # Update password
                new_hash = auth_manager.hash_password(new_password)
                auth_manager.db.update('users', {'password_hash': new_hash}, 'id = ?', (token_data['user_id'],))
                
                # Mark token as used
                auth_manager.db.update('password_reset_tokens', {'used': True}, 'id = ?', (token_data['id'],))
                
                flash('Password reset successfully! You can now login with your new password.', 'success')
                return redirect(url_for('login'))
                
        except Exception as e:
            flash(f'Error resetting password: {str(e)}', 'error')
            current_time = datetime.now(timezone.utc)
            
            if expires_at < current_time:
                flash('Password reset link has expired.', 'error')
                return redirect(url_for('forgot_password'))

            user_id = token_data['user_id']

            # Update user password
            password_hash = generate_password_hash(new_password)
            supabase.table('users').update({'password_hash': password_hash}).eq('id', user_id).execute()

            # Delete the used token
            supabase.table('password_reset_tokens').delete().eq('token', token).execute()

            flash('Your password has been updated! You are now able to log in', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error resetting password: {str(e)}', 'error')
            return render_template('reset_password.html', token=token)

    return render_template('reset_password.html', token=token)

@app.route('/article/<int:article_id>')
def view_article(article_id):
    """View individual article"""
    try:
        if local_db:
            # Use local database
            articles = local_db.select('articles', where='id = ?', params=(article_id,))
            if articles:
                article = articles[0]
            else:
                flash('Article not found', 'error')
                return redirect(url_for('home'))
        elif supabase:
            # Use Supabase
            result = supabase.table('articles').select('*').eq('id', article_id).execute()
            if result.data:
                article = result.data[0]
            else:
                flash('Article not found', 'error')
                return redirect(url_for('home'))
        else:
            # Fallback to sample data
            sample_articles = get_sample_articles()
            article = next((a for a in sample_articles if a['id'] == article_id), None)
            if not article:
                flash('Article not found', 'error')
                return redirect(url_for('home'))
        
        return render_template('article_improved.html',
                             article=article,
                             get_category_icon=get_category_icon,
                             format_date=format_date)
    
    except Exception as e:
        print(f"Error viewing article: {e}")
        flash('Error loading article', 'error')
        return redirect(url_for('home'))

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


@app.route('/admin/database-toggle')
def database_toggle():
    """Database toggle admin page"""
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('home'))
    
    current_db = get_database_status()
    return render_template('database_toggle.html', current_database=current_db)

@app.route('/admin/switch-to-local')
def switch_to_local():
    """Switch to local database"""
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('home'))
    
    from database_manager import switch_to_local
    switch_to_local()
    flash('Switched to local database', 'success')
    return redirect(url_for('database_toggle'))

@app.route('/admin/switch-to-cloud')
def switch_to_cloud():
    """Switch to cloud database"""
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('home'))
    
    from database_manager import switch_to_cloud
    switch_to_cloud()
    flash('Switched to cloud database', 'success')
    return redirect(url_for('database_toggle'))


# Context processor to make auth functions available in templates
@app.context_processor
def inject_auth():
    return {
        'current_user': get_current_user(),
        'is_authenticated': is_authenticated(),
        'is_admin': is_admin()
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002) 