#!/usr/bin/env python3
"""
Script to update admin user email
"""

import os
from dotenv import load_dotenv
from supabase.client import create_client

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def update_admin_email():
    """Update admin user email to teenbuzzteam@gmail.com"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Update admin user email
        print("📝 Updating admin user email...")
        
        # First, check if the new email already exists
        existing_user = supabase.table('users').select('id').eq('email', 'teenbuzzteam@gmail.com').execute()
        if existing_user.data:
            print("❌ Error: Email teenbuzzteam@gmail.com already exists for another user")
            return False
        
        # Update the admin user's email
        result = supabase.table('users').update({
            'email': 'teenbuzzteam@gmail.com'
        }).eq('username', 'admin').execute()
        
        if result.data:
            print("✅ Successfully updated admin email to: teenbuzzteam@gmail.com")
            print("\n📋 Updated admin credentials:")
            print("   Username: admin")
            print("   Password: admin123")
            print("   Email: teenbuzzteam@gmail.com")
            print("\n🔗 You can now:")
            print("   1. Login at http://localhost:5002/login")
            print("   2. Access admin panel at http://localhost:5002/admin")
            return True
        else:
            print("❌ Error: Could not update admin user")
            return False
        
    except Exception as e:
        print(f"❌ Error updating admin email: {str(e)}")
        return False

if __name__ == "__main__":
    update_admin_email() 