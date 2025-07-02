#!/usr/bin/env python3
"""
Simple script to set up user authentication tables in TeenBuzz database
"""

import os
from dotenv import load_dotenv
from supabase.client import create_client
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def setup_user_tables():
    """Set up user authentication tables"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Create default admin user
        print("📝 Creating default admin user...")
        admin_password_hash = generate_password_hash('admin123')
        admin_user = {
            'username': 'admin',
            'password_hash': admin_password_hash,
            'email': 'admin@teenbuzz.com',
            'is_admin': True
        }
        
        # Check if admin user already exists
        try:
            existing_admin = supabase.table('users').select('id').eq('username', 'admin').execute()
            if not existing_admin.data:
                supabase.table('users').insert(admin_user).execute()
                print("✅ Default admin user created (username: admin, password: admin123)")
            else:
                print("ℹ️  Admin user already exists")
        except Exception as e:
            print(f"⚠️  Users table might not exist yet: {str(e)}")
            print("📝 Please run the SQL commands from database_schema.sql in your Supabase dashboard first")
            return False
        
        print("\n🎉 User authentication setup complete!")
        print("\n📋 Default admin credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n🔗 You can now:")
        print("   1. Register new users at /register")
        print("   2. Login at /login")
        print("   3. Users can draw articles from their profile page")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up user tables: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up TeenBuzz user authentication...")
    success = setup_user_tables()
    if success:
        print("\n✅ Setup completed successfully!")
    else:
        print("\n❌ Setup failed. Please check your configuration.") 