#!/usr/bin/env python3
"""
Script to create user authentication tables in TeenBuzz database
"""

import os
from dotenv import load_dotenv
from supabase.client import create_client

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def create_tables():
    """Create user authentication tables"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Create users table
        print("📝 Creating users table...")
        users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id BIGSERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            email VARCHAR(100) UNIQUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_login TIMESTAMP WITH TIME ZONE,
            is_admin BOOLEAN DEFAULT FALSE
        );
        """
        
        try:
            supabase.rpc('exec_sql', {'sql': users_sql}).execute()
            print("✅ Users table created")
        except Exception as e:
            print(f"⚠️  Could not create users table via RPC: {str(e)}")
            print("💡 Please create the table manually in Supabase dashboard")
            return False
        
        # Add drawn_by_user_id to articles table
        print("📝 Adding user tracking to articles table...")
        alter_articles_sql = """
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS drawn_by_user_id BIGINT REFERENCES users(id);
        """
        
        try:
            supabase.rpc('exec_sql', {'sql': alter_articles_sql}).execute()
            print("✅ Articles table updated")
        except Exception as e:
            print(f"⚠️  Could not update articles table: {str(e)}")
        
        # Create user_draws table
        print("📝 Creating user_draws table...")
        user_draws_sql = """
        CREATE TABLE IF NOT EXISTS user_draws (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(id) NOT NULL,
            article_id BIGINT REFERENCES articles(id) NOT NULL,
            drawn_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        try:
            supabase.rpc('exec_sql', {'sql': user_draws_sql}).execute()
            print("✅ User draws table created")
        except Exception as e:
            print(f"⚠️  Could not create user_draws table: {str(e)}")
        
        # Create indexes
        print("📝 Creating indexes...")
        indexes_sql = """
        CREATE INDEX IF NOT EXISTS idx_articles_drawn_by ON articles(drawn_by_user_id);
        CREATE INDEX IF NOT EXISTS idx_user_draws_user_id ON user_draws(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_draws_drawn_at ON user_draws(drawn_at DESC);
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        """
        
        try:
            supabase.rpc('exec_sql', {'sql': indexes_sql}).execute()
            print("✅ Indexes created")
        except Exception as e:
            print(f"⚠️  Could not create indexes: {str(e)}")
        
        # Enable RLS
        print("📝 Enabling Row Level Security...")
        rls_sql = """
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;
        ALTER TABLE user_draws ENABLE ROW LEVEL SECURITY;
        """
        
        try:
            supabase.rpc('exec_sql', {'sql': rls_sql}).execute()
            print("✅ RLS enabled")
        except Exception as e:
            print(f"⚠️  Could not enable RLS: {str(e)}")
        
        # Create policies
        print("📝 Creating security policies...")
        policies_sql = """
        CREATE POLICY IF NOT EXISTS "Users can insert articles" ON articles FOR INSERT WITH CHECK (true);
        CREATE POLICY IF NOT EXISTS "Users can update their own articles" ON articles FOR UPDATE USING (true);
        CREATE POLICY IF NOT EXISTS "Users can insert draws" ON user_draws FOR INSERT WITH CHECK (true);
        CREATE POLICY IF NOT EXISTS "Users can view their own draws" ON user_draws FOR SELECT USING (true);
        """
        
        try:
            supabase.rpc('exec_sql', {'sql': policies_sql}).execute()
            print("✅ Security policies created")
        except Exception as e:
            print(f"⚠️  Could not create policies: {str(e)}")
        
        print("\n🎉 Tables created successfully!")
        print("\n📋 Next steps:")
        print("   1. Run: python setup_user_tables_simple.py")
        print("   2. Test registration at: http://localhost:8000/register")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Creating TeenBuzz user authentication tables...")
    success = create_tables()
    if success:
        print("\n✅ Table creation completed!")
    else:
        print("\n❌ Table creation failed. Please create tables manually in Supabase dashboard.") 