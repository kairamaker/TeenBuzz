#!/usr/bin/env python3
"""
Detailed API debugging
"""

import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

api_key = os.getenv('PERPLEXITY_API_KEY')

print("🔍 Detailed API Debug:")
print(f"API Key length: {len(api_key) if api_key else 0}")
print(f"API Key starts with: {api_key[:15] if api_key else 'None'}...")

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

print(f"\n📤 Request Headers:")
for key, value in headers.items():
    if key == 'Authorization':
        print(f"  {key}: Bearer {api_key[:15]}..." if api_key else f"  {key}: None")
    else:
        print(f"  {key}: {value}")

data = {
    'model': 'llama-3.1-sonar-small-128k-online',
    'messages': [
        {'role': 'user', 'content': 'Hello'}
    ]
}

print(f"\n📤 Request Data:")
print(json.dumps(data, indent=2))

try:
    print(f"\n🔄 Making request...")
    response = requests.post('https://api.perplexity.ai/chat/completions', 
                           headers=headers, json=data, timeout=10)
    
    print(f"📥 Response Status: {response.status_code}")
    print(f"📥 Response Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    
    print(f"\n📥 Response Body:")
    print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
    
except Exception as e:
    print(f"❌ Exception: {e}")
    print(f"Exception type: {type(e)}") 