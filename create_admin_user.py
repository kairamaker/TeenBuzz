#!/usr/bin/env python3
"""
Script to create admin user with proper password hashing
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

def create_admin_user(email="admin@teenbuzz.com"):
    """Create admin user with proper password hashing"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Create admin user with proper password hashing
        print("📝 Creating admin user...")
        admin_password_hash = generate_password_hash('admin123')
        admin_user = {
            'username': 'admin',
            'password_hash': admin_password_hash,
            'email': email,
            'is_admin': True
        }
        
        # Check if admin user already exists
        try:
            existing_admin = supabase.table('users').select('id').eq('username', 'admin').execute()
            if existing_admin.data:
                # Update existing admin with new email and password
                supabase.table('users').update({
                    'password_hash': admin_password_hash,
                    'email': email,
                    'is_admin': True
                }).eq('username', 'admin').execute()
                print(f"✅ Updated existing admin user with email: {email}")
            else:
                # Create new admin user
                supabase.table('users').insert(admin_user).execute()
                print(f"✅ Created new admin user with email: {email}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("📝 Please make sure the users table exists in your Supabase database")
            return False
        
        print("\n🎉 Admin user setup complete!")
        print("\n📋 Admin credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print(f"   Email: {email}")
        print("\n🔗 You can now:")
        print("   1. Login at http://localhost:5002/login")
        print("   2. Access admin panel at http://localhost:5002/admin")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        return False

if __name__ == "__main__":
    # You can change the email here or pass it as an argument
    email = input("Enter admin email (or press Enter for default): ").strip()
    if not email:
        email = "admin@teenbuzz.com"
    
    create_admin_user(email) 