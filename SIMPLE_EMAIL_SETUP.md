# 📧 Simple Email Setup for Password Reset

## **Current Status:**
- ✅ Password reset shows a dedicated page with the link
- ✅ Link expires in 1 hour for security
- ✅ Users can copy the link or open it directly

## **Option 1: Keep Current System (Recommended)**
- **Pros:** No email setup needed, works immediately
- **Cons:** User needs to copy the link manually
- **Best for:** Development and testing

## **Option 2: Enable Email System (5 minutes)**

### **Quick Gmail Setup:**
1. Go to https://myaccount.google.com/security
2. Enable 2-Factor Authentication
3. Go to https://myaccount.google.com/apppasswords
4. Generate app password for "TeenBuzz"
5. Copy the 16-character password

### **Set Environment Variable:**
```bash
export EMAIL_PASSWORD='your-16-character-app-password'
```

### **Test Email:**
```bash
cd /Users/kairaschool/Downloads/TeenBuzz
source teenbuzz_env/bin/activate
python test_email.py
```

### **Restart Application:**
```bash
# Stop current server (Ctrl+C)
source teenbuzz_env/bin/activate
python app_with_auth.py
```

## **After Email Setup:**
- Password reset will send real emails
- Users get email with reset link
- No need to copy links manually
- Professional user experience

## **Current Working System:**
- Password reset generates secure link
- Shows dedicated page with copy button
- Link expires in 1 hour
- Works without any email setup

**Choose what works best for you!** 🚀
