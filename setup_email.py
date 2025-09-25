#!/usr/bin/env python3
"""
Email Setup Script for TeenBuzz
"""

import os
from email_config import print_setup_instructions

def setup_email():
    """Interactive email setup"""
    print("📧 TeenBuzz Email Setup")
    print("=" * 30)
    
    # Check current configuration
    current_password = os.getenv('EMAIL_PASSWORD')
    
    if current_password and current_password != 'your-app-password-here':
        print(f"✅ Email password is configured: {current_password[:4]}****")
        
        # Test the configuration
        from email_system import email_manager
        print("\n🧪 Testing email connection...")
        success, message = email_manager.test_email_connection()
        
        if success:
            print(f"✅ {message}")
            print("\n🎉 Email system is ready to use!")
            
            # Test sending an email
            test_email = input("\n📧 Enter your email to test password reset: ").strip()
            if test_email:
                success, message = email_manager.send_password_reset_email(
                    test_email, "test-token-123", "TestUser"
                )
                if success:
                    print(f"✅ {message}")
                    print("📬 Check your email inbox!")
                else:
                    print(f"❌ {message}")
        else:
            print(f"❌ {message}")
            print("\n🔧 Please check your Gmail App Password configuration.")
    else:
        print("❌ Email password not configured")
        print_setup_instructions()
        
        # Offer to set it interactively
        app_password = input("\n🔑 Enter your Gmail App Password (or press Enter to skip): ").strip()
        if app_password:
            # Set environment variable for current session
            os.environ['EMAIL_PASSWORD'] = app_password
            print("✅ Email password set for current session")
            print("💡 To make it permanent, add to your shell profile:")
            print(f"   export EMAIL_PASSWORD='{app_password}'")
            
            # Test the new configuration
            from email_system import email_manager
            print("\n🧪 Testing email connection...")
            success, message = email_manager.test_email_connection()
            
            if success:
                print(f"✅ {message}")
                print("🎉 Email system is now working!")
            else:
                print(f"❌ {message}")

if __name__ == "__main__":
    setup_email()

