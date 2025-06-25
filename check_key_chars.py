#!/usr/bin/env python3
"""
Check for hidden characters in API key
"""

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('PERPLEXITY_API_KEY')

print("🔍 API Key Character Analysis:")
print(f"Length: {len(api_key)}")
print(f"Raw key: {repr(api_key)}")
print(f"First 20 chars: {repr(api_key[:20])}")
print(f"Last 20 chars: {repr(api_key[-20:])}")

# Check for common issues
if api_key:
    if api_key.startswith('"') and api_key.endswith('"'):
        print("⚠️  Key has quotes - removing them...")
        api_key = api_key.strip('"')
    if api_key.startswith("'") and api_key.endswith("'"):
        print("⚠️  Key has single quotes - removing them...")
        api_key = api_key.strip("'")
    
    # Check for whitespace
    if api_key != api_key.strip():
        print("⚠️  Key has leading/trailing whitespace")
        api_key = api_key.strip()
    
    print(f"Cleaned key: {repr(api_key)}") 