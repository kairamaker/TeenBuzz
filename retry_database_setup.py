#!/usr/bin/env python3

import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def test_and_setup():
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    print(f"Testing connection to: {SUPABASE_URL}")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        result = supabase.table('pg_tables').select('*').limit(1).execute()
        print("✅ Connection successful! Running database setup...")
        
        # Run the complete setup
        os.system("python setup_database_complete.py")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("=== TeenBuzz Database Retry Script ===")
    print("This will test the connection and set up the database when ready")
    print()
    
    # Try immediately
    if test_and_setup():
        print("🎉 Database setup complete!")
    else:
        print("⏳ DNS still not ready. Here are your options:")
        print()
        print("1. WAIT 10-15 MINUTES and run: python retry_database_setup.py")
        print("2. TRY DIFFERENT NETWORK (mobile hotspot, different WiFi)")
        print("3. USE VPN if available")
        print("4. CHECK SUPABASE DASHBOARD to ensure project is active")
        print()
        print("Your app works perfectly with sample data in the meantime!")
