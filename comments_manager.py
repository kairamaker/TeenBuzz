#!/usr/bin/env python3
"""
Comments Manager for TeenBuzz
Handles all comment operations
"""

from database_manager import get_database
from datetime import datetime
import re

class CommentsManager:
    def __init__(self):
        self.db = get_database()
    
    def create_comment(self, article_id, user_id, content, parent_id=None):
        """Create a new comment"""
        try:
            if not self.db:
                return False, "Database connection failed"
            
            # Validate content
            content = content.strip()
            if not content or len(content) < 3:
                return False, "Comment must be at least 3 characters long"
            
            if len(content) > 1000:
                return False, "Comment must be less than 1000 characters"
            
            # Check if article exists
            article = self.db.select('articles', where='id = ?', params=(article_id,), limit=1)
            if not article:
                return False, "Article not found"
            
            # Check if parent comment exists (for replies)
            if parent_id:
                parent = self.db.select('comments', where='id = ?', params=(parent_id,), limit=1)
                if not parent:
                    return False, "Parent comment not found"
            
            # Create comment
            comment_data = {
                'article_id': article_id,
                'user_id': user_id,
                'content': content,
                'parent_id': parent_id,
                'likes': 0,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            comment_id = self.db.insert('comments', comment_data)
            
            return True, f"Comment created successfully with ID: {comment_id}"
            
        except Exception as e:
            return False, f"Error creating comment: {str(e)}"
    
    def get_comments(self, article_id, limit=50):
        """Get comments for an article"""
        try:
            if not self.db:
                return [], "Database connection failed"
            
            # Get top-level comments (no parent)
            comments = self.db.execute_query("""
                SELECT c.*, u.username, u.email
                FROM comments c
                JOIN users u ON c.user_id = u.id
                WHERE c.article_id = ? AND c.parent_id IS NULL
                ORDER BY c.created_at DESC
                LIMIT ?
            """, (article_id, limit))
            
            # Get replies for each comment
            for comment in comments:
                replies = self.db.execute_query("""
                    SELECT c.*, u.username, u.email
                    FROM comments c
                    JOIN users u ON c.user_id = u.id
                    WHERE c.parent_id = ?
                    ORDER BY c.created_at ASC
                """, (comment['id'],))
                comment['replies'] = replies
            
            return comments, "Comments retrieved successfully"
            
        except Exception as e:
            return [], f"Error retrieving comments: {str(e)}"
    
    def update_comment(self, comment_id, user_id, content):
        """Update a comment"""
        try:
            if not self.db:
                return False, "Database connection failed"
            
            # Check if comment exists and belongs to user
            comment = self.db.select('comments', where='id = ? AND user_id = ?', 
                                   params=(comment_id, user_id), limit=1)
            if not comment:
                return False, "Comment not found or you don't have permission to edit it"
            
            # Validate content
            content = content.strip()
            if not content or len(content) < 3:
                return False, "Comment must be at least 3 characters long"
            
            if len(content) > 1000:
                return False, "Comment must be less than 1000 characters"
            
            # Update comment
            self.db.update('comments', 
                          {'content': content, 'updated_at': datetime.now().isoformat()}, 
                          'id = ?', (comment_id,))
            
            return True, "Comment updated successfully"
            
        except Exception as e:
            return False, f"Error updating comment: {str(e)}"
    
    def delete_comment(self, comment_id, user_id):
        """Delete a comment"""
        try:
            if not self.db:
                return False, "Database connection failed"
            
            # Check if comment exists and belongs to user
            comment = self.db.select('comments', where='id = ? AND user_id = ?', 
                                   params=(comment_id, user_id), limit=1)
            if not comment:
                return False, "Comment not found or you don't have permission to delete it"
            
            # Delete comment (this will also delete replies due to foreign key cascade)
            self.db.execute_query("DELETE FROM comments WHERE id = ?", (comment_id,))
            
            return True, "Comment deleted successfully"
            
        except Exception as e:
            return False, f"Error deleting comment: {str(e)}"
    
    def toggle_comment_like(self, comment_id, user_id):
        """Toggle like for a comment"""
        try:
            if not self.db:
                return False, "Database connection failed"
            
            # Check if user already liked this comment
            existing = self.db.select('comment_likes', 
                                    where='comment_id = ? AND user_id = ?', 
                                    params=(comment_id, user_id), 
                                    limit=1)
            
            if existing:
                # Unlike - remove the like
                self.db.execute_query(
                    "DELETE FROM comment_likes WHERE comment_id = ? AND user_id = ?",
                    (comment_id, user_id)
                )
                # Decrement like count
                self.db.execute_query(
                    "UPDATE comments SET likes = likes - 1 WHERE id = ?",
                    (comment_id,)
                )
                return True, "Comment unliked"
            else:
                # Like - add the like
                like_data = {
                    'comment_id': comment_id,
                    'user_id': user_id,
                    'created_at': datetime.now().isoformat()
                }
                self.db.insert('comment_likes', like_data)
                # Increment like count
                self.db.execute_query(
                    "UPDATE comments SET likes = likes + 1 WHERE id = ?",
                    (comment_id,)
                )
                return True, "Comment liked"
                
        except Exception as e:
            return False, f"Error toggling comment like: {str(e)}"
    
    def get_comment_stats(self, article_id):
        """Get comment statistics for an article"""
        try:
            if not self.db:
                return None, "Database connection failed"
            
            # Total comments
            total = self.db.execute_query(
                "SELECT COUNT(*) as count FROM comments WHERE article_id = ?", 
                (article_id,)
            )[0]['count']
            
            # Top-level comments
            top_level = self.db.execute_query(
                "SELECT COUNT(*) as count FROM comments WHERE article_id = ? AND parent_id IS NULL", 
                (article_id,)
            )[0]['count']
            
            # Replies
            replies = total - top_level
            
            return {
                'total_comments': total,
                'top_level_comments': top_level,
                'replies': replies
            }, "Stats retrieved successfully"
            
        except Exception as e:
            return None, f"Error retrieving comment stats: {str(e)}"

# Create global instance
comments_manager = CommentsManager()

