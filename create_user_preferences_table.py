#!/usr/bin/env python3
"""
Script to create user_preferences table in Supabase
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def create_user_preferences_table():
    """Create user_preferences table using Supabase REST API"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # SQL to create the table
    sql_commands = [
        """
        CREATE TABLE IF NOT EXISTS user_preferences (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            email TEXT UNIQUE,
            topics TEXT[] DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_user_preferences_email ON user_preferences(email);
        """,
        """
        ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
        """,
        """
        CREATE POLICY "Users can view their own preferences" ON user_preferences
            FOR SELECT USING (true);
        """,
        """
        CREATE POLICY "Users can insert their own preferences" ON user_preferences
            FOR INSERT WITH CHECK (true);
        """,
        """
        CREATE POLICY "Users can update their own preferences" ON user_preferences
            FOR UPDATE USING (true);
        """,
        """
        CREATE POLICY "Users can delete their own preferences" ON user_preferences
            FOR DELETE USING (true);
        """
    ]
    
    print("🔧 Creating user_preferences table...")
    
    for i, sql in enumerate(sql_commands, 1):
        try:
            # Use the SQL endpoint
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
                headers=headers,
                json={"sql": sql}
            )
            
            if response.status_code == 200:
                print(f"✅ Command {i} executed successfully")
            else:
                print(f"⚠️ Command {i} failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Command {i} error: {e}")
    
    print("\n📋 Manual SQL Commands (if automatic creation fails):")
    print("=" * 50)
    for sql in sql_commands:
        print(sql.strip())
        print()

if __name__ == "__main__":
    create_user_preferences_table()
