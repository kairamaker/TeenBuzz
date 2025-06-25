#!/usr/bin/env python3
"""
Test Perplexity API with exact requirements
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_perplexity_api():
    """Test Perplexity API with exact requirements"""
    
    # Get API key
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        print("❌ No API key found")
        return False
    
    print(f"🔍 Testing with API key: {api_key[:20]}...")
    
    # API endpoint
    url = "https://api.perplexity.ai/chat/completions"
    
    # Headers with API key
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # JSON payload with all required fields
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": "Say hello and confirm you're working."}
        ],
        "max_tokens": 100,
        "temperature": 0.5
    }
    
    print("📤 Making API request...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Make the API call
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Response: {result}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Perplexity API with exact requirements...")
    test_perplexity_api() 