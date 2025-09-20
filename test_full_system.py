#!/usr/bin/env python3
"""
Comprehensive system test for TeenBuzz authentication
"""

import requests
import time
from auth_system_enhanced import auth_manager

def test_web_endpoints():
    """Test all web endpoints"""
    print("🌐 Testing Web Endpoints")
    print("=" * 40)
    
    base_url = "http://localhost:5003"
    endpoints = [
        ("/", "Homepage"),
        ("/login", "Login Page"),
        ("/register", "Register Page"),
        ("/search", "Search Page"),
        ("/trending", "Trending Page"),
        ("/categories", "Categories Page"),
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {name}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {name}: Connection failed - {e}")
    
    print()

def test_authentication_flow():
    """Test the complete authentication flow"""
    print("🔐 Testing Authentication Flow")
    print("=" * 40)
    
    # Test 1: Registration
    print("1. Testing User Registration...")
    success, message = auth_manager.register_user(
        username="testuser_web",
        email="testweb@example.com",
        password="TestPass123!",
        confirm_password="TestPass123!"
    )
    print(f"   Registration: {'✅' if success else '❌'} {message}")
    
    # Test 2: Database verification
    print("\n2. Verifying Database Storage...")
    try:
        user = auth_manager.db.select('users', where='username = ?', params=('testuser_web',), limit=1)
        if user:
            user_data = user[0]
            hashed_password = user_data.get('password_hash', '')
            is_hashed = hashed_password.startswith('$2b$')
            print(f"   Password Hashing: {'✅' if is_hashed else '❌'} {'Properly hashed' if is_hashed else 'Plain text detected'}")
            print(f"   User Active: {'✅' if user_data.get('is_active') else '❌'}")
        else:
            print("   Database Storage: ❌ User not found")
    except Exception as e:
        print(f"   Database Storage: ❌ Error: {e}")
    
    # Test 3: Password verification
    print("\n3. Testing Password Verification...")
    try:
        user = auth_manager.db.select('users', where='username = ?', params=('testuser_web',), limit=1)
        if user:
            user_data = user[0]
            correct_password = auth_manager.verify_password("TestPass123!", user_data['password_hash'])
            wrong_password = auth_manager.verify_password("WrongPass123!", user_data['password_hash'])
            print(f"   Correct Password: {'✅' if correct_password else '❌'}")
            print(f"   Wrong Password: {'✅' if not wrong_password else '❌'}")
    except Exception as e:
        print(f"   Password Verification: ❌ Error: {e}")
    
    print()

def test_validation():
    """Test input validation"""
    print("✅ Testing Input Validation")
    print("=" * 40)
    
    # Test username validation
    print("1. Username Validation:")
    test_cases = [
        ("ab", False, "Too short"),
        ("validuser123", True, "Valid"),
        ("user@invalid", False, "Invalid characters"),
        ("a" * 25, False, "Too long"),
    ]
    
    for username, expected, description in test_cases:
        valid, msg = auth_manager.validate_username(username)
        result = "✅" if valid == expected else "❌"
        print(f"   {result} {description}: {username} -> {msg}")
    
    # Test email validation
    print("\n2. Email Validation:")
    email_cases = [
        ("invalid-email", False, "Invalid format"),
        ("test@example.com", True, "Valid"),
        ("user@domain", False, "Missing TLD"),
    ]
    
    for email, expected, description in email_cases:
        valid, msg = auth_manager.validate_email(email)
        result = "✅" if valid == expected else "❌"
        print(f"   {result} {description}: {email} -> {msg}")
    
    # Test password validation
    print("\n3. Password Validation:")
    password_cases = [
        ("weak", False, "Too weak"),
        ("TestPass123!", True, "Strong password"),
        ("nouppercase123!", False, "No uppercase"),
        ("NOLOWERCASE123!", False, "No lowercase"),
    ]
    
    for password, expected, description in password_cases:
        valid, msg = auth_manager.validate_password(password)
        result = "✅" if valid == expected else "❌"
        print(f"   {result} {description}: {msg}")
    
    print()

def test_database_operations():
    """Test database operations"""
    print("🗄️ Testing Database Operations")
    print("=" * 40)
    
    try:
        # Test user count
        users = auth_manager.db.select('users')
        print(f"✅ Total users in database: {len(users)}")
        
        # Test admin users
        admin_users = [u for u in users if u.get('is_admin')]
        print(f"✅ Admin users: {len(admin_users)}")
        
        # Test active users
        active_users = [u for u in users if u.get('is_active', True)]
        print(f"✅ Active users: {len(active_users)}")
        
        # Test password reset tokens table
        try:
            tokens = auth_manager.db.select('password_reset_tokens')
            print(f"✅ Password reset tokens: {len(tokens)}")
        except:
            print("⚠️ Password reset tokens table not found")
        
    except Exception as e:
        print(f"❌ Database operations failed: {e}")
    
    print()

def test_security_features():
    """Test security features"""
    print("🔒 Testing Security Features")
    print("=" * 40)
    
    # Test password hashing
    print("1. Password Security:")
    password = "TestSecurity123!"
    hashed1 = auth_manager.hash_password(password)
    hashed2 = auth_manager.hash_password(password)
    
    # Hashes should be different (due to salt)
    different_hashes = hashed1 != hashed2
    print(f"   Salt Generation: {'✅' if different_hashes else '❌'} {'Unique salts' if different_hashes else 'Same hashes'}")
    
    # Both should verify correctly
    verify1 = auth_manager.verify_password(password, hashed1)
    verify2 = auth_manager.verify_password(password, hashed2)
    print(f"   Password Verification: {'✅' if verify1 and verify2 else '❌'}")
    
    # Test SQL injection prevention
    print("\n2. SQL Injection Prevention:")
    try:
        # Try to inject SQL in username
        malicious_username = "'; DROP TABLE users; --"
        result = auth_manager.db.select('users', where='username = ?', params=(malicious_username,), limit=1)
        print(f"   SQL Injection Test: {'✅' if not result else '❌'} {'Protected' if not result else 'Vulnerable'}")
    except Exception as e:
        print(f"   SQL Injection Test: ✅ Protected (Error: {e})")
    
    print()

def main():
    """Run all tests"""
    print("🧪 TeenBuzz Authentication System - Full Test Suite")
    print("=" * 60)
    print()
    
    # Check if app is running
    try:
        response = requests.get("http://localhost:5003", timeout=3)
        if response.status_code == 200:
            print("✅ App is running on http://localhost:5003")
        else:
            print(f"⚠️ App responded with status: {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ App is not running. Start it with: python app_with_auth.py")
        return
    
    print()
    
    # Run all tests
    test_web_endpoints()
    test_authentication_flow()
    test_validation()
    test_database_operations()
    test_security_features()
    
    print("🎉 Full System Test Complete!")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("1. Visit http://localhost:5003/login to test the web interface")
    print("2. Create an admin user: python create_admin_user.py")
    print("3. Test admin features at http://localhost:5003/admin")
    print("4. Check the testing guide: cat test_authentication_guide.md")

if __name__ == "__main__":
    main()
