#!/usr/bin/env python3
"""
Article Manager for TeenBuzz
Handles all article CRUD operations
"""

from database_manager import get_database
from datetime import datetime
import re

class ArticleManager:
    def __init__(self):
        self.db = get_database()
    
    def create_article(self, headline, content, category, tags="", source="Manual", url=""):
        """Create a new article"""
        try:
            if not self.db:
                return False, "Database connection failed"
            
            # Validate required fields
            if not headline or not content or not category:
                return False, "Headline, content, and category are required"
            
            # Clean and prepare data
            article_data = {
                'headline': headline.strip(),
                'content': content.strip(),
                'category': category.strip(),
                'tags': tags.strip(),
                'source': source.strip(),
                'url': url.strip(),
                'views': 0,
                'likes': 0,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Insert article
            article_id = self.db.insert('articles', article_data)
            
            return True, f"Article created successfully with ID: {article_id}"
            
        except Exception as e:
            return False, f"Error creating article: {str(e)}"
    
    def get_article(self, article_id):
        """Get a specific article by ID"""
        try:
            if not self.db:
                return None, "Database connection failed"
            
            articles = self.db.select('articles', where='id = ?', params=(article_id,), limit=1)
            
            if articles:
                return articles[0], "Article found"
            else:
                return None, "Article not found"
                
        except Exception as e:
            return None, f"Error retrieving article: {str(e)}"
    
    def update_article(self, article_id, **kwargs):
        """Update an existing article"""
        try:
            if not self.db:
                return False, "Database connection failed"
            
            # Check if article exists
            existing = self.db.select('articles', where='id = ?', params=(article_id,), limit=1)
            if not existing:
                return False, "Article not found"
            
            # Prepare update data
            update_data = {}
            allowed_fields = ['headline', 'content', 'category', 'tags', 'source', 'url']
            
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    update_data[field] = str(value).strip()
            
            if not update_data:
                return False, "No valid fields to update"
            
            # Add update timestamp
            update_data['updated_at'] = datetime.now().isoformat()
            
            # Update article
            self.db.update('articles', update_data, 'id = ?', (article_id,))
            
            return True, "Article updated successfully"
            
        except Exception as e:
            return False, f"Error updating article: {str(e)}"
    
    def delete_article(self, article_id):
        """Delete an article"""
        try:
            if not self.db:
                return False, "Database connection failed"
            
            # Check if article exists
            existing = self.db.select('articles', where='id = ?', params=(article_id,), limit=1)
            if not existing:
                return False, "Article not found"
            
            # Delete article
            self.db.execute_query("DELETE FROM articles WHERE id = ?", (article_id,))
            
            return True, "Article deleted successfully"
            
        except Exception as e:
            return False, f"Error deleting article: {str(e)}"
    
    def get_articles(self, limit=20, offset=0, category=None, search=None):
        """Get articles with optional filtering"""
        try:
            if not self.db:
                return [], "Database connection failed"
            
            where_clause = ""
            params = []
            
            conditions = []
            
            if category:
                conditions.append("category = ?")
                params.append(category)
            
            if search:
                conditions.append("(headline LIKE ? OR content LIKE ? OR tags LIKE ?)")
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])
            
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)
            
            # Build query
            query = f"""
                SELECT * FROM articles 
                {where_clause}
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])
            
            articles = self.db.execute_query(query, params)
            
            return articles, "Articles retrieved successfully"
            
        except Exception as e:
            return [], f"Error retrieving articles: {str(e)}"
    
    def increment_views(self, article_id):
        """Increment article view count"""
        try:
            if not self.db:
                return False, "Database connection failed"
            
            self.db.execute_query(
                "UPDATE articles SET views = views + 1 WHERE id = ?", 
                (article_id,)
            )
            
            return True, "View count updated"
            
        except Exception as e:
            return False, f"Error updating view count: {str(e)}"
    
    def toggle_like(self, article_id, user_id):
        """Toggle like for an article by a user"""
        try:
            if not self.db:
                return False, "Database connection failed"
            
            # Check if user already liked this article
            existing = self.db.select('article_likes', 
                                    where='article_id = ? AND user_id = ?', 
                                    params=(article_id, user_id), 
                                    limit=1)
            
            if existing:
                # Unlike - remove the like
                self.db.execute_query(
                    "DELETE FROM article_likes WHERE article_id = ? AND user_id = ?",
                    (article_id, user_id)
                )
                # Decrement like count
                self.db.execute_query(
                    "UPDATE articles SET likes = likes - 1 WHERE id = ?",
                    (article_id,)
                )
                return True, "Article unliked"
            else:
                # Like - add the like
                like_data = {
                    'article_id': article_id,
                    'user_id': user_id,
                    'created_at': datetime.now().isoformat()
                }
                self.db.insert('article_likes', like_data)
                # Increment like count
                self.db.execute_query(
                    "UPDATE articles SET likes = likes + 1 WHERE id = ?",
                    (article_id,)
                )
                return True, "Article liked"
                
        except Exception as e:
            return False, f"Error toggling like: {str(e)}"
    
    def toggle_bookmark(self, article_id, user_id):
        """Toggle bookmark for an article by a user"""
        try:
            if not self.db:
                return False, "Database connection failed"
            
            # Check if user already bookmarked this article
            existing = self.db.select('article_bookmarks', 
                                    where='article_id = ? AND user_id = ?', 
                                    params=(article_id, user_id), 
                                    limit=1)
            
            if existing:
                # Remove bookmark
                self.db.execute_query(
                    "DELETE FROM article_bookmarks WHERE article_id = ? AND user_id = ?",
                    (article_id, user_id)
                )
                return True, "Article bookmark removed"
            else:
                # Add bookmark
                bookmark_data = {
                    'article_id': article_id,
                    'user_id': user_id,
                    'created_at': datetime.now().isoformat()
                }
                self.db.insert('article_bookmarks', bookmark_data)
                return True, "Article bookmarked"
                
        except Exception as e:
            return False, f"Error toggling bookmark: {str(e)}"
    
    def get_user_bookmarks(self, user_id, limit=20):
        """Get user's bookmarked articles"""
        try:
            if not self.db:
                return [], "Database connection failed"
            
            # Get bookmarked articles
            bookmarks = self.db.execute_query("""
                SELECT a.*, ab.created_at as bookmarked_at
                FROM articles a
                JOIN article_bookmarks ab ON a.id = ab.article_id
                WHERE ab.user_id = ?
                ORDER BY ab.created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            return bookmarks, "Bookmarks retrieved successfully"
            
        except Exception as e:
            return [], f"Error retrieving bookmarks: {str(e)}"
    
    def get_article_stats(self):
        """Get article statistics"""
        try:
            if not self.db:
                return None, "Database connection failed"
            
            # Total articles
            total = self.db.execute_query("SELECT COUNT(*) as count FROM articles")[0]['count']
            
            # Articles by category
            categories = self.db.execute_query("""
                SELECT category, COUNT(*) as count 
                FROM articles 
                WHERE category IS NOT NULL 
                GROUP BY category 
                ORDER BY count DESC
            """)
            
            # Recent articles (last 7 days)
            week_ago = (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - 
                       datetime.timedelta(days=7)).isoformat()
            recent = self.db.execute_query(
                "SELECT COUNT(*) as count FROM articles WHERE created_at > ?",
                (week_ago,)
            )[0]['count']
            
            # Most viewed articles
            top_articles = self.db.execute_query("""
                SELECT headline, views, likes 
                FROM articles 
                ORDER BY views DESC 
                LIMIT 5
            """)
            
            return {
                'total_articles': total,
                'recent_articles': recent,
                'categories': categories,
                'top_articles': top_articles
            }, "Stats retrieved successfully"
            
        except Exception as e:
            return None, f"Error retrieving stats: {str(e)}"

# Create global instance
article_manager = ArticleManager()
