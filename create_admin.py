#!/usr/bin/env python3
"""
Create Admin Account for TeenBuzz
"""

from database_manager import get_database
from auth_system_enhanced import auth_manager
import uuid
from datetime import datetime

def create_admin_account():
    """Create an admin account"""
    try:
        db = get_database()
        if not db:
            print("❌ Could not connect to database")
            return False
        
        # Check if admin already exists
        existing_admin = db.select('users', where='username = ?', params=('admin',), limit=1)
        if existing_admin:
            print("✅ Admin account already exists")
            return True
        
        # Create admin user
        admin_data = {
            'id': str(uuid.uuid4()),
            'username': 'admin',
            'email': 'admin@teenbuzz.com',
            'password_hash': auth_manager.hash_password('admin123'),
            'is_admin': True,
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        
        # Insert admin user
        db.insert('users', admin_data)
        print("✅ Admin account created successfully!")
        print("👑 Username: admin")
        print("🔑 Password: admin123")
        print("⚠️  Change this password after first login!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        return False

if __name__ == '__main__':
    create_admin_account()
