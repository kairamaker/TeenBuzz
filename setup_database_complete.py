#!/usr/bin/env python3

import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

print("=== TeenBuzz Complete Database Setup ===")
print()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print(f"Connecting to: {SUPABASE_URL}")
print(f"Using key: {SUPABASE_KEY[:20]}...")
print()

# Test connection with retries
def test_connection(max_retries=5, delay=30):
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}: Testing connection...")
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            
            # Test with a simple query
            result = supabase.table('pg_tables').select('*').limit(1).execute()
            print("✅ Connection successful!")
            return supabase
            
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Waiting {delay} seconds before retry...")
                time.sleep(delay)
            else:
                print("❌ All connection attempts failed")
                return None

# Create all necessary tables
def create_tables(supabase):
    print("\n=== Creating Database Tables ===")
    
    # SQL commands for all tables
    tables_sql = [
        # Users table
        """
        CREATE TABLE IF NOT EXISTS users (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Articles table
        """
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            headline TEXT NOT NULL,
            content TEXT NOT NULL,
            category VARCHAR(100) NOT NULL,
            source VARCHAR(255),
            url TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            drawn_by_user_id UUID REFERENCES users(id),
            publish_date DATE,
            tags TEXT[],
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0
        );
        """,
        
        # User draws table
        """
        CREATE TABLE IF NOT EXISTS user_draws (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES users(id) NOT NULL,
            article_id INTEGER REFERENCES articles(id) NOT NULL,
            drawn_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(user_id, article_id)
        );
        """,
        
        # Categories table
        """
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            icon VARCHAR(50),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Password reset tokens table
        """
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES users(id) NOT NULL,
            token VARCHAR(255) UNIQUE NOT NULL,
            expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # User preferences table
        """
        CREATE TABLE IF NOT EXISTS user_preferences (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES users(id) UNIQUE NOT NULL,
            topics TEXT[],
            categories TEXT[],
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
    ]
    
    # Execute table creation
    for i, sql in enumerate(tables_sql, 1):
        try:
            print(f"Creating table {i}/{len(tables_sql)}...")
            supabase.rpc('exec_sql', {'sql': sql}).execute()
            print(f"✅ Table {i} created successfully")
        except Exception as e:
            print(f"❌ Error creating table {i}: {e}")
    
    print("\n=== Creating Indexes ===")
    
    # Create indexes for better performance
    indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);",
        "CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_articles_drawn_by ON articles(drawn_by_user_id);",
        "CREATE INDEX IF NOT EXISTS idx_user_draws_user_id ON user_draws(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_user_draws_article_id ON user_draws(article_id);",
        "CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(token);",
        "CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);"
    ]
    
    for i, sql in enumerate(indexes_sql, 1):
        try:
            print(f"Creating index {i}/{len(indexes_sql)}...")
            supabase.rpc('exec_sql', {'sql': sql}).execute()
            print(f"✅ Index {i} created successfully")
        except Exception as e:
            print(f"❌ Error creating index {i}: {e}")

# Insert sample data
def insert_sample_data(supabase):
    print("\n=== Inserting Sample Data ===")
    
    # Insert categories
    categories = [
        {"name": "Technology", "description": "Latest tech news and innovations", "icon": "fas fa-laptop-code"},
        {"name": "Environment", "description": "Climate and environmental news", "icon": "fas fa-leaf"},
        {"name": "Health", "description": "Health and wellness topics", "icon": "fas fa-heartbeat"},
        {"name": "Social Issues", "description": "Social justice and community topics", "icon": "fas fa-users"},
        {"name": "Science", "description": "Scientific discoveries and research", "icon": "fas fa-flask"}
    ]
    
    try:
        for category in categories:
            supabase.table('categories').insert(category).execute()
        print("✅ Categories inserted successfully")
    except Exception as e:
        print(f"❌ Error inserting categories: {e}")
    
    # Insert sample articles
    sample_articles = [
        {
            "headline": "New AI Tools Help Students Study Smarter, Not Harder",
            "content": "Students are discovering how artificial intelligence can revolutionize their study habits. From personalized learning plans to instant homework help, AI is making education more accessible and effective for teens everywhere. These tools are changing how students approach learning, making complex subjects more digestible and study sessions more efficient.",
            "category": "Technology",
            "source": "TechCrunch",
            "tags": ["AI", "education", "technology", "students", "learning"],
            "views": 1250,
            "likes": 89
        },
        {
            "headline": "Climate Change: What Teens Can Do to Make a Real Difference",
            "content": "Young activists are leading the charge against climate change with innovative solutions and powerful voices. Learn about the practical steps you can take to protect our planet and inspire others to join the movement. From school strikes to social media campaigns, teens are proving that age is just a number when it comes to environmental action.",
            "category": "Environment",
            "source": "BBC News",
            "tags": ["climate", "environment", "activism", "sustainability", "youth"],
            "views": 980,
            "likes": 76
        },
        {
            "headline": "Mental Health Apps That Actually Help Teens Cope",
            "content": "New mental health resources designed specifically for teenagers are making it easier to find support and build resilience. These apps offer everything from meditation guides to crisis support, helping teens navigate the challenges of modern life with better mental health tools and resources.",
            "category": "Health",
            "source": "NPR",
            "tags": ["mental health", "apps", "wellness", "teenagers", "support"],
            "views": 850,
            "likes": 64
        },
        {
            "headline": "The Future of Social Media: What Teens Need to Know",
            "content": "Social media platforms are evolving rapidly, and teens are at the forefront of these changes. From new privacy features to emerging platforms, understanding these shifts can help you navigate the digital world more safely and effectively.",
            "category": "Technology",
            "source": "Wired",
            "tags": ["social media", "privacy", "technology", "digital", "platforms"],
            "views": 720,
            "likes": 58
        },
        {
            "headline": "How Gen Z is Redefining Success in the Workplace",
            "content": "Young people are changing what it means to have a successful career, prioritizing work-life balance, mental health, and meaningful work over traditional corporate ladders. This shift is reshaping entire industries and creating new opportunities.",
            "category": "Social Issues",
            "source": "Forbes",
            "tags": ["career", "workplace", "gen z", "success", "work-life balance"],
            "views": 680,
            "likes": 52
        },
        {
            "headline": "The Science Behind Why Music Moves Us",
            "content": "New research reveals how music affects our brains and emotions, especially during teenage years. Understanding these connections can help you use music more effectively for studying, relaxation, and emotional regulation.",
            "category": "Science",
            "source": "Scientific American",
            "tags": ["music", "science", "brain", "emotions", "research"],
            "views": 590,
            "likes": 45
        }
    ]
    
    try:
        for article in sample_articles:
            supabase.table('articles').insert(article).execute()
        print("✅ Sample articles inserted successfully")
    except Exception as e:
        print(f"❌ Error inserting articles: {e}")

# Create admin user
def create_admin_user(supabase):
    print("\n=== Creating Admin User ===")
    
    admin_user = {
        "username": "admin",
        "email": "admin@teenbuzz.com",
        "password_hash": "admin123",  # In production, this should be hashed
        "is_admin": True
    }
    
    try:
        supabase.table('users').insert(admin_user).execute()
        print("✅ Admin user created successfully")
        print("   Username: admin")
        print("   Email: admin@teenbuzz.com")
        print("   Password: admin123")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

# Main execution
if __name__ == "__main__":
    print("Starting database setup...")
    print("This may take a few minutes due to DNS propagation...")
    print()
    
    # Test connection
    supabase = test_connection()
    
    if supabase:
        # Create tables
        create_tables(supabase)
        
        # Insert sample data
        insert_sample_data(supabase)
        
        # Create admin user
        create_admin_user(supabase)
        
        print("\n🎉 Database setup complete!")
        print("Your TeenBuzz app should now work with real data!")
        
    else:
        print("\n❌ Could not connect to database")
        print("Please try again in a few minutes when DNS propagation completes")
        print("Or try using a different network/VPN")
