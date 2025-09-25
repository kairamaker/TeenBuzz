#!/usr/bin/env python3
"""
Enhanced Authentication System for TeenBuzz
"""

import bcrypt
import secrets
import re
from datetime import datetime, timedelta
from functools import wraps
from flask import session, request, flash, redirect, url_for, current_app
from database_manager import get_database

class AuthManager:
    def __init__(self):
        self.db = get_database()
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password, hashed):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = re.match(pattern, email) is not None
        if is_valid:
            return True, "Email is valid"
        else:
            return False, "Invalid email format"
    
    def validate_password(self, password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"
    
    def validate_username(self, username):
        """Validate username"""
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 20:
            return False, "Username must be less than 20 characters"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        return True, "Username is valid"
    
    def generate_username_suggestions(self, base_username):
        """Generate alternative username suggestions"""
        import random
        suggestions = []
        
        # Add numbers
        for i in range(1, 4):
            suggestion = f"{base_username}{i}"
            existing = self.db.select('users', where='username = ?', params=(suggestion,), limit=1)
            if not existing:
                suggestions.append(suggestion)
                if len(suggestions) >= 3:
                    break
        
        # Add random numbers if we need more
        while len(suggestions) < 3:
            random_num = random.randint(100, 999)
            suggestion = f"{base_username}{random_num}"
            existing = self.db.select('users', where='username = ?', params=(suggestion,), limit=1)
            if not existing and suggestion not in suggestions:
                suggestions.append(suggestion)
        
        return suggestions[:3]

    def register_user(self, username, email, password, confirm_password):
        """Register a new user"""
        # Validation
        if password != confirm_password:
            return False, "Passwords do not match"
        
        valid, msg = self.validate_username(username)
        if not valid:
            return False, msg
        
        valid, msg = self.validate_email(email)
        if not valid:
            return False, msg
        
        valid, msg = self.validate_password(password)
        if not valid:
            return False, msg
        
        # Check if user already exists
        existing_user = self.db.select('users', where='username = ?', params=(username,), limit=1)
        if existing_user:
            suggestions = self.generate_username_suggestions(username)
            return False, f"Username already exists. Try: {', '.join(suggestions)}"
        
        existing_email = self.db.select('users', where='email = ?', params=(email,), limit=1)
        if existing_email:
            return False, "Email already exists"
        
        # Hash password and create user
        hashed_password = self.hash_password(password)
        
        user_data = {
            'username': username,
            'email': email,
            'password_hash': hashed_password,
            'is_admin': False,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'is_active': True
        }
        
        try:
            user_id = self.db.insert('users', user_data)
            return True, f"User registered successfully with ID: {user_id}"
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def login_user(self, username, password, remember_me=False):
        """Login user"""
        # Find user by username or email
        user = self.db.select('users', where='username = ?', params=(username,), limit=1)
        if not user:
            user = self.db.select('users', where='email = ?', params=(username,), limit=1)
        
        if not user:
            return False, "Invalid username or password"
        
        user = user[0]
        
        # Check if user is active
        if not user.get('is_active', True):
            return False, "Account is deactivated"
        
        # Verify password
        if not self.verify_password(password, user['password_hash']):
            return False, "Invalid username or password"
        
        # Update last login
        self.db.update('users', {'last_login': datetime.now().isoformat()}, 'id = ?', (user['id'],))
        
        # Create session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['email'] = user['email']
        session['is_admin'] = user.get('is_admin', False)
        session['is_authenticated'] = True
        
        if remember_me:
            session.permanent = True
            current_app.permanent_session_lifetime = timedelta(days=30)
        else:
            session.permanent = False
        
        return True, "Login successful"
    
    def logout_user(self):
        """Logout user"""
        session.clear()
        return True, "Logged out successfully"
    
    def get_current_user(self):
        """Get current user from session"""
        if not session.get('is_authenticated'):
            return None
        
        return {
            'id': session.get('user_id'),
            'username': session.get('username'),
            'email': session.get('email'),
            'is_admin': session.get('is_admin', False)
        }
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return session.get('is_authenticated', False)
    
    def is_admin(self):
        """Check if current user is admin"""
        return session.get('is_admin', False)
    
    def change_password(self, user_id, old_password, new_password):
        """Change user password"""
        user = self.db.select('users', where='id = ?', params=(user_id,), limit=1)
        if not user:
            return False, "User not found"
        
        user = user[0]
        
        # Verify old password
        if not self.verify_password(old_password, user['password_hash']):
            return False, "Current password is incorrect"
        
        # Validate new password
        valid, msg = self.validate_password(new_password)
        if not valid:
            return False, msg
        
        # Hash new password and update
        hashed_password = self.hash_password(new_password)
        self.db.update('users', {'password_hash': hashed_password}, 'id = ?', (user_id,))
        
        return True, "Password changed successfully"
    
    def generate_reset_token(self, email):
        """Generate password reset token"""
        user = self.db.select('users', where='email = ?', params=(email,), limit=1)
        if not user:
            return False, "Email not found"
        
        user = user[0]
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)
        
        # Store token in database
        token_data = {
            'user_id': user['id'],
            'token': token,
            'expires_at': expires_at.isoformat(),
            'used': False,
            'created_at': datetime.now().isoformat()
        }
        
        try:
            self.db.insert('password_reset_tokens', token_data)
            return True, token
        except Exception as e:
            return False, f"Failed to generate reset token: {str(e)}"
    
    def reset_password(self, token, new_password):
        """Reset password using token"""
        # Find valid token
        token_record = self.db.select('password_reset_tokens', where='token = ? AND used = ?', params=(token, False), limit=1)
        if not token_record:
            return False, "Invalid or expired token"
        
        token_record = token_record[0]
        
        # Check if token is expired
        expires_at = datetime.fromisoformat(token_record['expires_at'])
        if datetime.now() > expires_at:
            return False, "Token has expired"
        
        # Validate new password
        valid, msg = self.validate_password(new_password)
        if not valid:
            return False, msg
        
        # Hash new password and update user
        hashed_password = self.hash_password(new_password)
        self.db.update('users', {'password_hash': hashed_password}, 'id = ?', (token_record['user_id'],))
        
        # Mark token as used
        self.db.update('password_reset_tokens', {'used': True}, 'id = ?', (token_record['id'],))
        
        return True, "Password reset successfully"

# Global auth manager instance
auth_manager = AuthManager()

# Decorators
def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth_manager.is_authenticated():
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth_manager.is_authenticated():
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        if not auth_manager.is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current user"""
    return auth_manager.get_current_user()

def is_authenticated():
    """Check if user is authenticated"""
    return auth_manager.is_authenticated()

def is_admin():
    """Check if user is admin"""
    return auth_manager.is_admin()
