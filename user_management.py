#!/usr/bin/env python3
"""
User Management System for TeenBuzz
"""

from datetime import datetime
from database_manager import get_database
from auth_system_enhanced import auth_manager

class UserManager:
    def __init__(self):
        pass  # Don't store database connection to avoid threading issues
    
    def _get_db(self):
        """Get fresh database connection for each request"""
        return get_database()
    
    def get_user_profile(self, user_id):
        """Get complete user profile with preferences"""
        try:
            # Get user data
            db = self._get_db()
            user = db.select('users', where='id = ?', params=(user_id,), limit=1)
            if not user:
                return None
            
            user_data = user[0]
            
            # Get user preferences (convert user_id to string for TEXT column)
            preferences = db.select('user_preferences', where='user_id = ?', params=(str(user_id),), limit=1)
            if preferences:
                user_data['preferences'] = preferences[0]
            else:
                # Create default preferences
                user_data['preferences'] = self.create_default_preferences(user_id)
            
            # Get user statistics
            user_data['stats'] = self.get_user_stats(user_id)
            
            return user_data
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    def create_default_preferences(self, user_id):
        """Create default preferences for a user"""
        default_prefs = {
            'user_id': str(user_id),  # Ensure user_id is string
            'topics': 'technology,environment,health,science,social issues',
            'categories': 'Technology,Environment,Health,Science,Social Issues',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        try:
            pref_id = self._get_db().insert('user_preferences', default_prefs)
            default_prefs['id'] = pref_id
            return default_prefs
        except Exception as e:
            print(f"Error creating default preferences: {e}")
            return default_prefs
    
    def update_user_preferences(self, user_id, preferences_data):
        """Update user preferences"""
        try:
            print(f"🔍 Checking preferences for user_id: {user_id}")
            db = self._get_db()
            
            # Check if preferences exist
            existing = db.select('user_preferences', where='user_id = ?', params=(str(user_id),), limit=1)
            print(f"📊 Existing preferences: {existing}")
            
            preferences_data['updated_at'] = datetime.now().isoformat()
            
            if existing:
                # Update existing preferences
                print(f"🔄 Updating existing preferences")
                db.update('user_preferences', preferences_data, 'user_id = ?', (str(user_id),))
                return True, "Preferences updated successfully"
            else:
                # Create new preferences
                print(f"➕ Creating new preferences")
                preferences_data['user_id'] = str(user_id)
                preferences_data['created_at'] = datetime.now().isoformat()
                db.insert('user_preferences', preferences_data)
                return True, "Preferences created successfully"
        except Exception as e:
            print(f"❌ Error in update_user_preferences: {str(e)}")
            return False, f"Error updating preferences: {str(e)}"
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        try:
            stats = {
                'articles_read': 0,
                'articles_liked': 0,
                'comments_made': 0,
                'member_since': None,
                'last_active': None
            }
            
            # Get user data for member_since and last_active
            user = self._get_db().select('users', where='id = ?', params=(user_id,), limit=1)
            if user:
                user_data = user[0]
                stats['member_since'] = user_data.get('created_at')
                stats['last_active'] = user_data.get('last_login')
            
            # Get articles read (placeholder - would need reading history table)
            # Get articles liked (placeholder - would need likes table)
            # Get comments made (placeholder - would need comments table)
            
            return stats
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {}
    
    def update_user_profile(self, user_id, profile_data):
        """Update user profile information"""
        try:
            # Remove sensitive fields that shouldn't be updated directly
            sensitive_fields = ['id', 'password_hash', 'is_admin', 'created_at']
            for field in sensitive_fields:
                profile_data.pop(field, None)
            
            profile_data['updated_at'] = datetime.now().isoformat()
            
            self._get_db().update('users', profile_data, 'id = ?', (user_id,))
            return True, "Profile updated successfully"
        except Exception as e:
            return False, f"Error updating profile: {str(e)}"
    
    def get_user_reading_history(self, user_id, limit=10):
        """Get user's reading history"""
        try:
            reading_records = self._get_db().select('reading_history', 
                                            where='user_id = ?', 
                                            params=(str(user_id),), 
                                            limit=limit)
            
            history = []
            for record in reading_records:
                # Get article details
                article_id = record['article_id']
                articles = self._get_db().select('articles', where='id = ?', params=(article_id,), limit=1)
                
                if articles:
                    article = articles[0]
                    history.append({
                        'id': record['id'],
                        'user_id': record['user_id'],
                        'article_id': record['article_id'],
                        'progress_percentage': record['progress_percentage'],
                        'last_read_at': record['last_read_at'],
                        'created_at': record['created_at'],
                        'updated_at': record['updated_at'],
                        'headline': article['headline'],
                        'category': article['category'],
                        'source': article['source']
                    })
            
            return history
        except Exception as e:
            print(f"Error getting reading history: {e}")
            return []
    
    def get_user_bookmarks(self, user_id, limit=10):
        """Get user's bookmarked articles"""
        try:
            # This would require a bookmarks table
            # For now, return empty list
            return []
        except Exception as e:
            print(f"Error getting bookmarks: {e}")
            return []
    
    def get_recommended_articles(self, user_id, limit=5):
        """Get personalized article recommendations"""
        try:
            # Get user preferences
            preferences = self._get_db().select('user_preferences', where='user_id = ?', params=(str(user_id),), limit=1)
            
            if not preferences:
                # Return random articles if no preferences
                articles = self._get_db().select('articles', limit=limit)
                return articles
            
            pref_data = preferences[0]
            preferred_categories = pref_data.get('categories', '').split(',')
            preferred_topics = pref_data.get('topics', '').split(',')
            
            # Get articles matching user preferences
            recommended = []
            
            # First, try to get articles from preferred categories
            for category in preferred_categories:
                category = category.strip()
                if category:
                    articles = self._get_db().select('articles', where='category = ?', params=(category,), limit=2)
                    recommended.extend(articles)
            
            # If not enough articles, get articles with preferred topics in tags
            if len(recommended) < limit:
                for topic in preferred_topics:
                    topic = topic.strip()
                    if topic:
                        articles = self._get_db().select('articles', where='tags LIKE ?', params=(f'%{topic}%',), limit=2)
                        recommended.extend(articles)
            
            # Remove duplicates and limit results
            seen_ids = set()
            unique_recommended = []
            for article in recommended:
                if article['id'] not in seen_ids:
                    seen_ids.add(article['id'])
                    unique_recommended.append(article)
                    if len(unique_recommended) >= limit:
                        break
            
            return unique_recommended
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []
    
    def get_available_categories(self):
        """Get all available categories from articles"""
        try:
            categories = self._get_db().execute_query('SELECT DISTINCT category FROM articles WHERE category IS NOT NULL ORDER BY category')
            return [cat['category'] for cat in categories] if categories else []
        except Exception as e:
            print(f"Error getting categories: {e}")
            return ['Technology', 'Environment', 'Health', 'Science', 'Social Issues', 'Education', 'Entertainment', 'Gaming', 'Music', 'Sports']
    
    def get_available_topics(self):
        """Get all available topics from article tags"""
        try:
            articles = self._get_db().select('articles')
            all_topics = set()
            
            for article in articles:
                tags = article.get('tags', '').split(',')
                for tag in tags:
                    tag = tag.strip().lower()
                    if tag and len(tag) > 2:  # Filter out very short tags
                        all_topics.add(tag)
            
            return sorted(list(all_topics))
        except Exception as e:
            print(f"Error getting topics: {e}")
            return ['technology', 'environment', 'health', 'science', 'politics', 'education', 'ai', 'climate']

    def get_continue_reading_articles(self, user_id, limit=5):
        """Get articles the user has read, prioritizing incomplete ones, then showing recent completed ones"""
        try:
            # Get all reading history records for user, ordered by last_read_at (most recent first)
            reading_records = self._get_db().execute_query(
                "SELECT * FROM reading_history WHERE user_id = ? ORDER BY last_read_at DESC LIMIT ?",
                (str(user_id), limit * 2)
            )
            
            if not reading_records:
                return []
            
            # Separate incomplete and complete articles
            incomplete_articles = []
            complete_articles = []
            
            for record in reading_records:
                # Get the article data
                article_id = record['article_id']
                articles = self._get_db().select('articles', where='id = ?', params=(article_id,), limit=1)
                
                if articles:
                    article = articles[0]
                    # Add reading progress data to article
                    article['reading_progress'] = record['progress_percentage']
                    article['last_read_at'] = record['last_read_at']
                    
                    if record['progress_percentage'] < 1.0:
                        incomplete_articles.append(article)
                    else:
                        complete_articles.append(article)
            
            # Prioritize incomplete articles, then add recent complete ones
            continue_reading = incomplete_articles[:limit]
            
            # If we need more articles and have complete ones, add recent completed articles
            if len(continue_reading) < limit and complete_articles:
                remaining_slots = limit - len(continue_reading)
                continue_reading.extend(complete_articles[:remaining_slots])
            
            return continue_reading
        except Exception as e:
            print(f"Error getting continue reading articles: {e}")
            return []

    def update_reading_progress(self, user_id, article_id, progress_percentage):
        """Update or create reading progress for a user and article"""
        try:
            # Check if reading history already exists
            existing = self._get_db().select('reading_history', 
                                    where='user_id = ? AND article_id = ?', 
                                    params=(str(user_id), article_id), 
                                    limit=1)
            
            if existing:
                # Update existing record
                self._get_db().update('reading_history', 
                             {'progress_percentage': progress_percentage, 
                              'last_read_at': datetime.now().isoformat(),
                              'updated_at': datetime.now().isoformat()}, 
                             'user_id = ? AND article_id = ?', 
                             (str(user_id), article_id))
            else:
                # Create new record
                reading_data = {
                    'user_id': str(user_id),
                    'article_id': article_id,
                    'progress_percentage': progress_percentage,
                    'last_read_at': datetime.now().isoformat(),
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                self._get_db().insert('reading_history', reading_data)
            
            return True, "Reading progress updated successfully"
        except Exception as e:
            return False, f"Error updating reading progress: {str(e)}"

# Global user manager instance
user_manager = UserManager()
