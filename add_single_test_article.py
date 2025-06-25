#!/usr/bin/env python3
"""
Script to add one properly structured test article
"""

from app import supabase
from datetime import datetime

def add_test_article():
    """Add one properly structured test article"""
    
    test_article = {
        'headline': 'New Study Shows How Social Media Affects Teen Brain Development',
        'content': '''
        A groundbreaking new study from Stanford University has revealed some eye-opening facts about how social media affects your brain development. 
        The research, which followed over 1,000 teenagers for three years, found that the way you use social media can actually change how your brain works.
        
        Here's what the scientists discovered: teens who spent more than three hours a day on social media showed different patterns of brain activity compared to those who used it less. 
        The heavy social media users had more activity in the parts of the brain that respond to social rewards - basically, your brain gets really excited about likes and comments.
        
        "It's like your brain is being trained to crave social validation," explains Dr. Sarah Chen, one of the study's lead researchers. 
        "When you get a like or a comment, your brain releases dopamine, which is the same chemical that makes you feel good when you eat chocolate or win a game."
        
        But here's the interesting part: the study also found that this isn't necessarily bad. Social media can actually help you develop important social skills and stay connected with friends. 
        The key is finding the right balance and being mindful about how you're using it.
        
        The researchers recommend setting time limits, taking regular breaks, and being intentional about what you're consuming online. 
        They also suggest using social media to connect with real friends rather than just scrolling through endless content.
        
        "Think of social media like junk food for your brain," says Dr. Chen. "A little bit is fine, but too much can have negative effects. 
        The goal is to use it in a way that makes you feel good and connected, not anxious or overwhelmed."
        
        This research is especially important for teens because your brain is still developing until your mid-20s. 
        The choices you make now about technology use can have long-lasting effects on how your brain develops.
        
        So next time you're about to spend hours scrolling through TikTok, remember: your brain is literally being shaped by what you're doing. 
        Make sure you're shaping it in a way that will help you succeed in school, relationships, and life.
        ''',
        'source': 'Stanford University Research',
        'original_url': 'https://example.com/stanford-social-media-study',
        'category': 'Science',
        'relevance': 'This matters to teens because it shows how social media use can literally change your brain development and affect your future mental health.',
        'created_at': datetime.now().isoformat()
    }
    
    try:
        result = supabase.table('articles').insert(test_article).execute()
        print("✅ Successfully added test article!")
        print(f"Article ID: {result.data[0]['id']}")
        print(f"Headline: {test_article['headline']}")
        print(f"Category: {test_article['category']}")
        print(f"Original URL: {test_article['original_url']}")
        print("\nYou can now view this article at:")
        print("1. Homepage: http://localhost:8000/")
        print("2. Direct link: http://localhost:8000/article/[ID]")
        print("3. Admin panel: http://localhost:8000/admin")
        
    except Exception as e:
        print(f"❌ Error adding article: {str(e)}")

if __name__ == "__main__":
    print("Adding properly structured test article...")
    add_test_article() 