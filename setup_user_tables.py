#!/usr/bin/env python3
"""
Script to set up user authentication tables in TeenBuzz database
"""

import os
from dotenv import load_dotenv
from supabase.client import create_client
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def setup_user_tables():
    """Set up user authentication tables"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Create users table
        print("📝 Creating users table...")
        users_table_sql = """
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
        supabase.rpc('exec_sql', {'sql': users_table_sql}).execute()
        print("✅ Users table created")
        
        # Add drawn_by_user_id column to articles table
        print("📝 Adding user tracking to articles table...")
        alter_articles_sql = """
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS drawn_by_user_id BIGINT REFERENCES users(id);
        """
        supabase.rpc('exec_sql', {'sql': alter_articles_sql}).execute()
        print("✅ Articles table updated")
        
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
        supabase.rpc('exec_sql', {'sql': user_draws_sql}).execute()
        print("✅ User draws table created")
        
        # Create indexes
        print("📝 Creating indexes...")
        indexes_sql = """
        CREATE INDEX IF NOT EXISTS idx_articles_drawn_by ON articles(drawn_by_user_id);
        CREATE INDEX IF NOT EXISTS idx_user_draws_user_id ON user_draws(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_draws_drawn_at ON user_draws(drawn_at DESC);
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        """
        supabase.rpc('exec_sql', {'sql': indexes_sql}).execute()
        print("✅ Indexes created")
        
        # Enable RLS
        print("📝 Enabling Row Level Security...")
        rls_sql = """
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;
        ALTER TABLE user_draws ENABLE ROW LEVEL SECURITY;
        """
        supabase.rpc('exec_sql', {'sql': rls_sql}).execute()
        print("✅ RLS enabled")
        
        # Create policies
        print("📝 Creating security policies...")
        policies_sql = """
        CREATE POLICY IF NOT EXISTS "Users can insert articles" ON articles FOR INSERT WITH CHECK (true);
        CREATE POLICY IF NOT EXISTS "Users can update their own articles" ON articles FOR UPDATE USING (true);
        CREATE POLICY IF NOT EXISTS "Users can insert draws" ON user_draws FOR INSERT WITH CHECK (true);
        CREATE POLICY IF NOT EXISTS "Users can view their own draws" ON user_draws FOR SELECT USING (true);
        """
        supabase.rpc('exec_sql', {'sql': policies_sql}).execute()
        print("✅ Security policies created")
        
        # Create default admin user
        print("📝 Creating default admin user...")
        admin_password_hash = generate_password_hash('admin123')
        admin_user = {
            'username': 'admin',
            'password_hash': admin_password_hash,
            'email': 'admin@teenbuzz.com',
            'is_admin': True
        }
        
        # Check if admin user already exists
        existing_admin = supabase.table('users').select('id').eq('username', 'admin').execute()
        if not existing_admin.data:
            supabase.table('users').insert(admin_user).execute()
            print("✅ Default admin user created (username: admin, password: admin123)")
        else:
            print("ℹ️  Admin user already exists")
        
        print("\n🎉 User authentication setup complete!")
        print("\n📋 Default admin credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n🔗 You can now:")
        print("   1. Register new users at /register")
        print("   2. Login at /login")
        print("   3. Users can draw articles from their profile page")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up user tables: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up TeenBuzz user authentication...")
    success = setup_user_tables()
    if success:
        print("\n✅ Setup completed successfully!")
    else:
        print("\n❌ Setup failed. Please check your configuration.") 