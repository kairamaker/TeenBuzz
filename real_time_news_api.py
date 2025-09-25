#!/usr/bin/env python3
"""
Real-Time News API for TeenBuzz
Provides API endpoints for fetching and managing articles
"""

from flask import Flask, jsonify, request
from database_manager import get_database
import json
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/api/articles', methods=['GET'])
def get_articles():
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
                               limit=limit,
                               offset=offset)
        else:
            articles = db.select('articles', limit=limit, offset=offset)
        
        return jsonify({
            "success": True,
            "articles": articles,
            "count": len(articles)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """Get a specific article by ID"""
    try:
        db = get_database()
        if not db:
            return jsonify({"error": "Database connection failed"}), 500
        
        articles = db.select('articles', where='id = ?', params=(article_id,), limit=1)
        
        if not articles:
            return jsonify({"error": "Article not found"}), 404
        
        return jsonify({
            "success": True,
            "article": articles[0]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles/search', methods=['GET'])
def search_articles():
    """Search articles by keyword"""
    try:
        db = get_database()
        if not db:
            return jsonify({"error": "Database connection failed"}), 500
        
        query = request.args.get('q', '')
        if not query:
            return jsonify({"error": "Search query required"}), 400
        
        # Search in headline, content, and tags
        search_query = f"""
        SELECT * FROM articles 
        WHERE headline LIKE ? 
        OR content LIKE ? 
        OR tags LIKE ?
        ORDER BY created_at DESC
        LIMIT 20
        """
        
        search_term = f"%{query}%"
        articles = db.execute_query(search_query, (search_term, search_term, search_term))
        
        return jsonify({
            "success": True,
            "articles": articles,
            "query": query,
            "count": len(articles)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles/categories', methods=['GET'])
def get_categories():
    """Get all available categories"""
    try:
        db = get_database()
        if not db:
            return jsonify({"error": "Database connection failed"}), 500
        
        categories = db.execute_query("SELECT DISTINCT category FROM articles WHERE category IS NOT NULL")
        
        return jsonify({
            "success": True,
            "categories": [cat['category'] for cat in categories]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles/trending', methods=['GET'])
def get_trending_articles():
    """Get trending articles based on views and likes"""
    try:
        db = get_database()
        if not db:
            return jsonify({"error": "Database connection failed"}), 500
        
        # Get articles from the last 7 days, ordered by engagement
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        trending_query = """
        SELECT *, (views + likes * 2) as engagement_score
        FROM articles 
        WHERE created_at > ?
        ORDER BY engagement_score DESC
        LIMIT 10
        """
        
        articles = db.execute_query(trending_query, (seven_days_ago,))
        
        return jsonify({
            "success": True,
            "articles": articles,
            "count": len(articles)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles/fetch', methods=['POST'])
def fetch_new_articles():
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

@app.route('/api/articles/stats', methods=['GET'])
def get_article_stats():
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

if __name__ == "__main__":
    print("🚀 Starting TeenBuzz News API...")
    print("📡 Available endpoints:")
    print("  GET  /api/articles - Get all articles")
    print("  GET  /api/articles/<id> - Get specific article")
    print("  GET  /api/articles/search?q=query - Search articles")
    print("  GET  /api/articles/categories - Get categories")
    print("  GET  /api/articles/trending - Get trending articles")
    print("  POST /api/articles/fetch - Fetch new articles")
    print("  GET  /api/articles/stats - Get statistics")
    
    app.run(debug=True, port=5004)

