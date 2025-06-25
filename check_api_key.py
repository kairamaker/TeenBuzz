#!/usr/bin/env python3
"""
Check API key format
"""

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('PERPLEXITY_API_KEY')

print("🔍 API Key Analysis:")
print(f"Length: {len(api_key) if api_key else 0} characters")
print(f"Starts with: {api_key[:10] if api_key else 'None'}...")
print(f"Ends with: ...{api_key[-4:] if api_key and len(api_key) > 4 else 'None'}")

if api_key:
    if len(api_key) < 50:
        print("❌ API key seems too short")
    elif not api_key.startswith('sk-proj-'):
        print("❌ API key doesn't start with 'sk-proj-'")
    else:
        print("✅ API key format looks correct")
else:
    print("❌ No API key found") 