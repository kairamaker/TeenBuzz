#!/usr/bin/env python3
"""
Check for similar articles that might be duplicates
"""

import os
from dotenv import load_dotenv
from supabase.client import create_client
from difflib import SequenceMatcher

# Load environment variables
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def similarity(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def check_similar_articles():
    """Check for articles with similar headlines"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Get all articles
        result = supabase.table('articles').select('*').order('created_at', desc=True).execute()
        articles = result.data or []
        
        print(f"📊 Found {len(articles)} articles")
        print("🔍 Checking for similar articles...")
        
        similar_pairs = []
        
        # Compare each article with others
        for i, article1 in enumerate(articles):
            for j, article2 in enumerate(articles[i+1:], i+1):
                headline1 = article1['headline'].strip()
                headline2 = article2['headline'].strip()
                
                # Calculate similarity
                sim_ratio = similarity(headline1, headline2)
                
                # If similarity is high (> 0.8), they might be duplicates
                if sim_ratio > 0.8:
                    similar_pairs.append({
                        'article1': article1,
                        'article2': article2,
                        'similarity': sim_ratio
                    })
        
        if not similar_pairs:
            print("✅ No similar articles found!")
            return True
        
        print(f"\n🔍 Found {len(similar_pairs)} similar article pairs:")
        print("-" * 60)
        
        for i, pair in enumerate(similar_pairs, 1):
            article1 = pair['article1']
            article2 = pair['article2']
            sim_ratio = pair['similarity']
            
            print(f"Pair {i} (Similarity: {sim_ratio:.2f}):")
            print(f"  Article 1 (ID: {article1['id']}): {article1['headline']}")
            print(f"  Article 2 (ID: {article2['id']}): {article2['headline']}")
            print(f"  Source 1: {article1['source']}")
            print(f"  Source 2: {article2['source']}")
            print(f"  Created 1: {article1['created_at']}")
            print(f"  Created 2: {article2['created_at']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error in check_similar_articles: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting TeenBuzz Similar Article Check...")
    check_similar_articles() 