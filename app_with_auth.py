#!/usr/bin/env python3
"""
TeenBuzz Flask App with Enhanced Authentication
"""

from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from database_manager import get_database, get_database_status
from datetime import datetime
from auth_system_enhanced import (
    auth_manager, login_required, admin_required, 
    get_current_user, is_authenticated, is_admin
)
from user_management import user_manager
from email_system import email_manager
from article_manager import article_manager
from comments_manager import comments_manager
import sqlite3
from datetime import datetime

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

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-this-in-production'

# Initialize database
try:
    db_instance = get_database()
    if db_instance is None:
        print("Using sample data - no database connection")
        local_db = None
    else:
        local_db = db_instance
        print(f"✅ Using local database: {get_database_status()}")
except Exception as e:
    print(f"Warning: Could not initialize database: {e}")
    local_db = None

def get_articles_from_db(limit=20):
    """Get articles from local database"""
    try:
        # Create a new database connection for each request to avoid thread issues
        db = get_database()
        if not db:
            return []
        
        articles = db.select('articles', limit=limit)
        return articles
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return []

def enhanced_search_filter(articles, query):
    """Enhanced search function that matches individual words in query and news sources"""
    if not query:
        return articles
    
    query_lower = query.lower()
    query_words = query_lower.split()
    
    # Common news source mappings for better search
    news_source_mappings = {
        'bbc': ['bbc', 'bbc news', 'bbc.com'],
        'cnn': ['cnn', 'cnn.com'],
        'reuters': ['reuters', 'reuters.com'],
        'guardian': ['guardian', 'the guardian', 'theguardian.com'],
        'wired': ['wired', 'wired.com'],
        'techcrunch': ['techcrunch', 'techcrunch.com'],
        'forbes': ['forbes', 'forbes.com'],
        'nytimes': ['new york times', 'nytimes', 'nytimes.com'],
        'washington post': ['washington post', 'wapo', 'washingtonpost.com'],
        'npr': ['npr', 'npr.org'],
        'ap': ['associated press', 'ap news', 'ap.org'],
        'bloomberg': ['bloomberg', 'bloomberg.com'],
        'wsj': ['wall street journal', 'wsj', 'wsj.com'],
        'psychology today': ['psychology today', 'psychologytoday.com'],
        'scientific american': ['scientific american', 'sciam', 'scientificamerican.com'],
        'gamespot': ['gamespot', 'gamespot.com'],
        'vogue': ['vogue', 'vogue.com'],
        'rss': ['rss feed', 'rss', 'feed']
    }
    
    def article_matches_query(article):
        headline = (article.get('headline') or '').lower()
        content = (article.get('content') or '').lower()
        tags = (article.get('tags') or '').lower()
        category = (article.get('category') or '').lower()
        source = (article.get('source') or '').lower()
        
        # Check if any query word matches in headline, content, tags, category, or source
        for word in query_words:
            if (word in headline or 
                word in content or 
                word in tags or 
                word in category or
                word in source):
                return True
        
        # Check for news source mappings
        for search_term, source_variations in news_source_mappings.items():
            if search_term in query_lower:
                for variation in source_variations:
                    if variation in source:
                        return True
        
        return False
    
    return [a for a in articles if article_matches_query(a)]

# Context processor to inject user data into all templates
@app.context_processor
def inject_user():
    """Inject user variables into all templates"""
    return {
        'current_user': get_current_user(),
        'is_authenticated': is_authenticated(),
        'is_admin': is_admin()
    }

@app.route('/')
def home():
    """Home page"""
    try:
        # Get articles based on user authentication and interests
        if is_authenticated():
            user_id = session.get('user_id')
            
            # Fix for users with None user_id - get from username
            if not user_id and session.get('username'):
                user = get_database().select('users', where='username = ?', params=(session['username'],), limit=1)
                if user and user[0]['id']:
                    user_id = user[0]['id']
                    session['user_id'] = user_id  # Fix the session
                    print(f"🔧 Fixed user_id in session: {user_id}")
            
            if user_id:
                # Get personalized articles based on user interests
                articles = user_manager.get_recommended_articles(user_id, limit=10)
                print(f"🎯 Found {len(articles)} personalized articles for user {user_id}")
                
                # Get continue reading articles
                continue_reading = user_manager.get_continue_reading_articles(user_id, limit=5)
                print(f"📖 Found {len(continue_reading)} continue reading articles for user {user_id}")
            else:
                # Fallback to general articles
                articles = get_articles_from_db(limit=10)
                continue_reading = []
                print(f"🔍 No valid user_id found, using fallback")
        else:
            # For non-authenticated users, show general articles
            articles = get_articles_from_db(limit=10)
            continue_reading = []
            print(f"📰 Found {len(articles)} general articles for non-authenticated user")
        
        
        return render_template('index_modern.html', 
                             articles=articles, 
                             continue_reading=continue_reading,
                             format_date=format_date)
    except Exception as e:
        print(f"Error in home route: {e}")
        return render_template('index_modern.html', articles=[], continue_reading=[])

@app.route('/search')
def search_articles():
    """Search articles page"""
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    try:
        # Always try to get articles from database
        articles = get_articles_from_db(limit=20)
        print(f"DEBUG: Found {len(articles)} articles from database")
        
        # Apply filters with enhanced search
        if query:
            print(f"DEBUG: Searching for '{query}' in {len(articles)} articles")
            print(f"DEBUG: First article structure: {articles[0] if articles else 'No articles'}")
            articles = enhanced_search_filter(articles, query)
            print(f"DEBUG: After search filter: {len(articles)} articles")
            if articles:
                print(f"DEBUG: First filtered article: {articles[0]}")
        if category:
            articles = [a for a in articles if a.get('category') == category]
        
        return render_template('search.html', 
                             articles=articles, 
                             query=query, 
                             category=category,
                             total_results=len(articles),
                             format_date=format_date)
    except Exception as e:
        print(f"Error in search route: {e}")
        return render_template('search.html', articles=[], query=query, category=category, format_date=format_date)

# Trending page removed - feature for future release

# Duplicate bookmarks route removed

@app.route('/categories')
def categories():
    """Categories page"""
    try:
        db = get_database()
        if not db:
            return render_template('categories.html', categories=[])
        
        # Get all unique categories
        category_results = db.execute_query('SELECT DISTINCT category FROM articles WHERE category IS NOT NULL')
        
        categories = []
        for row in category_results:
            category_name = row['category']
            
            # Get articles for this category
            category_articles = db.select('articles', where='category = ?', params=(category_name,), limit=10)
            
            # Calculate stats
            total_views = sum(article.get('views', 0) for article in category_articles)
            total_likes = sum(article.get('likes', 0) for article in category_articles)
            
            # Get recent articles (last 3)
            recent_articles = sorted(category_articles, key=lambda x: x.get('created_at', ''), reverse=True)[:3]
            
            category_data = {
                'name': category_name,
                'article_count': len(category_articles),
                'views': total_views,
                'likes': total_likes,
                'recent_articles': recent_articles
            }
            categories.append(category_data)
        
        # Sort categories by article count (most articles first)
        categories.sort(key=lambda x: x['article_count'], reverse=True)
        
        # Check if user wants to filter by specific category
        selected_category = request.args.get('category', '')
        filtered_articles = []
        
        if selected_category:
            # Get articles for the selected category
            filtered_articles = db.select('articles', where='category = ?', params=(selected_category,), limit=20)
            print(f"🔍 Filtering by category: {selected_category} - Found {len(filtered_articles)} articles")
        
        print(f"📂 Loaded {len(categories)} categories for categories page")
        print(f"🔍 Categories data: {[cat['name'] for cat in categories]}")
        
        # Debug: Check if categories is empty
        if not categories:
            print("⚠️ No categories found - this might be the issue")
            # Try to get some basic category data
            all_articles = db.select('articles', limit=10)
            print(f"📰 Found {len(all_articles)} total articles")
            if all_articles:
                print(f"📰 Sample article categories: {[a.get('category', 'None') for a in all_articles[:5]]}")
        
        return render_template('categories_simple.html', 
                             categories=categories, 
                             selected_category=selected_category,
                             filtered_articles=filtered_articles)
        
    except Exception as e:
        print(f"Error in categories route: {e}")
        return render_template('categories.html', categories=[])

@app.route('/article-management')
@admin_required
def article_management():
    """Article management page for admins"""
    return render_template('article_management.html')

@app.route('/create-article', methods=['GET', 'POST'])
@admin_required
def create_article():
    """Create a new article"""
    if request.method == 'POST':
        headline = request.form.get('headline', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', '').strip()
        tags = request.form.get('tags', '').strip()
        source = request.form.get('source', 'TeenBuzz').strip()
        url = request.form.get('url', '').strip()
        
        success, message = article_manager.create_article(
            headline=headline,
            content=content,
            category=category,
            tags=tags,
            source=source,
            url=url
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('article_management'))
        else:
            flash(message, 'error')
    
    return render_template('article_editor.html')

@app.route('/edit-article/<int:article_id>', methods=['GET', 'POST'])
@admin_required
def edit_article(article_id):
    """Edit an existing article"""
    article, message = article_manager.get_article(article_id)
    
    if not article:
        flash(message, 'error')
        return redirect(url_for('article_management'))
    
    if request.method == 'POST':
        headline = request.form.get('headline', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', '').strip()
        tags = request.form.get('tags', '').strip()
        source = request.form.get('source', '').strip()
        url = request.form.get('url', '').strip()
        
        success, message = article_manager.update_article(
            article_id,
            headline=headline,
            content=content,
            category=category,
            tags=tags,
            source=source,
            url=url
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('article_management'))
        else:
            flash(message, 'error')
    
    return render_template('article_editor.html', article=article)

@app.route('/delete-article/<int:article_id>')
@admin_required
def delete_article(article_id):
    """Delete an article"""
    success, message = article_manager.delete_article(article_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('article_management'))

@app.route('/like-article/<int:article_id>', methods=['POST'])
@login_required
def like_article(article_id):
    """Toggle like for an article"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not authenticated"}), 401
        
        success, message = article_manager.toggle_like(article_id, user['id'])
        
        if success:
            # Get updated like count
            article, _ = article_manager.get_article(article_id)
            like_count = article['likes'] if article else 0
            
            return jsonify({
                "success": True,
                "message": message,
                "like_count": like_count
            })
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Bookmark functionality removed - not needed

# Comment functionality removed - not needed

# All comment functionality removed - not needed

# Like comment functionality removed - not needed

# Bookmarks route removed - not needed

# Comments route removed - not needed

@app.route('/article/<int:article_id>')
def view_article(article_id):
    """View individual article"""
    try:
        print(f"🔍 Attempting to view article {article_id}")
        
        # Create a new database connection for each request to avoid thread issues
        db = get_database()
        if db:
            print("✅ Database connection successful")
            articles = db.select('articles', where='id = ?', params=(article_id,), limit=1)
            print(f"✅ Found {len(articles)} articles")
            
            if articles:
                article = articles[0]
                print(f"✅ Article found: {article['headline'][:50]}...")
                
                # Track reading progress if user is authenticated
                if is_authenticated():
                    user_id = session.get('user_id')
                    if user_id:
                        # For now, we'll set progress to 50% when user views an article
                        # In a real implementation, this would be based on scroll position
                        user_manager.update_reading_progress(user_id, article_id, 0.5)
                        print(f"📖 Updated reading progress for user {user_id}, article {article_id}")
                
                # Get comments for this article
                comments, _ = comments_manager.get_comments(article_id)
                
                # Get related articles (same category, excluding current article)
                related_articles = db.select('articles', 
                                           where='category = ? AND id != ?', 
                                           params=(article['category'], article_id), 
                                           limit=6)
                
                print("✅ About to render template")
                return render_template('article_simple.html', 
                                     article=article, 
                                     format_date=format_date)
            else:
                print("❌ No article found")
                flash('Article not found', 'error')
                return redirect(url_for('home'))
        else:
            print("❌ Database connection failed")
            return redirect(url_for('home'))
    except Exception as e:
        print(f"❌ Error viewing article: {e}")
        import traceback
        traceback.print_exc()
        flash('Article not found', 'error')
        return redirect(url_for('home'))

@app.route('/update-reading-progress', methods=['POST'])
@login_required
def update_reading_progress():
    """Update reading progress for an article"""
    try:
        data = request.get_json()
        article_id = data.get('article_id')
        progress = data.get('progress', 0.5)  # Default to 50%
        
        user_id = session.get('user_id')
        if not user_id or not article_id:
            return {'success': False, 'message': 'Invalid request'}
        
        success, message = user_manager.update_reading_progress(user_id, article_id, progress)
        
        return {'success': success, 'message': message}
    except Exception as e:
        print(f"Error updating reading progress: {e}")
        return {'success': False, 'message': 'Error updating progress'}

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        if not username or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('login.html')
        
        success, message = auth_manager.login_user(username, password, remember_me)
        
        if success:
            flash(message, 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            flash(message, 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not all([username, email, password, confirm_password]):
            flash('Please fill in all fields.', 'error')
            return render_template('register.html', 
                                 username=username, 
                                 email=email)
        
        success, message = auth_manager.register_user(username, email, password, confirm_password)
        
        if success:
            # Store registration data in session for category selection
            session['new_user'] = {
                'username': username,
                'email': email,
                'user_id': message.split(': ')[-1] if ': ' in message else None
            }
            flash(message, 'success')
            return redirect(url_for('select_categories'))
        else:
            # If password mismatch, only reset password fields
            if 'Passwords do not match' in message:
                return render_template('register.html', 
                                     username=username, 
                                     email=email,
                                     password_error=message)
            else:
                flash(message, 'error')
                return render_template('register.html', 
                                     username=username, 
                                     email=email)
    
    return render_template('register.html')

@app.route('/select-categories', methods=['GET', 'POST'])
def select_categories():
    """Category selection page for new users"""
    if 'new_user' not in session:
        flash('Please complete registration first.', 'error')
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        selected_categories = request.form.getlist('categories')
        
        if not selected_categories:
            flash('Please select at least one category.', 'error')
            return render_template('select_categories.html')
        
        # Save user preferences
        user_id = session['new_user']['user_id']
        if user_id:
            try:
                db = get_database()
                if db:
                    # Save user preferences as a comma-separated string
                    categories_str = ','.join(selected_categories)
                    preference_data = {
                        'user_id': user_id,
                        'categories': categories_str,
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    # Check if user already has preferences
                    existing = db.select('user_preferences', where='user_id = ?', params=(user_id,), limit=1)
                    if existing:
                        # Update existing preferences
                        db.update('user_preferences', 
                                {'categories': categories_str, 'updated_at': datetime.now().isoformat()}, 
                                'user_id = ?', (user_id,))
                    else:
                        # Insert new preferences
                        db.insert('user_preferences', preference_data)
                    
                    # Log the user in
                    session['user_id'] = user_id
                    session['username'] = session['new_user']['username']
                    session['email'] = session['new_user']['email']
                    session['is_admin'] = False
                    session['is_authenticated'] = True
                    
                    # Clear new_user data
                    session.pop('new_user', None)
                    
                    flash('Welcome to TeenBuzz! Your preferences have been saved.', 'success')
                    return redirect(url_for('user_profile'))
            except Exception as e:
                flash(f'Error saving preferences: {str(e)}', 'error')
                return render_template('select_categories.html')
    
    # Get available categories from database, with fallback to comprehensive list
    try:
        db = get_database()
        if db:
            categories = db.select('articles', columns=['DISTINCT category'], where='category IS NOT NULL')
            db_categories = [cat['category'] for cat in categories if cat['category']]
        else:
            db_categories = []
    except:
        db_categories = []
    
    # Comprehensive list of interest categories
    comprehensive_categories = [
        'Technology', 'Environment', 'Health & Wellness', 'Science', 'Social Issues',
        'Education', 'Entertainment', 'Sports', 'Music', 'Art & Design',
        'Fashion & Beauty', 'Food & Cooking', 'Travel', 'Gaming', 'Books & Literature',
        'Movies & TV', 'Photography', 'Fitness', 'Mental Health', 'Career & Future',
        'Relationships', 'Lifestyle', 'DIY & Crafts', 'Nature', 'Space & Astronomy',
        'History', 'Politics', 'Current Events', 'Innovation', 'Creativity'
    ]
    
    # Combine database categories with comprehensive list, removing duplicates
    category_list = list(set(db_categories + comprehensive_categories))
    category_list.sort()  # Sort alphabetically for better UX
    
    return render_template('select_categories.html', categories=category_list)

@app.route('/api/check-username', methods=['POST'])
def check_username():
    """Check if username is available and return suggestions if taken"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return {'available': False, 'message': 'Username is required'}
        
        # Check if username exists
        db = get_database()
        if not db:
            return {'available': False, 'message': 'Database connection error'}
        
        existing_user = db.select('users', where='username = ?', params=(username,), limit=1)
        
        if existing_user:
            # Generate suggestions
            suggestions = auth_manager.generate_username_suggestions(username)
            return {
                'available': False, 
                'message': f'Username "{username}" is already taken',
                'suggestions': suggestions
            }
        else:
            return {'available': True, 'message': 'Username is available'}
    
    except Exception as e:
        return {'available': False, 'message': f'Error checking username: {str(e)}'}

@app.route('/api/check-email', methods=['POST'])
def check_email():
    """Check if email is available"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return {'available': False, 'message': 'Email is required'}
        
        # Check if email exists
        db = get_database()
        if not db:
            return {'available': False, 'message': 'Database connection error'}
        
        existing_email = db.select('users', where='email = ?', params=(email,), limit=1)
        
        if existing_email:
            return {'available': False, 'message': f'Email "{email}" is already registered'}
        else:
            return {'available': True, 'message': 'Email is available'}
    
    except Exception as e:
        return {'available': False, 'message': f'Error checking email: {str(e)}'}

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    success, message = auth_manager.logout_user()
    flash(message, 'success')
    return redirect(url_for('home'))


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password page"""
    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not all([old_password, new_password, confirm_password]):
            flash('Please fill in all fields.', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return render_template('change_password.html')
        
        user = get_current_user()
        success, message = auth_manager.change_password(user['id'], old_password, new_password)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('user_profile'))
        else:
            flash(message, 'error')
    
    return render_template('change_password.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page"""
    error_message = None
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            error_message = 'Please enter your email address.'
            return render_template('forgot_password.html', error_message=error_message)
        
        # First check if email exists in database
        db = get_database()
        if not db:
            error_message = 'Database connection error. Please try again later.'
            return render_template('forgot_password.html', error_message=error_message)
        
        user = db.select('users', where='email = ?', params=(email,), limit=1)
        if not user:
            error_message = 'Email not registered on the app. Please check your email address or register for a new account.'
            return render_template('forgot_password.html', error_message=error_message)
        
        # Email exists, proceed with password reset
        import secrets
        from datetime import datetime, timedelta
        
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)
        
        # Store token in database
        token_data = {
            'user_id': user[0]['id'],
            'token': token,
            'expires_at': expires_at.isoformat(),
            'created_at': datetime.now().isoformat()
        }
        
        try:
            db.insert('password_reset_tokens', token_data)
            username = user[0]['username']
            
            # Try to send email first
            if email_manager.is_configured():
                success, message = email_manager.send_password_reset_email(email, token, username)
                if success:
                    flash('Password reset email sent! Check your inbox and follow the instructions.', 'success')
                else:
                    flash(f'Email could not be sent: {message}', 'error')
                    # Fallback to showing link
                    reset_url = f"http://localhost:5003/reset-password/{token}"
                    return render_template('password_reset_link.html', 
                                         username=username, 
                                         reset_url=reset_url)
            else:
                # Email not configured, show link page
                reset_url = f"http://localhost:5003/reset-password/{token}"
                return render_template('password_reset_link.html', 
                                     username=username, 
                                     reset_url=reset_url)
            
            return redirect(url_for('login'))
        except Exception as e:
            error_message = f'Error generating reset token: {str(e)}'
            return render_template('forgot_password.html', error_message=error_message)
    
    return render_template('forgot_password.html', error_message=error_message)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password page"""
    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not all([new_password, confirm_password]):
            flash('Please fill in all fields.', 'error')
            return render_template('reset_password.html', token=token)
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token)
        
        success, message = auth_manager.reset_password(token, new_password)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'error')
    
    return render_template('reset_password.html', token=token)

# Admin Routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    return render_template('admin_dashboard.html')

@app.route('/admin/users')
@admin_required
def admin_users():
    """Admin users management"""
    try:
        users = local_db.select('users') if local_db else []
        return render_template('admin_users.html', users=users)
    except Exception as e:
        flash(f'Error loading users: {str(e)}', 'error')
        return render_template('admin_users.html', users=[])

# Enhanced User Management Routes

@app.route('/profile')
@app.route('/user-profile')
@login_required
def user_profile():
    """Simplified user profile page"""
    try:
        user = get_current_user()
        
        # Simple profile data without complex queries
        user_profile = {
            'id': user['id'],
            'username': user['username'],
            'email': user.get('email', ''),
            'created_at': user.get('created_at', ''),
            'stats': {
                'articles_read': 0,
                'articles_liked': 0,
                'comments_made': 0
            }
        }
        
        return render_template('profile_enhanced.html',
                             user_stats=user_profile['stats'],
                             user_preferences={'categories': [], 'topics': []},
                             recommended_articles=[],
                             available_categories=[],
                             available_topics=[])
    except Exception as e:
        print(f"Error in user_profile route: {e}")
        return redirect(url_for('home'))

# Preferences route removed - simplified app
"""
@app.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    \"\"\"New preferences page\"\"\"
    if request.method == 'GET':
        try:
            print("🔍 Loading preferences page...")
            user = get_current_user()
            print(f"👤 User: {user['username']}")
            
            # Get user preferences
            user_profile = user_manager.get_user_profile(user['id'])
            print(f"📊 User profile: {user_profile is not None}")
            
            preferences = user_profile.get('preferences', {}) if user_profile else {}
            print(f"⚙️ Raw preferences: {preferences}")
            
            # Convert comma-separated strings to lists for template
            if preferences:
                if 'categories' in preferences and preferences['categories']:
                    preferences['categories'] = [cat.strip() for cat in preferences['categories'].split(',')]
                else:
                    preferences['categories'] = []
                
                if 'topics' in preferences and preferences['topics']:
                    preferences['topics'] = [topic.strip() for topic in preferences['topics'].split(',')]
                else:
                    preferences['topics'] = []
            
            print(f"✅ Processed preferences: {preferences}")
            
            # Get available categories and topics
            available_categories = user_manager.get_available_categories()
            available_topics = user_manager.get_available_topics()
            
            print(f"📋 Available categories: {len(available_categories)}")
            print(f"📋 Available topics: {len(available_topics)}")
            
            return render_template('preferences_modern.html',
                                 user_preferences=preferences,
                                 available_categories=available_categories,
                                 available_topics=available_topics)
        except Exception as e:
            print(f"❌ Error loading preferences: {str(e)}")
            import traceback
            traceback.print_exc()
            flash(f'Error loading preferences: {str(e)}', 'error')
            return redirect(url_for('user_profile'))
    
    else:  # POST request
        return update_preferences()
"""

# Preferences routes removed - simplified app
# All preferences functionality has been removed for simplicity

@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information"""
    try:
        user = get_current_user()
        
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        
        if not username or not email:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('user_profile') + '?tab=settings')
        
        # Validate email format
        valid, msg = auth_manager.validate_email(email)
        if not valid:
            flash(msg, 'error')
            return redirect(url_for('user_profile') + '?tab=settings')
        
        # Validate username
        valid, msg = auth_manager.validate_username(username)
        if not valid:
            flash(msg, 'error')
            return redirect(url_for('user_profile') + '?tab=settings')
        
        # Check if username/email already exists (excluding current user)
        existing_user = local_db.select('users', where='username = ? AND id != ?', params=(username, user['id']), limit=1)
        if existing_user:
            flash('Username already exists', 'error')
            return redirect(url_for('user_profile') + '?tab=settings')
        
        existing_email = local_db.select('users', where='email = ? AND id != ?', params=(email, user['id']), limit=1)
        if existing_email:
            flash('Email already exists', 'error')
            return redirect(url_for('user_profile') + '?tab=settings')
        
        # Update profile
        profile_data = {
            'username': username,
            'email': email
        }
        
        success, message = user_manager.update_user_profile(user['id'], profile_data)
        
        if success:
            # Update session
            session['username'] = username
            session['email'] = email
            flash(message, 'success')
        else:
            flash(message, 'error')
        
        return redirect(url_for('user_profile') + '?tab=settings')
    except Exception as e:
        flash(f'Error updating profile: {str(e)}', 'error')
        return redirect(url_for('user_profile'))

# API Routes for Article Management
@app.route('/api/articles', methods=['GET'])
def api_get_articles():
    """Get articles with optional filtering"""
    try:
        db = get_database()
        if not db:
            return jsonify({"error": "Database connection failed"}), 500
        
        # Get query parameters
        category = request.args.get('category')
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        if category:
            articles = db.select('articles', 
                               where='category = ?', 
                               params=(category,), 
                               limit=limit)
        else:
            articles = db.select('articles', limit=limit)
        
        return jsonify({
            "success": True,
            "articles": articles,
            "count": len(articles)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles/stats', methods=['GET'])
def api_get_article_stats():
    """Get article statistics"""
    try:
        db = get_database()
        if not db:
            return jsonify({"error": "Database connection failed"}), 500
        
        # Get total articles
        total_articles = db.execute_query("SELECT COUNT(*) as count FROM articles")[0]['count']
        
        # Get articles by category
        category_stats = db.execute_query("""
            SELECT category, COUNT(*) as count 
            FROM articles 
            WHERE category IS NOT NULL 
            GROUP BY category 
            ORDER BY count DESC
        """)
        
        # Get recent articles (last 24 hours)
        from datetime import timedelta
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        recent_articles = db.execute_query("""
            SELECT COUNT(*) as count 
            FROM articles 
            WHERE created_at > ?
        """, (yesterday,))[0]['count']
        
        return jsonify({
            "success": True,
            "stats": {
                "total_articles": total_articles,
                "recent_articles_24h": recent_articles,
                "categories": category_stats
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles/fetch', methods=['POST'])
def api_fetch_new_articles():
    """Manually trigger article fetching"""
    try:
        from advanced_article_fetcher import fetch_real_articles, add_articles_to_database
        
        # Fetch articles
        articles = fetch_real_articles()
        
        if articles:
            # Add to database
            success = add_articles_to_database(articles)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": f"Successfully fetched and added {len(articles)} articles",
                    "count": len(articles)
                })
            else:
                return jsonify({"error": "Failed to add articles to database"}), 500
        else:
            return jsonify({"error": "No articles fetched"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003)
