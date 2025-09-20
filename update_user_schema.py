#!/usr/bin/env python3
"""
Update user schema to include missing columns for enhanced authentication
"""

import sqlite3
from database_manager import get_database

def update_user_schema():
    """Add missing columns to users table"""
    print("🔄 Updating user schema for enhanced authentication...")
    
    try:
        # Get database connection
        db = get_database()
        if not db:
            print("❌ Could not connect to database")
            return False
        
        # Add missing columns
        columns_to_add = [
            "ALTER TABLE users ADD COLUMN last_login TIMESTAMP",
            "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1"
        ]
        
        for column_sql in columns_to_add:
            try:
                db.execute_query(column_sql)
                print(f"✅ Added column: {column_sql}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"⚠️  Column already exists: {column_sql}")
                else:
                    print(f"❌ Error adding column: {e}")
        
        # Verify the updated schema
        print("\n📋 Updated users table schema:")
        try:
            schema = db.execute_query("PRAGMA table_info(users)")
            for column in schema:
                print(f"  - {column[1]} ({column[2]})")
        except Exception as e:
            print(f"  Could not retrieve schema: {e}")
        
        print("\n✅ User schema update complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        return False

if __name__ == "__main__":
    update_user_schema()
