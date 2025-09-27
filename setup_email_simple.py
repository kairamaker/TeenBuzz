#!/usr/bin/env python3
"""
Simple Email Setup for TeenBuzz
"""

import os
from email_system import email_manager

def setup_email():
    """Setup email configuration"""
    print("📧 TeenBuzz Email Setup")
    print("=" * 40)
    print()
    print("To send password reset emails from teenbuzzteam@gmail.com:")
    print()
    print("1. Go to: https://myaccount.google.com/apppasswords")
    print("2. Sign in with: teenbuzzteam@gmail.com")
    print("3. Generate an 'App Password' for 'Mail'")
    print("4. Copy the 16-character password")
    print()
    
    # Check current status
    print("Current email status:")
    if email_manager.is_configured():
        print("✅ Email is configured")
        success, message = email_manager.test_email_connection()
        if success:
            print(f"✅ Email connection test: {message}")
        else:
            print(f"❌ Email connection failed: {message}")
    else:
        print("❌ Email not configured")
        print()
        print("To configure email:")
        print("1. Set environment variable:")
        print("   export EMAIL_PASSWORD='your-16-character-app-password'")
        print()
        print("2. Or add to .env file:")
        print("   EMAIL_PASSWORD=your-16-character-app-password")
        print()
        print("3. Restart the Flask app")
    
    print()
    print("📝 Note: If email setup fails, users will see a 'Show Reset Link' button instead.")

if __name__ == '__main__':
    setup_email()
