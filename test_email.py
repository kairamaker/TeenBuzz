#!/usr/bin/env python3
"""
Test Email System for TeenBuzz
"""

import os
from email_system import email_manager

def test_email_system():
    """Test the email system"""
    print("🧪 Testing TeenBuzz Email System")
    print("=" * 50)
    
    # Check if email password is set
    email_password = os.getenv("EMAIL_PASSWORD")
    if not email_password or email_password == "your-app-password-here":
        print("❌ Email password not configured!")
        print("\n📋 Setup Instructions:")
        print("1. Enable 2-Factor Authentication on your Gmail account")
        print("2. Generate an App Password for TeenBuzz")
        print("3. Create a .env file with: EMAIL_PASSWORD=your-app-password")
        print("4. Run this test again")
        return False
    
    print(f"✅ Email password configured: {email_password[:4]}****")
    
    # Test email connection
    print("\n🔌 Testing email connection...")
    success, message = email_manager.test_email_connection()
    
    if success:
        print(f"✅ {message}")
        
        # Test sending a password reset email
        print("\n📧 Testing password reset email...")
        test_email = input("Enter your email address to test: ").strip()
        
        if test_email:
            success, message = email_manager.send_password_reset_email(
                test_email, 
                "test-token-123", 
                "TestUser"
            )
            
            if success:
                print(f"✅ {message}")
                print("📬 Check your email inbox for the test message!")
            else:
                print(f"❌ {message}")
        else:
            print("⏭️  Skipping email send test")
    else:
        print(f"❌ {message}")
        print("\n🔧 Troubleshooting:")
        print("- Make sure 2FA is enabled on your Gmail account")
        print("- Verify you're using the App Password (not regular password)")
        print("- Check that the App Password doesn't have spaces")
        print("- Ensure your internet connection is working")
    
    return success

if __name__ == "__main__":
    test_email_system()

