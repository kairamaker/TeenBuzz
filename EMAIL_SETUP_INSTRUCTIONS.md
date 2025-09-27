# 📧 Email Setup Instructions

## **Why Password Reset Shows "Gibberish"**

The password reset is showing a token instead of sending an email because the email system isn't configured yet.

## **Quick Fix (5 minutes):**

### **1. Set Up Gmail App Password**
1. Go to https://myaccount.google.com/security
2. Enable 2-Factor Authentication if not already enabled
3. Go to https://myaccount.google.com/apppasswords
4. Generate a new app password for "TeenBuzz"
5. Copy the 16-character password

### **2. Configure Email**
```bash
# Option 1: Set environment variable
export EMAIL_PASSWORD='your-16-character-app-password'

# Option 2: Add to .env file
echo "EMAIL_PASSWORD=your-16-character-app-password" >> .env
```

### **3. Test Email System**
```bash
cd /Users/kairaschool/Downloads/TeenBuzz
source teenbuzz_env/bin/activate
python test_email.py
```

### **4. Restart Application**
```bash
# Stop current server (Ctrl+C)
# Then restart:
source teenbuzz_env/bin/activate
python app_with_auth.py
```

## **After Setup:**
- Password reset will send real emails instead of showing tokens
- Users will receive proper password reset emails
- No more "gibberish" on the login page

## **Alternative: Disable Password Reset**
If you don't want to set up email, we can disable the password reset feature entirely.
