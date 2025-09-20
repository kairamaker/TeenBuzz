#!/usr/bin/env python3

import sqlite3
import os
from datetime import datetime

def create_local_database():
    """Create a local SQLite database with all the same tables as Supabase"""
    
    # Create database file
    db_path = 'teenbuzz_local.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed existing local database")
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Creating local SQLite database...")
    
    # 1. Create Users Table
    cursor.execute('''
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Create Articles Table
    cursor.execute('''
        CREATE TABLE articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            source TEXT,
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            drawn_by_user_id TEXT,
            publish_date DATE,
            tags TEXT,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            FOREIGN KEY (drawn_by_user_id) REFERENCES users(id)
        )
    ''')
    
    # 3. Create User Draws Table
    cursor.execute('''
        CREATE TABLE user_draws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            article_id INTEGER NOT NULL,
            drawn_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (article_id) REFERENCES articles(id),
            UNIQUE(user_id, article_id)
        )
    ''')
    
    # 4. Create Categories Table
    cursor.execute('''
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            icon TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 5. Create Password Reset Tokens Table
    cursor.execute('''
        CREATE TABLE password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 6. Create User Preferences Table
    cursor.execute('''
        CREATE TABLE user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            topics TEXT,
            categories TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    print("✅ All tables created successfully")
    
    # Insert sample data
    print("Inserting sample data...")
    
    # Insert categories
    categories = [
        ('Technology', 'Latest tech news and innovations', 'fas fa-laptop-code'),
        ('Environment', 'Climate and environmental news', 'fas fa-leaf'),
        ('Health', 'Health and wellness topics', 'fas fa-heartbeat'),
        ('Social Issues', 'Social justice and community topics', 'fas fa-users'),
        ('Science', 'Scientific discoveries and research', 'fas fa-flask')
    ]
    
    cursor.executemany('''
        INSERT INTO categories (name, description, icon) VALUES (?, ?, ?)
    ''', categories)
    
    # Insert sample articles
    articles = [
        ('New AI Tools Help Students Study Smarter, Not Harder', 
         'Students are discovering how artificial intelligence can revolutionize their study habits. From personalized learning plans to instant homework help, AI is making education more accessible and effective for teens everywhere. These tools are changing how students approach learning, making complex subjects more digestible and study sessions more efficient.',
         'Technology', 'TechCrunch', 'AI,education,technology,students,learning', 1250, 89),
        
        ('Climate Change: What Teens Can Do to Make a Real Difference',
         'Young activists are leading the charge against climate change with innovative solutions and powerful voices. Learn about the practical steps you can take to protect our planet and inspire others to join the movement. From school strikes to social media campaigns, teens are proving that age is just a number when it comes to environmental action.',
         'Environment', 'BBC News', 'climate,environment,activism,sustainability,youth', 980, 76),
        
        ('Mental Health Apps That Actually Help Teens Cope',
         'New mental health resources designed specifically for teenagers are making it easier to find support and build resilience. These apps offer everything from meditation guides to crisis support, helping teens navigate the challenges of modern life with better mental health tools and resources.',
         'Health', 'NPR', 'mental health,apps,wellness,teenagers,support', 850, 64),
        
        ('The Future of Social Media: What Teens Need to Know',
         'Social media platforms are evolving rapidly, and teens are at the forefront of these changes. From new privacy features to emerging platforms, understanding these shifts can help you navigate the digital world more safely and effectively.',
         'Technology', 'Wired', 'social media,privacy,technology,digital,platforms', 720, 58),
        
        ('How Gen Z is Redefining Success in the Workplace',
         'Young people are changing what it means to have a successful career, prioritizing work-life balance, mental health, and meaningful work over traditional corporate ladders. This shift is reshaping entire industries and creating new opportunities.',
         'Social Issues', 'Forbes', 'career,workplace,gen z,success,work-life balance', 680, 52),
        
        ('The Science Behind Why Music Moves Us',
         'New research reveals how music affects our brains and emotions, especially during teenage years. Understanding these connections can help you use music more effectively for studying, relaxation, and emotional regulation.',
         'Science', 'Scientific American', 'music,science,brain,emotions,research', 590, 45)
    ]
    
    cursor.executemany('''
        INSERT INTO articles (headline, content, category, source, tags, views, likes) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', articles)
    
    # Insert admin user
    import uuid
    admin_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO users (id, username, email, password_hash, is_admin) 
        VALUES (?, ?, ?, ?, ?)
    ''', (admin_id, 'admin', 'admin@teenbuzz.com', 'admin123', 1))
    
    # Commit changes
    conn.commit()
    
    # Verify data
    cursor.execute('SELECT COUNT(*) FROM articles')
    article_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM categories')
    category_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    
    print(f"✅ Sample data inserted:")
    print(f"   - {article_count} articles")
    print(f"   - {category_count} categories")
    print(f"   - {user_count} users")
    
    conn.close()
    
    print(f"\n🎉 Local database created successfully: {db_path}")
    print("You can now use the local database instead of Supabase!")

if __name__ == "__main__":
    create_local_database()
