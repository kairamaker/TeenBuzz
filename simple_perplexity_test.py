#!/usr/bin/env python3
"""
Simple Perplexity API test
"""

import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv('PERPLEXITY_API_KEY')

print("Testing Perplexity API...")
print(f"API Key: {api_key[:15]}..." if api_key else "No API key")

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

data = {
    'model': 'sonar-pro',
    'messages': [
        {'role': 'user', 'content': 'Say hello'}
    ]
}

try:
    response = requests.post('https://api.perplexity.ai/chat/completions', 
                           headers=headers, json=data, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Response: {response.text[:200]}...")
    
except Exception as e:
    print(f"Error: {e}") 