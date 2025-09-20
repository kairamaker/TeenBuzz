from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
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
from threading import Thread
import threading

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here-change-this-to-something-secure')

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

# News categories for teens
NEWS_CATEGORIES = [
    'Technology',
    'Entertainment',
    'Health',
    'Environment',
    'Social Issues',
    'Science',
    'Sports',
    'Politics'
]

def get_category_icon(category):
    """Get icon for category"""
    icons = {
        'Technology': 'fas fa-laptop-code',
        'Entertainment': 'fas fa-film',
        'Health': 'fas fa-heartbeat',
        'Environment': 'fas fa-leaf',
        'Social Issues': 'fas fa-users',
        'Science': 'fas fa-flask',
        'Sports': 'fas fa-football-ball',
        'Politics': 'fas fa-vote-yea'
    }
    return icons.get(category, 'fas fa-newspaper')

def format_date(date_string):
    """Format date string"""
    try:
        if isinstance(date_string, str):
            date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        else:
            date_obj = date_string
        return date_obj.strftime('%B %d, %Y')
    except:
        return 'Recent'

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
            'likes': 89,
            'tags': 'AI,artificial intelligence,education,technology,students,learning,homework,study tools,personalized learning,academic success,teenagers,digital learning,smart studying,educational technology,AI tutoring,learning apps,study habits,academic performance,student life,tech for teens'
        },
        {
            'id': 2,
            'headline': 'Climate Change: What Teens Can Do to Make a Real Difference',
            'content': 'Young activists are leading the charge against climate change with innovative solutions and powerful voices. Learn about the practical steps you can take to protect our planet and inspire others to join the movement. From school strikes to social media campaigns, teens are proving that age is just a number when it comes to environmental action.',
            'category': 'Environment',
            'source': 'BBC News',
            'created_at': datetime.now().isoformat(),
            'views': 980,
            'likes': 76,
            'tags': 'climate,environment,activism,sustainability,youth,global warming,green living,eco-friendly,renewable energy,carbon footprint,environmental justice,climate action,teen activists,earth day,conservation,recycling,green technology,environmental education,planet protection,climate solutions'
        },
        {
            'id': 3,
            'headline': 'Mental Health Apps That Actually Help Teens Cope',
            'content': 'New mental health resources designed specifically for teenagers are making it easier to find support and build resilience. These apps offer everything from meditation guides to crisis support, helping teens navigate the challenges of modern life with better mental health tools and resources.',
            'category': 'Health',
            'source': 'NPR',
            'created_at': datetime.now().isoformat(),
            'views': 850,
            'likes': 64,
            'tags': 'mental health,apps,wellness,teenagers,support,anxiety,depression,stress,meditation,mindfulness,therapy,self-care,emotional health,psychological support,teen mental health,wellness apps,mental wellness,coping strategies,emotional support,mental health awareness'
        },
        {
            'id': 4,
            'headline': 'The Future of Social Media: What Teens Need to Know',
            'content': 'Social media platforms are evolving rapidly, and teens are at the forefront of these changes. From new privacy features to emerging platforms, understanding these shifts can help you navigate the digital world more safely and effectively.',
            'category': 'Technology',
            'source': 'Wired',
            'created_at': datetime.now().isoformat(),
            'views': 720,
            'likes': 58,
            'tags': 'social media,privacy,technology,digital,platforms,Instagram,TikTok,Facebook,Twitter,digital safety,online privacy,cyberbullying,digital citizenship,internet safety,social networking,online presence,digital footprint,social media trends,teen social media,online security'
        },
        {
            'id': 5,
            'headline': 'How Gen Z is Redefining Success in the Workplace',
            'content': 'Young people are changing what it means to have a successful career, prioritizing work-life balance, mental health, and meaningful work over traditional corporate ladders. This shift is reshaping entire industries and creating new opportunities.',
            'category': 'Social Issues',
            'source': 'Forbes',
            'created_at': datetime.now().isoformat(),
            'views': 680,
            'likes': 52,
            'tags': 'career,workplace,gen z,success,work-life balance,jobs,employment,career advice,professional development,workplace culture,remote work,entrepreneurship,career goals,job market,workplace trends,career planning,professional growth,workplace diversity,career success,teen careers'
        },
        {
            'id': 6,
            'headline': 'The Science Behind Why Music Moves Us',
            'content': 'New research reveals how music affects our brains and emotions, especially during teenage years. Understanding these connections can help you use music more effectively for studying, relaxation, and emotional regulation.',
            'category': 'Science',
            'source': 'Scientific American',
            'created_at': datetime.now().isoformat(),
            'views': 590,
            'likes': 45,
            'tags': 'music,science,brain,emotions,research,neuroscience,psychology,music therapy,studying,relaxation,emotional regulation,teen brain,music psychology,neural pathways,music and learning,emotional intelligence,music research,brain development,music benefits,teen psychology'
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
                articles = [a for a in articles if query.lower() in a.get('headline', '').lower() or query.lower() in a.get('content', '').lower() or query.lower() in a.get('tags', '').lower()]
            if category:
                articles = [a for a in articles if a.get('category') == category]
                
        elif supabase:
            # Use Supabase
            flash('✅ Connected to Supabase database', 'success')
            articles = get_articles_from_db(limit=20)
            
            # Apply filters
            if query:
                articles = [a for a in articles if query.lower() in a.get('headline', '').lower() or query.lower() in a.get('content', '').lower() or query.lower() in a.get('tags', '').lower()]
            if category:
                articles = [a for a in articles if a.get('category') == category]
        else:
            # Fallback to sample data
            flash('Using sample search data while database connection is being resolved.', 'info')
            articles = get_sample_articles()
            
            # Apply filters
            if query:
                articles = [a for a in articles if query.lower() in a.get('headline', '').lower() or query.lower() in a.get('content', '').lower() or query.lower() in a.get('tags', '').lower()]
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
        if local_db:
            # Use local database
            flash(f'✅ Using local database: {get_database_status()}', 'success')
            all_articles = get_articles_from_db(limit=50)
        elif supabase:
            # Use Supabase
            flash('✅ Connected to Supabase database', 'success')
            all_articles = get_articles_from_db(limit=50)
        else:
            # Fallback to sample data
            flash('Database connection in progress. Showing sample articles while we connect to your database.', 'info')
            all_articles = get_sample_articles()
        
        return render_template('categories.html',
                             all_articles=all_articles,
                             get_category_icon=get_category_icon,
                             format_date=format_date,
                             current_date=datetime.now().strftime('%B %d, %Y'))
    
    except Exception as e:
        print(f"Error in categories route: {e}")
        # Fallback to sample data on any error
        flash('Using sample data due to an error.', 'warning')
        all_articles = get_sample_articles()
        
        return render_template('categories.html',
                             all_articles=all_articles,
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
