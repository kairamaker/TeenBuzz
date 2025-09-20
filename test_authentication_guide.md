# 🧪 TeenBuzz Authentication Testing Guide

## **Quick Test URLs**

Your app is running at: **http://localhost:5003**

### **1. Basic Navigation Test**
- **Homepage**: http://localhost:5003/
- **Login**: http://localhost:5003/login
- **Register**: http://localhost:5003/register
- **Search**: http://localhost:5003/search
- **Trending**: http://localhost:5003/trending
- **Categories**: http://localhost:5003/categories

### **2. Authentication Flow Test**

#### **Step 1: Test Registration**
1. Go to http://localhost:5003/register
2. Try these test cases:

**✅ Valid Registration:**
- Username: `testuser123`
- Email: `test@example.com`
- Password: `TestPass123!`
- Confirm Password: `TestPass123!`

**❌ Invalid Registration Tests:**
- Username too short: `ab`
- Invalid email: `invalid-email`
- Weak password: `weak`
- Mismatched passwords: `TestPass123!` vs `DifferentPass123!`

#### **Step 2: Test Login**
1. Go to http://localhost:5003/login
2. Try logging in with:
- Username: `testuser123` OR Email: `test@example.com`
- Password: `TestPass123!`
- Check "Remember me" option

#### **Step 3: Test Authenticated Features**
After login, test:
- **Profile Page**: http://localhost:5003/profile
- **Change Password**: http://localhost:5003/change-password
- **Admin Panel** (if admin): http://localhost:5003/admin

#### **Step 4: Test Logout**
1. Click logout from profile page
2. Verify you're redirected to home
3. Try accessing protected pages (should redirect to login)

### **3. Admin Testing**

#### **Create Admin User**
Run this command to create an admin user:
```bash
python create_admin_user.py
```

Then login with:
- Username: `admin`
- Password: `AdminPass123!`

#### **Test Admin Features**
- **Admin Dashboard**: http://localhost:5003/admin
- **User Management**: http://localhost:5003/admin/users

### **4. Security Testing**

#### **Test Password Security**
1. Try weak passwords during registration
2. Test password change functionality
3. Verify old passwords don't work after change

#### **Test Session Security**
1. Login and check browser cookies
2. Logout and verify session is cleared
3. Try accessing protected pages without login

### **5. Database Testing**

#### **Check Database Contents**
```bash
sqlite3 teenbuzz_local.db "SELECT * FROM users;"
```

#### **Verify Password Hashing**
```bash
sqlite3 teenbuzz_local.db "SELECT username, password_hash FROM users;"
```

## **Automated Testing Scripts**

### **Run Authentication Tests**
```bash
python test_auth_simple.py
```

### **Run Full System Test**
```bash
python test_full_system.py
```

## **Expected Results**

### **✅ Success Indicators**
- Registration creates user with hashed password
- Login works with username or email
- Protected pages redirect to login when not authenticated
- Admin features only accessible to admin users
- Passwords are properly hashed in database
- Sessions work correctly
- Logout clears session

### **❌ Failure Indicators**
- Plain text passwords in database
- Access to protected pages without login
- Admin features accessible to regular users
- Session not cleared on logout
- Validation errors not showing

## **Troubleshooting**

### **Common Issues**
1. **"Working outside of request context"** - Use `app_with_auth.py` for web testing
2. **Database errors** - Check if `teenbuzz_local.db` exists
3. **Template errors** - Verify all templates are updated
4. **Import errors** - Ensure virtual environment is activated

### **Debug Commands**
```bash
# Check if app is running
curl http://localhost:5003

# Check database
sqlite3 teenbuzz_local.db ".tables"

# Check logs
tail -f app.log  # if logging is enabled
```

## **Performance Testing**

### **Load Testing**
```bash
# Test multiple concurrent requests
for i in {1..10}; do curl http://localhost:5003/login & done
```

### **Database Performance**
```bash
# Test database queries
python test_database_performance.py
```

## **Security Checklist**

- [ ] Passwords are hashed with bcrypt
- [ ] SQL injection prevention (parameterized queries)
- [ ] Session security (proper cleanup)
- [ ] Input validation on all forms
- [ ] Admin routes protected
- [ ] CSRF protection (if implemented)
- [ ] Rate limiting (if implemented)

## **Next Steps After Testing**

1. **Email Integration** - Set up SMTP for password reset
2. **Two-Factor Authentication** - Add 2FA support
3. **Social Login** - Google/Facebook OAuth
4. **Advanced Admin Features** - User management, analytics
5. **API Endpoints** - REST API for mobile apps
