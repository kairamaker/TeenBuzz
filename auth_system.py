#!/usr/bin/env python3

import hashlib
import secrets
import re
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, flash, request, current_app
from database_manager import get_database

class AuthManager:
    """Complete authentication system for TeenBuzz"""
    
    def __init__(self):
        self.db = get_database()
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, password_hash = stored_hash.split(':')
            test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return test_hash == password_hash
        except:
            return False
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_username(self, username: str) -> bool:
        """Validate username format"""
        if len(username) < 3 or len(username) > 20:
            return False
        pattern = r'^[a-zA-Z0-9]+$'
        return re.match(pattern, username) is not None
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, "Password is valid"
    
    def register_user(self, username: str, email: str, password: str) -> tuple[bool, str]:
        """Register a new user"""
        try:
            # Validate inputs
            if not self.validate_username(username):
                return False, "Username must be 3-20 characters and contain only letters, numbers, and underscores"
            
            if not self.validate_email(email):
                return False, "Please enter a valid email address"
            
            is_valid, message = self.validate_password(password)
            if not is_valid:
                return False, message
            
            # Check if user already exists
            if self.db:
                with self.db:
                    existing_user = self.db.select('users', where='username = ? OR email = ?', params=(username, email))
                    if existing_user:
                        return False, "Username or email already exists"
                    
                    # Create new user
                    user_data = {
                        'username': username,
                        'email': email,
                        'password_hash': self.hash_password(password),
                        'is_admin': False,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    result = self.db.insert('users', user_data)
                    return True, f"User {username} registered successfully!"
            else:
                return False, "Database not available"
                
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def login_user(self, username: str, password: str) -> tuple[bool, str, dict]:
        """Login user and return user data"""
        try:
            if not self.db:
                return False, "Database not available", {}
            
            with self.db:
                # Find user by username or email
                user = self.db.select('users', where='username = ? OR email = ?', params=(username, username))
                
                if not user:
                    return False, "Invalid username or password", {}
                
                user = user[0]
                
                # Verify password
                if not self.verify_password(password, user['password_hash']):
                    return False, "Invalid username or password", {}
                
                # Update last login
                self.db.update('users', {'updated_at': datetime.now().isoformat()}, 'id = ?', (user['id'],))
                
                # Return user data (without password hash)
                user_data = {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'is_admin': user['is_admin'],
                    'created_at': user['created_at']
                }
                
                return True, "Login successful", user_data
                
        except Exception as e:
            return False, f"Login failed: {str(e)}", {}
    
    def logout_user(self):
        """Logout current user"""
        session.clear()
    
    def get_current_user(self) -> dict:
        """Get current logged-in user"""
        if 'user_id' in session:
            try:
                if self.db:
                    with self.db:
                        user = self.db.select('users', where='id = ?', params=(session['user_id'],))
                        if user:
                            user = user[0]
                            return {
                                'id': user['id'],
                                'username': user['username'],
                                'email': user['email'],
                                'is_admin': user['is_admin'],
                                'created_at': user['created_at']
                            }
            except:
                pass
        return None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return 'user_id' in session and self.get_current_user() is not None
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        user = self.get_current_user()
        return user and user.get('is_admin', False)
    
    def require_auth(self, f):
        """Decorator to require authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.is_authenticated():
                flash('Please log in to access this page', 'error')
                return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function
    
    def require_admin(self, f):
        """Decorator to require admin access"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.is_authenticated():
                flash('Please log in to access this page', 'error')
                return redirect(url_for('login', next=request.url))
            if not self.is_admin():
                flash('Admin access required', 'error')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function

# Global auth manager instance
auth_manager = AuthManager()

# Convenience functions
def login_required(f):
    """Decorator to require authentication"""
    return auth_manager.require_auth(f)

def admin_required(f):
    """Decorator to require admin access"""
    return auth_manager.require_admin(f)

def get_current_user():
    """Get current user"""
    return auth_manager.get_current_user()

def is_authenticated():
    """Check if user is authenticated"""
    return auth_manager.is_authenticated()

def is_admin():
    """Check if user is admin"""
    return auth_manager.is_admin()
