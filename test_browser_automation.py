#!/usr/bin/env python3
"""
Browser automation test for TeenBuzz authentication
Requires: pip install selenium
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_with_selenium():
    """Test authentication with browser automation"""
    print("🌐 Testing with Browser Automation")
    print("=" * 40)
    
    # Check if app is running
    try:
        response = requests.get("http://localhost:5003", timeout=3)
        if response.status_code != 200:
            print("❌ App is not running. Start it with: python app_with_auth.py")
            return
    except requests.exceptions.RequestException:
        print("❌ App is not running. Start it with: python app_with_auth.py")
        return
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)
        
        base_url = "http://localhost:5003"
        
        # Test 1: Homepage
        print("1. Testing Homepage...")
        driver.get(base_url)
        title = driver.title
        print(f"   ✅ Homepage loaded: {title}")
        
        # Test 2: Login page
        print("\n2. Testing Login Page...")
        driver.get(f"{base_url}/login")
        wait = WebDriverWait(driver, 10)
        
        # Check if login form exists
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = driver.find_element(By.NAME, "password")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        print("   ✅ Login form elements found")
        
        # Test 3: Registration page
        print("\n3. Testing Registration Page...")
        driver.get(f"{base_url}/register")
        
        # Check if registration form exists
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        confirm_password_field = driver.find_element(By.NAME, "confirm_password")
        
        print("   ✅ Registration form elements found")
        
        # Test 4: Search page
        print("\n4. Testing Search Page...")
        driver.get(f"{base_url}/search")
        search_input = wait.until(EC.presence_of_element_located((By.NAME, "q")))
        print("   ✅ Search form found")
        
        # Test 5: Navigation
        print("\n5. Testing Navigation...")
        nav_links = driver.find_elements(By.CSS_SELECTOR, ".nav-link")
        print(f"   ✅ Found {len(nav_links)} navigation links")
        
        # Test 6: Authentication flow (if user exists)
        print("\n6. Testing Authentication Flow...")
        driver.get(f"{base_url}/login")
        
        # Try to login with test user
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys("testuser_web")
        password_field.send_keys("TestPass123!")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Wait for redirect
        time.sleep(2)
        
        current_url = driver.current_url
        if "profile" in current_url or "home" in current_url:
            print("   ✅ Login successful - redirected to protected page")
        else:
            print(f"   ⚠️ Login result unclear - current URL: {current_url}")
        
        driver.quit()
        print("\n🎉 Browser automation test complete!")
        
    except Exception as e:
        print(f"❌ Browser test failed: {e}")
        print("💡 Make sure you have Chrome and ChromeDriver installed")
        print("   Install with: pip install selenium")

def test_without_selenium():
    """Test without browser automation"""
    print("🌐 Testing Web Interface (No Browser)")
    print("=" * 40)
    
    base_url = "http://localhost:5003"
    endpoints = [
        ("/", "Homepage"),
        ("/login", "Login Page"),
        ("/register", "Register Page"),
        ("/search", "Search Page"),
        ("/trending", "Trending Page"),
        ("/categories", "Categories Page"),
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                # Check for key elements in HTML
                html = response.text
                if "TeenBuzz" in html:
                    print(f"   ✅ {name}: Loaded successfully")
                else:
                    print(f"   ⚠️ {name}: Loaded but missing content")
            else:
                print(f"   ❌ {name}: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {name}: Connection failed")
    
    print("\n📋 Manual Testing Steps:")
    print("1. Open browser and go to http://localhost:5003")
    print("2. Test registration with: testuser123 / test@example.com / TestPass123!")
    print("3. Test login with the same credentials")
    print("4. Check profile page and logout functionality")
    print("5. Test admin features (create admin user first)")

if __name__ == "__main__":
    try:
        test_with_selenium()
    except ImportError:
        print("⚠️ Selenium not installed. Running basic web test...")
        test_without_selenium()
    except Exception as e:
        print(f"⚠️ Selenium test failed: {e}")
        test_without_selenium()
