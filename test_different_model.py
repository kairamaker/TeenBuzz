#!/usr/bin/env python3
"""
Test different Perplexity models
"""

import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv('PERPLEXITY_API_KEY')

models_to_test = [
    'llama-3.1-sonar-small-128k-online',
    'llama-3.1-sonar-small-128k',
    'llama-3.1-sonar-medium-128k-online',
    'llama-3.1-sonar-medium-128k',
    'sonar-small-online',
    'sonar-small-chat',
    'sonar-medium-online',
    'sonar-medium-chat'
]

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

for model in models_to_test:
    print(f"\n🧪 Testing model: {model}")
    
    data = {
        'model': model,
        'messages': [
            {'role': 'user', 'content': 'Hello'}
        ]
    }
    
    try:
        response = requests.post('https://api.perplexity.ai/chat/completions', 
                               headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ SUCCESS with {model}!")
            break
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}") 