#!/usr/bin/env python3
"""
Simple TeenBuzz Flask App with Enhanced Search
"""

from flask import Flask, render_template, request, flash, redirect, url_for
from database_manager import get_database, get_database_status
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
app.secret_key = 'your-secret-key-here'

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
    """Enhanced search function that matches individual words in query"""
    if not query:
        return articles
    
    query_lower = query.lower()
    query_words = query_lower.split()
    
    def article_matches_query(article):
        headline = article.get('headline', '').lower()
        content = article.get('content', '').lower()
        tags = article.get('tags', '').lower()
        category = article.get('category', '').lower()
        
        # Check if any query word matches in headline, content, tags, or category
        for word in query_words:
            if (word in headline or 
                word in content or 
                word in tags or 
                word in category):
                return True
        return False
    
    return [a for a in articles if article_matches_query(a)]

@app.context_processor
def inject_user():
    """Inject user variables into all templates"""
    return {
        'current_user': None,
        'is_authenticated': False,
        'is_admin': False
    }

@app.route('/')
def home():
    """Home page"""
    try:
        articles = get_articles_from_db(limit=10)
        flash(f'✅ Using local database: {get_database_status()}', 'success')
        
        return render_template('index_modern.html', articles=articles)
    except Exception as e:
        print(f"Error in home route: {e}")
        return render_template('index_modern.html', articles=[])

@app.route('/search')
def search_articles():
    """Search articles page"""
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    try:
        # Always try to get articles from database
        articles = get_articles_from_db(limit=20)
        print(f"DEBUG: Found {len(articles)} articles from database")
        flash(f'✅ Using local database: {get_database_status()}', 'success')
        
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

@app.route('/categories')
def categories():
    """Categories page"""
    try:
        if local_db:
            articles = get_articles_from_db(limit=20)
            flash(f'✅ Using local database: {get_database_status()}', 'success')
        else:
            articles = []
            flash('Using sample data while database connection is being resolved.', 'info')
        
        return render_template('categories.html', articles=articles)
    except Exception as e:
        print(f"Error in categories route: {e}")
        return render_template('categories.html', articles=[])

@app.route('/trending')
def trending():
    """Trending page"""
    try:
        if local_db:
            articles = get_articles_from_db(limit=20)
            flash(f'✅ Using local database: {get_database_status()}', 'success')
        else:
            articles = []
            flash('Using sample data while database connection is being resolved.', 'info')
        
        return render_template('trending.html', articles=articles)
    except Exception as e:
        print(f"Error in trending route: {e}")
        return render_template('trending.html', articles=[])

@app.route('/article/<int:article_id>')
def view_article(article_id):
    """View individual article"""
    try:
        if local_db:
            articles = local_db.select('articles', where={'id': article_id}, limit=1)
            if articles:
                article = articles[0]
                flash(f'✅ Using local database: {get_database_status()}', 'success')
            else:
                flash('Article not found', 'error')
                return redirect(url_for('home'))
        else:
            flash('Using sample data while database connection is being resolved.', 'info')
            return redirect(url_for('home'))
        
        return render_template('article_improved.html', article=article)
    except Exception as e:
        print(f"Error viewing article: {e}")
        flash('Article not found', 'error')
        return redirect(url_for('home'))

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/register')
def register():
    """Register page"""
    return render_template('register.html')

@app.route('/profile')
def profile():
    """Profile page"""
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
