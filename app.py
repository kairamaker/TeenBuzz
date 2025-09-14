from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from supabase.client import create_client, Client
import os
from dotenv import load_dotenv
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

# Initialize Supabase client only if credentials are provided
supabase = None
if SUPABASE_URL and SUPABASE_KEY and not SUPABASE_URL.startswith('your_') and not SUPABASE_KEY.startswith('your_'):
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Test the connection immediately
        test_result = supabase.table('articles').select('*').limit(1).execute()
        print("✅ Supabase connection successful!")
    except Exception as e:
        print(f"Warning: Could not initialize Supabase client: {e}")
        supabase = None

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'TeenBuzzTeam@gmail.com'
app.config['MAIL_PASSWORD'] = 'wjpq dpoi ureg sdaa'
app.config['MAIL_DEFAULT_SENDER'] = 'TeenBuzzTeam@gmail.com'
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

@app.route('/')
def home():
    """Home page with latest articles"""
    try:
        if not supabase:
            # Show sample articles when database is not configured
            sample_articles = [
                {
                    'id': 1,
                    'headline': 'New AI Tools Help Students Study Smarter, Not Harder',
                    'content': 'Students are discovering how artificial intelligence can revolutionize their study habits. From personalized learning plans to instant homework help, AI is making education more accessible and effective for teens everywhere. These tools are changing how students approach learning, making complex subjects more digestible and study sessions more efficient.',
                    'category': 'Technology',
                    'source': 'TechCrunch',
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': 2,
                    'headline': 'Climate Change: What Teens Can Do to Make a Real Difference',
                    'content': 'Young activists are leading the charge against climate change with innovative solutions and powerful voices. Learn about the practical steps you can take to protect our planet and inspire others to join the movement. From school strikes to social media campaigns, teens are proving that age is just a number when it comes to environmental action.',
                    'category': 'Environment',
                    'source': 'BBC News',
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': 3,
                    'headline': 'Mental Health Apps That Actually Help Teens Cope',
                    'content': 'New mental health resources designed specifically for teenagers are making it easier to find support and build resilience. These apps offer everything from meditation guides to crisis support, helping teens navigate the challenges of modern life with better mental health tools and resources.',
                    'category': 'Health',
                    'source': 'NPR',
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': 4,
                    'headline': 'The Future of Social Media: What Teens Need to Know',
                    'content': 'Social media platforms are evolving rapidly, and teens are at the forefront of these changes. From new privacy features to emerging platforms, understanding these shifts can help you navigate the digital world more safely and effectively.',
                    'category': 'Technology',
                    'source': 'Wired',
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': 5,
                    'headline': 'How Gen Z is Redefining Success in the Workplace',
                    'content': 'Young people are changing what it means to have a successful career, prioritizing work-life balance, mental health, and meaningful work over traditional corporate ladders. This shift is reshaping entire industries and creating new opportunities.',
                    'category': 'Social Issues',
                    'source': 'Forbes',
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': 6,
                    'headline': 'The Science Behind Why Music Moves Us',
                    'content': 'New research reveals how music affects our brains and emotions, especially during teenage years. Understanding these connections can help you use music more effectively for studying, relaxation, and emotional regulation.',
                    'category': 'Science',
                    'source': 'Scientific American',
                    'created_at': datetime.now().isoformat()
                }
            ]
            # Create personalized "For You" articles based on sample data
            for_you_articles = sample_articles[:4]  # Top 4 articles for personalized section
            
            # Create sample "Continue Reading" articles with progress
            continue_reading_articles = [
                {
                    'id': 1,
                    'headline': 'New AI Tools Help Students Study Smarter, Not Harder',
                    'content': 'Students are discovering how artificial intelligence can revolutionize their study habits. From personalized learning plans to instant homework help, AI is making education more accessible and effective for teens everywhere. These tools are changing how students approach learning, making complex subjects more digestible and study sessions more efficient.',
                    'category': 'Technology',
                    'source': 'TechCrunch',
                    'created_at': datetime.now().isoformat(),
                    'read_progress': 65,
                    'last_read_time': '2 hours ago'
                },
                {
                    'id': 2,
                    'headline': 'Climate Change: What Teens Can Do to Make a Real Difference',
                    'content': 'Young activists are leading the charge against climate change with innovative solutions and powerful voices. Learn about the practical steps you can take to protect our planet and inspire others to join the movement. From school strikes to social media campaigns, teens are proving that age is just a number when it comes to environmental action.',
                    'category': 'Environment',
                    'source': 'BBC News',
                    'created_at': datetime.now().isoformat(),
                    'read_progress': 30,
                    'last_read_time': '1 day ago'
                }
            ]
            
            flash('Database connection in progress. Showing sample articles while we connect to your Supabase database.', 'info')
            return render_template('index_modern.html', 
                                 today_articles=sample_articles[:3],
                                 all_articles=sample_articles,
                                 for_you_articles=for_you_articles,
                                 continue_reading_articles=continue_reading_articles,
                                 categories=NEWS_CATEGORIES,
                                 categories_with_articles=['Technology', 'Environment', 'Health', 'Social Issues', 'Science'],
                                 get_category_icon=get_category_icon,
                                 format_date=format_date,
                                 current_category='All',
                                 page_title='Latest News',
                                 current_date=datetime.now().strftime('%B %d, %Y'))
        
        # Get recent articles (last 2 days) for prominent display
        two_days_ago = (datetime.now() - timedelta(days=2)).isoformat()
        recent_result = supabase.table('articles').select('*').gte('created_at', two_days_ago).order('created_at', desc=True).limit(5).execute()
        recent_articles = recent_result.data or []
        
        # Get older articles (3-7 days) for additional content
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        older_recent_result = supabase.table('articles').select('*').gte('created_at', week_ago).lt('created_at', two_days_ago).order('created_at', desc=True).limit(3).execute()
        older_recent_articles = older_recent_result.data or []

        # Also check if we have any for today; if none, trigger background fetch once per day
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time()).isoformat()
        today_end = datetime.combine(today, datetime.max.time()).isoformat()
        today_count = supabase.table('articles').select('id').gte('created_at', today_start).lte('created_at', today_end).execute()
        if (not today_count.data) and PERPLEXITY_API_KEY and not PERPLEXITY_API_KEY.startswith('your_'):
            _auto_fetch_if_needed_async()
            flash('Fetching fresh articles for today in the background. Please refresh in ~10-20 seconds.', 'info')

        # Get all articles (limited to 8-10)
        all_articles_result = supabase.table('articles').select('*').order('created_at', desc=True).limit(10).execute()
        all_articles = all_articles_result.data or []

        # Get categories that have articles
        all_articles_combined = recent_articles + older_recent_articles + all_articles
        categories_with_articles = []
        if all_articles_combined:
            article_categories = set(article['category'] for article in all_articles_combined)
            categories_with_articles = [cat for cat in NEWS_CATEGORIES if cat in article_categories]
        
        # Create personalized "For You" articles (mix of recent and popular categories)
        for_you_articles = all_articles[:4] if all_articles else []
        
        # Get continue reading articles (simulate user reading history)
        # In a real app, this would come from user_draws table with read progress
        continue_reading_articles = []
        if all_articles:
            # Simulate some articles with reading progress
            for i, article in enumerate(all_articles[:2]):
                article_copy = article.copy()
                article_copy['read_progress'] = [65, 30][i] if i < 2 else 0
                article_copy['last_read_time'] = ['2 hours ago', '1 day ago'][i] if i < 2 else '3 days ago'
                continue_reading_articles.append(article_copy)
        
        return render_template('index_modern.html', 
                             today_articles=recent_articles,
                             older_recent_articles=older_recent_articles,
                             all_articles=all_articles,
                             for_you_articles=for_you_articles,
                             continue_reading_articles=continue_reading_articles,
                             categories=NEWS_CATEGORIES,
                             categories_with_articles=categories_with_articles,
                             get_category_icon=get_category_icon,
                             format_date=format_date,
                             current_category='All',
                             page_title='Latest News',
                             current_date=datetime.now().strftime('%B %d, %Y'))
    except Exception as e:
        # Show sample articles when there's an error
        sample_articles = [
            {
                'id': 1,
                'headline': 'New AI Tools Help Students Study Smarter, Not Harder',
                'content': 'Students are discovering how artificial intelligence can revolutionize their study habits. From personalized learning plans to instant homework help, AI is making education more accessible and effective for teens everywhere. These tools are changing how students approach learning, making complex subjects more digestible and study sessions more efficient.',
                'category': 'Technology',
                'source': 'TechCrunch',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 2,
                'headline': 'Climate Change: What Teens Can Do to Make a Real Difference',
                'content': 'Young activists are leading the charge against climate change with innovative solutions and powerful voices. Learn about the practical steps you can take to protect our planet and inspire others to join the movement. From school strikes to social media campaigns, teens are proving that age is just a number when it comes to environmental action.',
                'category': 'Environment',
                'source': 'BBC News',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 3,
                'headline': 'Mental Health Apps That Actually Help Teens Cope',
                'content': 'New mental health resources designed specifically for teenagers are making it easier to find support and build resilience. These apps offer everything from meditation guides to crisis support, helping teens navigate the challenges of modern life with better mental health tools and resources.',
                'category': 'Health',
                'source': 'NPR',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 4,
                'headline': 'The Future of Social Media: What Teens Need to Know',
                'content': 'Social media platforms are evolving rapidly, and teens are at the forefront of these changes. From new privacy features to emerging platforms, understanding these shifts can help you navigate the digital world more safely and effectively.',
                'category': 'Technology',
                'source': 'Wired',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 5,
                'headline': 'How Gen Z is Redefining Success in the Workplace',
                'content': 'Young people are changing what it means to have a successful career, prioritizing work-life balance, mental health, and meaningful work over traditional corporate ladders. This shift is reshaping entire industries and creating new opportunities.',
                'category': 'Social Issues',
                'source': 'Forbes',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 6,
                'headline': 'The Science Behind Why Music Moves Us',
                'content': 'New research reveals how music affects our brains and emotions, especially during teenage years. Understanding these connections can help you use music more effectively for studying, relaxation, and emotional regulation.',
                'category': 'Science',
                'source': 'Scientific American',
                'created_at': datetime.now().isoformat()
            }
        ]
        
        # Create personalized "For You" articles based on sample data
        for_you_articles = sample_articles[:4]  # Top 4 articles for personalized section
        
        # Create sample "Continue Reading" articles with progress
        continue_reading_articles = [
            {
                'id': 1,
                'headline': 'New AI Tools Help Students Study Smarter, Not Harder',
                'content': 'Students are discovering how artificial intelligence can revolutionize their study habits. From personalized learning plans to instant homework help, AI is making education more accessible and effective for teens everywhere. These tools are changing how students approach learning, making complex subjects more digestible and study sessions more efficient.',
                'category': 'Technology',
                'source': 'TechCrunch',
                'created_at': datetime.now().isoformat(),
                'read_progress': 65,
                'last_read_time': '2 hours ago'
            },
            {
                'id': 2,
                'headline': 'Climate Change: What Teens Can Do to Make a Real Difference',
                'content': 'Young activists are leading the charge against climate change with innovative solutions and powerful voices. Learn about the practical steps you can take to protect our planet and inspire others to join the movement. From school strikes to social media campaigns, teens are proving that age is just a number when it comes to environmental action.',
                'category': 'Environment',
                'source': 'BBC News',
                'created_at': datetime.now().isoformat(),
                'read_progress': 30,
                'last_read_time': '1 day ago'
            }
        ]
        
        flash('Database connection in progress. Showing sample articles while we connect to your Supabase database.', 'info')
        return render_template('index_modern.html', 
                             today_articles=sample_articles[:3],
                             all_articles=sample_articles,
                             for_you_articles=for_you_articles,
                             continue_reading_articles=continue_reading_articles,
                             categories=NEWS_CATEGORIES,
                             categories_with_articles=['Technology', 'Environment', 'Health', 'Social Issues', 'Science'],
                             get_category_icon=get_category_icon,
                             format_date=format_date,
                             current_category='All',
                             page_title='Latest News',
                             current_date=datetime.now().strftime('%B %d, %Y'))

@app.route('/trending')
def trending():
    """Trending articles page - most popular and engaging content"""
    try:
        if not supabase:
            # Show sample trending articles when database is not configured
            trending_articles = [
                {
                    'id': 1,
                    'headline': 'New AI Tools Help Students Study Smarter, Not Harder',
                    'content': 'Students are discovering how artificial intelligence can revolutionize their study habits. From personalized learning plans to instant homework help, AI is making education more accessible and effective for teens everywhere. These tools are changing how students approach learning, making complex subjects more digestible and study sessions more efficient.',
                    'category': 'Technology',
                    'source': 'TechCrunch',
                    'created_at': datetime.now().isoformat(),
                    'engagement_score': 95,
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
                    'engagement_score': 92,
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
                    'engagement_score': 88,
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
                    'engagement_score': 85,
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
                    'engagement_score': 82,
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
                    'engagement_score': 79,
                    'views': 590,
                    'likes': 45
                }
            ]
            
            # Sort by engagement score (trending algorithm)
            trending_articles.sort(key=lambda x: x['engagement_score'], reverse=True)
            
            return render_template('trending.html',
                                 trending_articles=trending_articles,
                                 categories=NEWS_CATEGORIES,
                                 get_category_icon=get_category_icon,
                                 format_date=format_date,
                                 current_date=datetime.now().strftime('%B %d, %Y'))
        
        # Get trending articles from database (most viewed/recent)
        # In a real app, this would use engagement metrics, views, likes, etc.
        trending_result = supabase.table('articles').select('*').order('created_at', desc=True).limit(12).execute()
        trending_articles = trending_result.data or []
        
        # Add simulated engagement data for demo
        for i, article in enumerate(trending_articles):
            article['engagement_score'] = max(60, 95 - (i * 3))  # Decreasing engagement score
            article['views'] = max(100, 1200 - (i * 100))
            article['likes'] = max(10, 90 - (i * 8))
        
        return render_template('trending.html',
                             trending_articles=trending_articles,
                             categories=NEWS_CATEGORIES,
                             get_category_icon=get_category_icon,
                             format_date=format_date,
                             current_date=datetime.now().strftime('%B %d, %Y'))
                             
    except Exception as e:
        print(f"Error in trending route: {e}")
        # Fallback to sample data
        trending_articles = [
            {
                'id': 1,
                'headline': 'New AI Tools Help Students Study Smarter, Not Harder',
                'content': 'Students are discovering how artificial intelligence can revolutionize their study habits.',
                'category': 'Technology',
                'source': 'TechCrunch',
                'created_at': datetime.now().isoformat(),
                'engagement_score': 95,
                'views': 1250,
                'likes': 89
            }
        ]
        return render_template('trending.html',
                             trending_articles=trending_articles,
                             categories=NEWS_CATEGORIES,
                             get_category_icon=get_category_icon,
                             format_date=format_date,
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
            
        return render_template('article_improved.html', article=article)
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
    
    # Build date options for the last 30 days
    date_options = []
    today = datetime.now().date()
    for i in range(30):
        day = today - timedelta(days=i)
        date_options.append({
            'value': day.strftime('%Y-%m-%d'),
            'label': day.strftime('%b %d, %Y')
        })
    
    selected_date = request.args.get('date', '').strip()
    
    try:
        if not supabase:
            flash('Database not configured. Please set up your Supabase credentials in .env file.', 'error')
            return render_template('admin.html', 
                                 articles=[],
                                 categories=NEWS_CATEGORIES,
                                 format_date=format_date,
                                 date_options=date_options,
                                 selected_date=selected_date)
        
        # Filter by selected date if provided
        articles = []
        if selected_date:
            try:
                day = datetime.strptime(selected_date, '%Y-%m-%d').date()
                day_start = datetime.combine(day, datetime.min.time()).isoformat()
                day_end = datetime.combine(day, datetime.max.time()).isoformat()
                result = supabase.table('articles').select('*') \
                    .gte('created_at', day_start) \
                    .lte('created_at', day_end) \
                    .order('created_at', desc=True).execute()
                articles = result.data or []
            except ValueError:
                flash('Invalid date format. Please select a valid date.', 'error')
        
        if not selected_date:
            # Default: show most recent 10
            result = supabase.table('articles').select('*').order('created_at', desc=True).limit(10).execute()
            articles = result.data or []
        
        return render_template('admin.html', 
                             articles=articles,
                             categories=NEWS_CATEGORIES,
                             format_date=format_date,
                             date_options=date_options,
                             selected_date=selected_date)
    except Exception as e:
        flash(f'Error loading admin panel: {str(e)}', 'error')
        return render_template('admin.html', 
                             articles=[],
                             categories=NEWS_CATEGORIES,
                             format_date=format_date,
                             date_options=date_options,
                             selected_date=selected_date)

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
        return redirect(url_for('admin_panel'))
    
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
            
            # Check if username already exists
            result = supabase.table('users').select('id').eq('username', name).execute()
            if result.data:
                flash('Username already taken. Please choose a different username.', 'error')
                return render_template('register.html', categories=NEWS_CATEGORIES, get_category_icon=get_category_icon)
            
            # Create new user
            password_hash = generate_password_hash(password)
            user_data = {
                'username': name,
                'email': email,
                'password_hash': password_hash,
                'created_at': datetime.now().isoformat()
            }
            
            result = supabase.table('users').insert(user_data).execute()
            new_user = result.data[0]
            
            # Store user preferences (user_id + topics)
            try:
                supabase.table('user_preferences').upsert({
                    'user_id': new_user['id'],
                    'email': email,
                    'topics': topics,
                    'updated_at': datetime.now().isoformat()
                }).execute()
                flash('Account created successfully! Your interests have been saved.', 'success')
            except Exception as e:
                # If the table doesn't exist yet, show info but continue
                flash('Account created successfully! To enable personalized features, please create the user_preferences table in Supabase.', 'info')
                print(f"User preferences error: {e}")
            
            # Log in the new user
            user = User(new_user)
            login_user(user)
            
            # Send welcome email
            try:
                welcome_msg = Message("Welcome to TeenBuzz! 🎉", recipients=[email])
                welcome_msg.body = f"""Hello {name}!

Welcome to TeenBuzz! We're excited to have you join our community of teen news enthusiasts.

Here's what you can do on TeenBuzz:
• Read teen-friendly news articles
• Browse articles by category
• Stay updated with news that matters to you

Your account has been created successfully and you're now logged in.

If you have any questions or feedback, feel free to reach out to us.

Happy reading!
The Teen Buzz Team"""
                mail.send(welcome_msg)
            except Exception as e:
                # Don't fail registration if email fails
                print(f"Welcome email failed to send: {e}")
            
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
        
        # Load preferences for checkbox state
        topics = []
        try:
            pref_result = supabase.table('user_preferences').select('topics').eq('user_id', current_user.id).single().execute()
            if pref_result.data:
                topics = pref_result.data.get('topics') or []
        except Exception as e:
            # Fallback to email-based lookup
            try:
                pref_result = supabase.table('user_preferences').select('topics').eq('email', current_user.email).single().execute()
                if pref_result.data:
                    topics = pref_result.data.get('topics') or []
            except Exception:
                topics = []
            print(f"User preferences lookup error: {e}")
        return render_template('profile.html', 
                             user=current_user,
                             articles=user_articles,
                             draw_history=draw_history,
                             topics=topics)
    except Exception as e:
        flash(f'Error loading profile: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/update-preferences', methods=['POST'])
@login_required
def update_preferences():
    """Update the current user's topic preferences"""
    try:
        if not supabase:
            flash('Database not configured', 'error')
            return redirect(url_for('profile'))
        topics = request.form.getlist('topics')
        if not topics:
            flash('Please select at least one topic', 'error')
            return redirect(url_for('profile'))
        supabase.table('user_preferences').upsert({
            'user_id': current_user.id,
            'email': current_user.email,
            'topics': topics,
            'updated_at': datetime.now().isoformat()
        }).execute()
        flash('Preferences updated', 'success')
    except Exception as e:
        flash(f'Could not save preferences: {str(e)}', 'error')
    return redirect(url_for('profile'))

@app.route('/for-you')
@login_required
def for_you():
    """Personalized page showing articles matching user's interests"""
    try:
        if not supabase:
            flash('Database not configured', 'error')
            return redirect(url_for('home'))
        # Load preferences
        prefs = None
        try:
            pref_result = supabase.table('user_preferences').select('topics').eq('user_id', current_user.id).single().execute()
            prefs = pref_result.data
        except Exception as e:
            # Fallback to email-based lookup
            try:
                pref_result = supabase.table('user_preferences').select('topics').eq('email', current_user.email).single().execute()
                prefs = pref_result.data
            except Exception:
                prefs = None
            print(f"For You preferences lookup error: {e}")
        topics = (prefs and prefs.get('topics')) or []
        articles = []
        if topics:
            # Fetch recent articles in preferred categories
            result = supabase.table('articles').select('*').in_('category', topics).order('created_at', desc=True).limit(20).execute()
            articles = result.data or []
        else:
            flash('Set your interests on your profile to personalize your feed.', 'info')
        return render_template('for_you.html', 
                             topics=topics,
                             articles=articles,
                             get_category_icon=get_category_icon,
                             format_date=format_date)
    except Exception as e:
        flash(f'Error loading For You: {str(e)}', 'error')
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
            if not supabase:
                flash('Database not configured', 'error')
                return render_template('reset_password.html', token=token)

            # Verify token
            result = supabase.table('password_reset_tokens').select('user_id, expires_at').eq('token', token).single().execute()
            token_data = result.data

            if not token_data:
                flash('Password reset link is invalid.', 'error')
                return redirect(url_for('forgot_password'))
            
            # Parse the timestamp and make it timezone-aware for comparison
            from datetime import timezone
            expires_at = datetime.fromisoformat(token_data['expires_at'].replace('Z', '+00:00'))
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
    app.run(debug=True, host='0.0.0.0', port=5002) 