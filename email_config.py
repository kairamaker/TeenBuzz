#!/usr/bin/env python3
"""
Email Configuration for TeenBuzz
"""

import os

# Email Configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email_address': 'teenbuzzteam@gmail.com',
    'email_password': os.getenv('EMAIL_PASSWORD', 'your-app-password-here'),
    'from_name': 'TeenBuzz Team'
}

def get_email_config():
    """Get email configuration"""
    return EMAIL_CONFIG

def is_email_configured():
    """Check if email is properly configured"""
    password = EMAIL_CONFIG['email_password']
    return password and password != 'your-app-password-here'

def print_setup_instructions():
    """Print email setup instructions"""
    print("📧 Email Setup Required!")
    print("=" * 40)
    print("1. Enable 2-Factor Authentication on Gmail")
    print("2. Generate App Password: https://myaccount.google.com/apppasswords")
    print("3. Set environment variable:")
    print("   export EMAIL_PASSWORD='your-16-character-app-password'")
    print("4. Or create .env file with:")
    print("   EMAIL_PASSWORD=your-16-character-app-password")
    print("5. Run: python test_email.py")

