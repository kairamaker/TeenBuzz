#!/usr/bin/env python3
"""
Test the enhanced authentication system
"""

from auth_system_enhanced import auth_manager
import requests

def test_auth_system():
    """Test the authentication system"""
    print("🧪 Testing Enhanced Authentication System")
    print("=" * 50)
    
    # Test 1: Register a new user
    print("\n1. Testing User Registration...")
    success, message = auth_manager.register_user(
        username="testuser",
        email="test@example.com", 
        password="TestPass123!",
        confirm_password="TestPass123!"
    )
    print(f"   Registration: {'✅' if success else '❌'} {message}")
    
    # Test 2: Try to register duplicate user
    print("\n2. Testing Duplicate Registration...")
    success, message = auth_manager.register_user(
        username="testuser",
        email="test2@example.com",
        password="TestPass123!",
        confirm_password="TestPass123!"
    )
    print(f"   Duplicate Registration: {'✅' if not success else '❌'} {message}")
    
    # Test 3: Test login with correct credentials
    print("\n3. Testing Login with Correct Credentials...")
    success, message = auth_manager.login_user("testuser", "TestPass123!")
    print(f"   Login: {'✅' if success else '❌'} {message}")
    
    # Test 4: Test login with wrong password
    print("\n4. Testing Login with Wrong Password...")
    success, message = auth_manager.login_user("testuser", "WrongPass123!")
    print(f"   Wrong Password: {'✅' if not success else '❌'} {message}")
    
    # Test 5: Test password validation
    print("\n5. Testing Password Validation...")
    valid, msg = auth_manager.validate_password("weak")
    print(f"   Weak Password: {'✅' if not valid else '❌'} {msg}")
    
    valid, msg = auth_manager.validate_password("StrongPass123!")
    print(f"   Strong Password: {'✅' if valid else '❌'} {msg}")
    
    # Test 6: Test email validation
    print("\n6. Testing Email Validation...")
    valid = auth_manager.validate_email("invalid-email")
    print(f"   Invalid Email: {'✅' if not valid else '❌'} Should be invalid")
    
    valid = auth_manager.validate_email("test@example.com")
    print(f"   Valid Email: {'✅' if valid else '❌'} Should be valid")
    
    # Test 7: Test username validation
    print("\n7. Testing Username Validation...")
    valid, msg = auth_manager.validate_username("ab")
    print(f"   Short Username: {'✅' if not valid else '❌'} {msg}")
    
    valid, msg = auth_manager.validate_username("validuser123")
    print(f"   Valid Username: {'✅' if valid else '❌'} {msg}")
    
    print("\n🎉 Authentication System Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_auth_system()
