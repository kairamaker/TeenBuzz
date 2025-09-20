#!/usr/bin/env python3
"""
Create an admin user for testing
"""

from auth_system_enhanced import auth_manager

def create_admin_user():
    """Create an admin user for testing"""
    print("🔧 Creating admin user...")
    
    # Create admin user
    success, message = auth_manager.register_user(
        username="admin",
        email="admin@teenbuzz.com",
        password="AdminPass123!",
        confirm_password="AdminPass123!"
    )
    
    if success:
        print(f"✅ Admin user created: {message}")
        
        # Update user to admin status
        try:
            # Get the user ID
            user = auth_manager.db.select('users', where='username = ?', params=('admin',), limit=1)
            if user:
                user_id = user[0]['id']
                # Update to admin
                auth_manager.db.update('users', {'is_admin': True}, 'id = ?', (user_id,))
                print("✅ Admin privileges granted")
                print("\n📋 Admin Login Credentials:")
                print("   Username: admin")
                print("   Email: admin@teenbuzz.com")
                print("   Password: AdminPass123!")
                print("\n🌐 Test at: http://localhost:5003/login")
            else:
                print("❌ Could not find admin user to update")
        except Exception as e:
            print(f"❌ Error updating admin status: {e}")
    else:
        print(f"❌ Failed to create admin user: {message}")

if __name__ == "__main__":
    create_admin_user()