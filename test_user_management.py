#!/usr/bin/env python3
"""
Test the enhanced user management system
"""

from user_management import user_manager
from email_system import email_manager
import requests

def test_user_management():
    """Test the user management system"""
    print("🧪 Testing Enhanced User Management System")
    print("=" * 50)
    
    # Test 1: Get user profile
    print("\n1. Testing User Profile System...")
    try:
        # Get a test user
        users = user_manager.db.select('users', limit=1)
        if users:
            user_id = users[0]['id']
            user_profile = user_manager.get_user_profile(user_id)
            
            if user_profile:
                print(f"   ✅ User profile loaded: {user_profile['username']}")
                print(f"   ✅ Preferences: {user_profile.get('preferences', {}).get('categories', 'None')}")
                print(f"   ✅ Stats: {user_profile.get('stats', {})}")
            else:
                print("   ❌ Failed to load user profile")
        else:
            print("   ❌ No users found in database")
    except Exception as e:
        print(f"   ❌ Error testing user profile: {e}")
    
    # Test 2: Get recommendations
    print("\n2. Testing Article Recommendations...")
    try:
        if users:
            user_id = users[0]['id']
            recommendations = user_manager.get_recommended_articles(user_id, limit=3)
            print(f"   ✅ Found {len(recommendations)} recommended articles")
            for article in recommendations:
                print(f"      - {article['headline'][:50]}...")
        else:
            print("   ❌ No users found for recommendations")
    except Exception as e:
        print(f"   ❌ Error testing recommendations: {e}")
    
    # Test 3: Get available categories and topics
    print("\n3. Testing Categories and Topics...")
    try:
        categories = user_manager.get_available_categories()
        topics = user_manager.get_available_topics()
        print(f"   ✅ Available categories: {len(categories)}")
        print(f"   ✅ Available topics: {len(topics)}")
        print(f"      Categories: {', '.join(categories[:5])}")
        print(f"      Topics: {', '.join(topics[:5])}")
    except Exception as e:
        print(f"   ❌ Error testing categories/topics: {e}")
    
    # Test 4: Update preferences
    print("\n4. Testing Preferences Update...")
    try:
        if users:
            user_id = users[0]['id']
            test_preferences = {
                'categories': 'Technology,Environment',
                'topics': 'ai,climate,technology'
            }
            success, message = user_manager.update_user_preferences(user_id, test_preferences)
            print(f"   {'✅' if success else '❌'} Preferences update: {message}")
        else:
            print("   ❌ No users found for preferences test")
    except Exception as e:
        print(f"   ❌ Error testing preferences: {e}")
    
    # Test 5: Email system
    print("\n5. Testing Email System...")
    try:
        # Test email connection (without actually sending)
        success, message = email_manager.test_email_connection()
        print(f"   {'✅' if success else '❌'} Email connection: {message}")
        
        if not success:
            print("   💡 To enable email features:")
            print("      1. Set EMAIL_PASSWORD environment variable")
            print("      2. Use Gmail App Password (not regular password)")
            print("      3. Enable 2-factor authentication on Gmail")
    except Exception as e:
        print(f"   ❌ Error testing email system: {e}")
    
    print("\n🎉 User Management System Test Complete!")
    print("=" * 50)

def test_web_endpoints():
    """Test the new web endpoints"""
    print("\n🌐 Testing New Web Endpoints")
    print("=" * 30)
    
    base_url = "http://localhost:5003"
    new_endpoints = [
        ("/dashboard", "User Dashboard"),
        ("/profile", "Enhanced Profile"),
        ("/update-preferences", "Update Preferences"),
        ("/update-profile", "Update Profile"),
    ]
    
    for endpoint, name in new_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=3)
            if response.status_code == 200:
                print(f"   ✅ {name}: Accessible")
            elif response.status_code == 302:
                print(f"   ⚠️ {name}: Redirected (login required)")
            else:
                print(f"   ❌ {name}: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {name}: Connection failed")

if __name__ == "__main__":
    test_user_management()
    test_web_endpoints()
    
    print("\n📋 Next Steps:")
    print("1. Login to test the enhanced profile: http://localhost:5003/login")
    print("2. Visit dashboard: http://localhost:5003/dashboard")
    print("3. Test preferences: http://localhost:5003/profile?tab=preferences")
    print("4. Test email reset: http://localhost:5003/forgot-password")
