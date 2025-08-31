#!/usr/bin/env python3
"""
Test script to verify registration process
"""

import os
from dotenv import load_dotenv
from supabase.client import create_client
from werkzeug.security import generate_password_hash
from datetime import datetime

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

def test_registration():
    """Test the registration process"""
    
    # Test data
    test_user = {
        'username': 'testuser123',
        'email': 'testuser123@example.com',
        'password': 'testpass123',
        'topics': ['Technology', 'Health']
    }
    
    print("🧪 Testing registration process...")
    
    # Check if user already exists
    try:
        result = supabase.table('users').select('id').eq('email', test_user['email']).execute()
        if result.data:
            print("⚠️ Test user already exists, skipping creation")
            return
    except Exception as e:
        print(f"❌ Error checking existing user: {e}")
        return
    
    # Create user
    try:
        password_hash = generate_password_hash(test_user['password'])
        user_data = {
            'username': test_user['username'],
            'email': test_user['email'],
            'password_hash': password_hash,
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('users').insert(user_data).execute()
        new_user = result.data[0]
        print(f"✅ User created successfully: {new_user['id']}")
        
        # Try to store preferences
        try:
            supabase.table('user_preferences').upsert({
                'user_id': new_user['id'],
                'email': test_user['email'],
                'topics': test_user['topics'],
                'updated_at': datetime.now().isoformat()
            }).execute()
            print("✅ User preferences stored successfully")
        except Exception as e:
            print(f"⚠️ User preferences storage failed: {e}")
            print("This is expected if the user_preferences table doesn't exist yet")
        
        # Clean up - delete test user
        try:
            supabase.table('users').delete().eq('id', new_user['id']).execute()
            print("✅ Test user cleaned up")
        except Exception as e:
            print(f"⚠️ Could not clean up test user: {e}")
            
    except Exception as e:
        print(f"❌ User creation failed: {e}")

if __name__ == "__main__":
    test_registration()
