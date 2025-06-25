#!/usr/bin/env python3
"""
Script to manually add a test article to TeenBuzz database
"""

from app import supabase
from datetime import datetime

def add_test_article():
    """Add a sample article to test the interface"""
    
    test_article = {
        'headline': 'New Social Media App Takes High Schools by Storm',
        'content': '''
        A new social media platform called "StudyBuddy" is becoming the talk of high schools across the country! 
        Unlike other apps that can be distracting, this one actually helps you study and connect with classmates.
        
        The app lets you form study groups, share notes, and even has a feature that blocks notifications during study sessions. 
        Teachers are loving it because students are actually using their phones for learning instead of just scrolling through memes.
        
        "It's like having a study group in your pocket," says 16-year-old Sarah from California. "I've made so many new friends 
        and my grades have actually improved since I started using it."
        
        The app was created by a group of college students who remembered how hard it was to stay focused while studying. 
        They wanted to create something that would help teens like you succeed in school while still being fun to use.
        ''',
        'source': 'TeenBuzz News',
        'category': 'Technology',
        'relevance': 'This matters to teens because it shows how technology can actually help with schoolwork and social connections.',
        'created_at': datetime.now().isoformat()
    }
    
    try:
        result = supabase.table('articles').insert(test_article).execute()
        print("✅ Successfully added test article!")
        print(f"Article ID: {result.data[0]['id']}")
        print(f"Headline: {test_article['headline']}")
        print(f"Category: {test_article['category']}")
        print("\nYou can now view this article at:")
        print("1. Homepage: http://localhost:8000/")
        print("2. Direct link: http://localhost:8000/article/[ID]")
        print("3. Admin panel: http://localhost:8000/admin")
        
    except Exception as e:
        print(f"❌ Error adding article: {str(e)}")

if __name__ == "__main__":
    print("Adding test article to TeenBuzz database...")
    add_test_article() 