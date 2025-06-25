#!/usr/bin/env python3
"""
Script to add multiple test articles to TeenBuzz database
"""

from app import supabase
from datetime import datetime

def add_multiple_articles():
    """Add several sample articles to test the interface"""
    
    articles = [
        {
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
            'relevance': 'This matters to teens because it shows how technology can actually help with schoolwork and social connections.'
        },
        {
            'headline': 'Climate Change Could Affect Your Future Career Choices',
            'content': '''
            Here's something that might surprise you: climate change isn't just about polar bears and melting ice caps. 
            It's actually going to change what jobs are available when you graduate from college.
            
            According to a new report, careers in renewable energy, environmental science, and sustainable technology are booming. 
            Companies are desperately looking for young people who understand green technology and want to make a difference.
            
            "I used to think climate change was something that would happen far in the future," says 17-year-old Marcus from Texas. 
            "But now I'm thinking about majoring in environmental engineering because I want to be part of the solution."
            
            The report shows that jobs in solar energy, wind power, and electric vehicle technology are growing three times faster 
            than traditional jobs. Even if you're not into science, there are opportunities in marketing, law, and business related to sustainability.
            
            This is your chance to not just get a good job, but to help save the planet while you're at it!
            ''',
            'source': 'TeenBuzz News',
            'category': 'Environment',
            'relevance': 'Teens need to understand how climate change will impact their future careers and opportunities.'
        },
        {
            'headline': 'New Study Shows Social Media Impact on Teen Mental Health',
            'content': '''
            A groundbreaking new study has revealed some surprising facts about how social media affects your brain and mental health. 
            The research followed thousands of teenagers for three years and found some eye-opening results.
            
            The good news? Social media isn't all bad. It can actually help you stay connected with friends and family, 
            especially during difficult times. Many teens reported feeling less lonely when they could chat with friends online.
            
            However, the study also found that spending more than three hours a day on social media was linked to higher levels of anxiety and depression. 
            The researchers think this might be because of the constant comparison with others' highlight reels.
            
            "I used to spend hours scrolling through Instagram and feeling like everyone else had a perfect life," says 15-year-old Emma. 
            "Now I limit myself to 30 minutes a day and I feel so much better about myself."
            
            The study's authors recommend setting time limits, following accounts that make you feel good, and remembering that 
            what you see online isn't always real life. Your mental health is way more important than getting the perfect selfie!
            ''',
            'source': 'TeenBuzz News',
            'category': 'Health',
            'relevance': 'Teens need to understand how social media affects their mental health and how to use it responsibly.'
        },
        {
            'headline': 'High School Students Create App to Fight Food Waste',
            'content': '''
            A group of high school students from Seattle has created an app that's helping reduce food waste in their community. 
            The app, called "SharePlate," connects people who have extra food with those who need it.
            
            The idea came when the students noticed how much food was being thrown away at school events and local restaurants. 
            They decided to do something about it and created an app that lets people post when they have leftover food to share.
            
            "We were shocked to learn that 40% of food in America goes to waste," says 16-year-old Priya, one of the app's creators. 
            "We wanted to create something that would help people share food instead of throwing it away."
            
            The app has been so successful that it's now being used in over 20 schools across the country. 
            Users can post photos of leftover food, set pickup times, and coordinate with others in their area.
            
            The students are now working with local food banks and restaurants to expand the app's reach. 
            They're proving that you don't have to wait until you're older to make a real difference in your community!
            ''',
            'source': 'TeenBuzz News',
            'category': 'Social Issues',
            'relevance': 'Shows teens how they can use technology to solve real-world problems and make a positive impact.'
        }
    ]
    
    for i, article in enumerate(articles):
        try:
            article['created_at'] = datetime.now().isoformat()
            result = supabase.table('articles').insert(article).execute()
            print(f"✅ Added article {i+1}: {article['headline']}")
            print(f"   Category: {article['category']}")
            print(f"   ID: {result.data[0]['id']}")
            print()
        except Exception as e:
            print(f"❌ Error adding article {i+1}: {str(e)}")
    
    print("🎉 All articles added successfully!")
    print("\nYou can now view them at:")
    print("1. Homepage: http://localhost:8000/")
    print("2. Admin panel: http://localhost:8000/admin")
    print("3. Category pages: http://localhost:8000/category/[category]")

if __name__ == "__main__":
    print("Adding multiple test articles to TeenBuzz database...")
    add_multiple_articles() 