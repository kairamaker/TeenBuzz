#!/usr/bin/env python3
"""
Quick test script to verify authentication system
"""

import requests
import time

def quick_test():
    """Quick test of the authentication system"""
    print("🚀 TeenBuzz Authentication - Quick Test")
    print("=" * 50)
    
    base_url = "http://localhost:5003"
    
    # Test 1: Check if app is running
    print("1. Checking if app is running...")
    try:
        response = requests.get(base_url, timeout=3)
        if response.status_code == 200:
            print("   ✅ App is running on http://localhost:5003")
        else:
            print(f"   ❌ App returned status: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"   ❌ App is not running: {e}")
        print("   💡 Start it with: python app_with_auth.py")
        return
    
    # Test 2: Check key pages
    print("\n2. Testing key pages...")
    pages = [
        ("/", "Homepage"),
        ("/login", "Login"),
        ("/register", "Register"),
        ("/search", "Search"),
    ]
    
    for page, name in pages:
        try:
            response = requests.get(f"{base_url}{page}", timeout=3)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {name}: {response.status_code}")
        except:
            print(f"   ❌ {name}: Connection failed")
    
    # Test 3: Show test credentials
    print("\n3. Test Credentials Available:")
    print("   👤 Regular User:")
    print("      Username: testuser_web")
    print("      Email: testweb@example.com")
    print("      Password: TestPass123!")
    print()
    print("   👑 Admin User:")
    print("      Username: admin")
    print("      Email: admin@teenbuzz.com")
    print("      Password: AdminPass123!")
    
    # Test 4: Show test URLs
    print("\n4. Test URLs:")
    print(f"   🏠 Homepage: {base_url}/")
    print(f"   🔐 Login: {base_url}/login")
    print(f"   📝 Register: {base_url}/register")
    print(f"   🔍 Search: {base_url}/search")
    print(f"   👤 Profile: {base_url}/profile (after login)")
    print(f"   ⚙️ Admin: {base_url}/admin (admin only)")
    
    print("\n5. Testing Steps:")
    print("   1. Open browser and go to http://localhost:5003")
    print("   2. Click 'Login' in the navigation")
    print("   3. Login with: testuser_web / TestPass123!")
    print("   4. Check profile page and logout")
    print("   5. Register a new user")
    print("   6. Login as admin to test admin features")
    
    print("\n🎉 Quick test complete!")
    print("=" * 50)

if __name__ == "__main__":
    quick_test()
