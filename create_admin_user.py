#!/usr/bin/env python3

from auth_system import auth_manager
import uuid

def create_admin_user():
    """Create an admin user for testing"""
    
    # Create admin user
    username = "admin"
    email = "admin@teenbuzz.com"
    password = "Admin123!"
    
    print("Creating admin user...")
    success, message = auth_manager.register_user(username, email, password)
    
    if success:
        print(f"✅ {message}")
        
        # Make user admin
        try:
            if auth_manager.db:
                with auth_manager.db:
                    # Find the user
                    users = auth_manager.db.select('users', where='username = ?', params=(username,))
                    if users:
                        user = users[0]
                        # Update to admin
                        auth_manager.db.update('users', {'is_admin': True}, 'id = ?', (user['id'],))
                        print("✅ User promoted to admin")
                    else:
                        print("❌ User not found")
        except Exception as e:
            print(f"❌ Error promoting to admin: {e}")
    else:
        print(f"❌ {message}")

if __name__ == "__main__":
    create_admin_user()