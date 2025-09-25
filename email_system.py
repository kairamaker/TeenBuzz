#!/usr/bin/env python3
"""
Email System for TeenBuzz
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from email_config import get_email_config, is_email_configured

class EmailManager:
    def __init__(self):
        # Email configuration
        config = get_email_config()
        self.smtp_server = config['smtp_server']
        self.smtp_port = config['smtp_port']
        self.email_address = config['email_address']
        self.email_password = config['email_password']
        
    def send_password_reset_email(self, user_email, reset_token, username):
        """Send password reset email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = user_email
            msg['Subject'] = "TeenBuzz - Password Reset Request"
            
            # Create reset URL
            reset_url = f"http://localhost:5003/reset-password/{reset_token}"
            
            # Email body
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #1e40af; margin: 0;">TeenBuzz</h1>
                        <p style="color: #6b7280; margin: 5px 0;">News That Actually Matters to You</p>
                    </div>
                    
                    <div style="background: #f9fafb; padding: 30px; border-radius: 10px; margin-bottom: 20px;">
                        <h2 style="color: #1f2937; margin-top: 0;">Password Reset Request</h2>
                        <p>Hi {username},</p>
                        <p>We received a request to reset your password for your TeenBuzz account.</p>
                        <p>Click the button below to reset your password:</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_url}" 
                               style="background: #1e40af; color: white; padding: 12px 30px; 
                                      text-decoration: none; border-radius: 6px; 
                                      display: inline-block; font-weight: 600;">
                                Reset Password
                            </a>
                        </div>
                        
                        <p style="font-size: 14px; color: #6b7280;">
                            If the button doesn't work, copy and paste this link into your browser:<br>
                            <a href="{reset_url}" style="color: #1e40af;">{reset_url}</a>
                        </p>
                        
                        <p style="font-size: 14px; color: #6b7280;">
                            This link will expire in 1 hour for security reasons.
                        </p>
                    </div>
                    
                    <div style="text-align: center; font-size: 12px; color: #9ca3af;">
                        <p>If you didn't request this password reset, please ignore this email.</p>
                        <p>© 2025 TeenBuzz. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_address, user_email, text)
            server.quit()
            
            return True, "Password reset email sent successfully"
            
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"
    
    def send_welcome_email(self, user_email, username):
        """Send welcome email to new users"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = user_email
            msg['Subject'] = "Welcome to TeenBuzz!"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #1e40af; margin: 0;">Welcome to TeenBuzz!</h1>
                        <p style="color: #6b7280; margin: 5px 0;">News That Actually Matters to You</p>
                    </div>
                    
                    <div style="background: #f9fafb; padding: 30px; border-radius: 10px; margin-bottom: 20px;">
                        <h2 style="color: #1f2937; margin-top: 0;">Hi {username}!</h2>
                        <p>Welcome to TeenBuzz! We're excited to have you join our community of informed teenagers.</p>
                        
                        <h3 style="color: #1e40af;">What you can do:</h3>
                        <ul style="color: #4b5563;">
                            <li>📰 Read personalized news articles</li>
                            <li>🔍 Search for topics that interest you</li>
                            <li>⭐ Save articles to read later</li>
                            <li>💬 Share your thoughts with the community</li>
                            <li>🎯 Get recommendations based on your interests</li>
                        </ul>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="http://localhost:5003/dashboard" 
                               style="background: #1e40af; color: white; padding: 12px 30px; 
                                      text-decoration: none; border-radius: 6px; 
                                      display: inline-block; font-weight: 600;">
                                Go to Dashboard
                            </a>
                        </div>
                    </div>
                    
                    <div style="text-align: center; font-size: 12px; color: #9ca3af;">
                        <p>© 2025 TeenBuzz. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_address, user_email, text)
            server.quit()
            
            return True, "Welcome email sent successfully"
            
        except Exception as e:
            return False, f"Failed to send welcome email: {str(e)}"
    
    def is_configured(self):
        """Check if email is properly configured"""
        return is_email_configured()
    
    def test_email_connection(self):
        """Test email connection"""
        if not self.is_configured():
            return False, "Email not configured. Please set EMAIL_PASSWORD environment variable."
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.quit()
            return True, "Email connection successful"
        except Exception as e:
            return False, f"Email connection failed: {str(e)}"

# Global email manager instance
email_manager = EmailManager()
