#!/usr/bin/env python3
"""
Script to test Perplexity API key
"""

import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

def test_perplexity_api():
    """Test if the Perplexity API key is working"""
    
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    print("🔍 Testing Perplexity API Configuration...")
    print(f"API Key found: {'Yes' if api_key else 'No'}")
    
    if not api_key:
        print("❌ No API key found in .env file")
        return False
    
    if api_key.startswith('your_') or api_key == 'your_perplexity_api_key_here':
        print("❌ API key is still set to placeholder value")
        print("Please update your .env file with your actual Perplexity API key")
        return False
    
    print(f"API Key starts with: {api_key[:10]}...")
    
    # Test the API
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'llama-3.1-sonar-small-128k-online',
            'messages': [
                {'role': 'user', 'content': 'Hello, this is a test message. Please respond with "API is working!"'}
            ]
        }
        
        print("🔄 Testing API connection...")
        response = requests.post('https://api.perplexity.ai/chat/completions', 
                               headers=headers, json=data)
        
        if response.status_code == 200:
            print("✅ Perplexity API is working!")
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"Response: {content}")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")
        return False

if __name__ == "__main__":
    test_perplexity_api() 