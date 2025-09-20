#!/usr/bin/env python3
"""
Simple test for authentication system without Flask context
"""

from auth_system_enhanced import AuthManager
import sqlite3

def test_auth_system():
    """Test the authentication system without Flask context"""
    print("🧪 Testing Enhanced Authentication System (Simple)")
    print("=" * 50)
    
    # Create auth manager
    auth_manager = AuthManager()
    
    # Test 1: Register a new user
    print("\n1. Testing User Registration...")
    success, message = auth_manager.register_user(
        username="testuser2",
        email="test2@example.com", 
        password="TestPass123!",
        confirm_password="TestPass123!"
    )
    print(f"   Registration: {'✅' if success else '❌'} {message}")
    
    # Test 2: Try to register duplicate user
    print("\n2. Testing Duplicate Registration...")
    success, message = auth_manager.register_user(
        username="testuser2",
        email="test3@example.com",
        password="TestPass123!",
        confirm_password="TestPass123!"
    )
    print(f"   Duplicate Registration: {'✅' if not success else '❌'} {message}")
    
    # Test 3: Test password validation
    print("\n3. Testing Password Validation...")
    valid, msg = auth_manager.validate_password("weak")
    print(f"   Weak Password: {'✅' if not valid else '❌'} {msg}")
    
    valid, msg = auth_manager.validate_password("StrongPass123!")
    print(f"   Strong Password: {'✅' if valid else '❌'} {msg}")
    
    # Test 4: Test email validation
    print("\n4. Testing Email Validation...")
    valid, msg = auth_manager.validate_email("invalid-email")
    print(f"   Invalid Email: {'✅' if not valid else '❌'} {msg}")
    
    valid, msg = auth_manager.validate_email("test@example.com")
    print(f"   Valid Email: {'✅' if valid else '❌'} {msg}")
    
    # Test 5: Test username validation
    print("\n5. Testing Username Validation...")
    valid, msg = auth_manager.validate_username("ab")
    print(f"   Short Username: {'✅' if not valid else '❌'} {msg}")
    
    valid, msg = auth_manager.validate_username("validuser123")
    print(f"   Valid Username: {'✅' if valid else '❌'} {msg}")
    
    # Test 6: Test password hashing
    print("\n6. Testing Password Hashing...")
    password = "TestPass123!"
    hashed = auth_manager.hash_password(password)
    verified = auth_manager.verify_password(password, hashed)
    print(f"   Password Hashing: {'✅' if verified else '❌'} Hash and verify working")
    
    # Test 7: Test database operations
    print("\n7. Testing Database Operations...")
    try:
        # Try to find the user we just created
        user = auth_manager.db.select('users', where='username = ?', params=('testuser2',), limit=1)
        if user:
            print(f"   Database Query: {'✅' if user else '❌'} Found user: {user[0]['username']}")
        else:
            print("   Database Query: ❌ User not found")
    except Exception as e:
        print(f"   Database Query: ❌ Error: {e}")
    
    print("\n🎉 Authentication System Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_auth_system()
