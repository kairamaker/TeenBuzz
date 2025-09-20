#!/usr/bin/env python3

from auth_system import auth_manager

def fix_admin_user():
    """Fix the admin user with proper password"""
    
    try:
        if auth_manager.db:
            with auth_manager.db:
                # Delete existing admin user
                auth_manager.db.delete('users', 'username = ?', ('admin',))
                print("✅ Deleted old admin user")
                
                # Create new admin user with proper password
                username = "admin"
                email = "admin@teenbuzz.com"
                password = "Admin123!"
                
                success, message = auth_manager.register_user(username, email, password)
                
                if success:
                    print(f"✅ {message}")
                    
                    # Make user admin
                    users = auth_manager.db.select('users', where='username = ?', params=(username,))
                    if users:
                        user = users[0]
                        auth_manager.db.update('users', {'is_admin': True}, 'id = ?', (user['id'],))
                        print("✅ User promoted to admin")
                        print(f"✅ Admin credentials: username='admin', password='Admin123!'")
                    else:
                        print("❌ User not found after creation")
                else:
                    print(f"❌ {message}")
        else:
            print("❌ Database not available")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_admin_user()
