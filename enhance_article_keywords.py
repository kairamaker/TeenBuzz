#!/usr/bin/env python3

from database_manager import get_database

def enhance_article_keywords():
    """Add comprehensive keywords to existing articles for better search"""
    
    db = get_database()
    if not db:
        print("❌ Database not available")
        return
    
    # Enhanced articles with comprehensive keywords
    enhanced_articles = [
        {
            'id': 1,
            'headline': 'New AI Tools Help Students Study Smarter, Not Harder',
            'content': 'Students are discovering how artificial intelligence can revolutionize their study habits. From personalized learning plans to instant homework help, AI is making education more accessible and effective for teens everywhere. These tools are changing how students approach learning, making complex subjects more digestible and study sessions more efficient.',
            'category': 'Technology',
            'source': 'TechCrunch',
            'tags': 'AI,artificial intelligence,education,technology,students,learning,homework,study tools,personalized learning,academic success,teenagers,digital learning,smart studying,educational technology,AI tutoring,learning apps,study habits,academic performance,student life,tech for teens',
            'views': 1250,
            'likes': 89
        },
        {
            'id': 2,
            'headline': 'Climate Change: What Teens Can Do to Make a Real Difference',
            'content': 'Young activists are leading the charge against climate change with innovative solutions and powerful voices. Learn about the practical steps you can take to protect our planet and inspire others to join the movement. From school strikes to social media campaigns, teens are proving that age is just a number when it comes to environmental action.',
            'category': 'Environment',
            'source': 'BBC News',
            'tags': 'climate,environment,activism,sustainability,youth,global warming,green living,eco-friendly,renewable energy,carbon footprint,environmental justice,climate action,teen activists,earth day,conservation,recycling,green technology,environmental education,planet protection,climate solutions',
            'views': 980,
            'likes': 76
        },
        {
            'id': 3,
            'headline': 'Mental Health Apps That Actually Help Teens Cope',
            'content': 'New mental health resources designed specifically for teenagers are making it easier to find support and build resilience. These apps offer everything from meditation guides to crisis support, helping teens navigate the challenges of modern life with better mental health tools and resources.',
            'category': 'Health',
            'source': 'NPR',
            'tags': 'mental health,apps,wellness,teenagers,support,anxiety,depression,stress,meditation,mindfulness,therapy,self-care,emotional health,psychological support,teen mental health,wellness apps,mental wellness,coping strategies,emotional support,mental health awareness',
            'views': 850,
            'likes': 64
        },
        {
            'id': 4,
            'headline': 'The Future of Social Media: What Teens Need to Know',
            'content': 'Social media platforms are evolving rapidly, and teens are at the forefront of these changes. From new privacy features to emerging platforms, understanding these shifts can help you navigate the digital world more safely and effectively.',
            'category': 'Technology',
            'source': 'Wired',
            'tags': 'social media,privacy,technology,digital,platforms,Instagram,TikTok,Facebook,Twitter,digital safety,online privacy,cyberbullying,digital citizenship,internet safety,social networking,online presence,digital footprint,social media trends,teen social media,online security',
            'views': 720,
            'likes': 58
        },
        {
            'id': 5,
            'headline': 'How Gen Z is Redefining Success in the Workplace',
            'content': 'Young people are changing what it means to have a successful career, prioritizing work-life balance, mental health, and meaningful work over traditional corporate ladders. This shift is reshaping entire industries and creating new opportunities.',
            'category': 'Social Issues',
            'source': 'Forbes',
            'tags': 'career,workplace,gen z,success,work-life balance,jobs,employment,career advice,professional development,workplace culture,remote work,entrepreneurship,career goals,job market,workplace trends,career planning,professional growth,workplace diversity,career success,teen careers',
            'views': 680,
            'likes': 52
        },
        {
            'id': 6,
            'headline': 'The Science Behind Why Music Moves Us',
            'content': 'New research reveals how music affects our brains and emotions, especially during teenage years. Understanding these connections can help you use music more effectively for studying, relaxation, and emotional regulation.',
            'category': 'Science',
            'source': 'Scientific American',
            'tags': 'music,science,brain,emotions,research,neuroscience,psychology,music therapy,studying,relaxation,emotional regulation,teen brain,music psychology,neural pathways,music and learning,emotional intelligence,music research,brain development,music benefits,teen psychology',
            'views': 590,
            'likes': 45
        }
    ]
    
    # Add more diverse articles with different topics
    additional_articles = [
        {
            'id': 7,
            'headline': 'Teen Entrepreneurs Building the Next Big Apps',
            'content': 'Meet the young innovators who are creating apps and startups that are changing the world. From social impact to entertainment, these teen entrepreneurs are proving that age is no barrier to innovation and success.',
            'category': 'Technology',
            'source': 'TechCrunch',
            'tags': 'entrepreneurship,startups,apps,innovation,teen entrepreneurs,business,technology,young innovators,app development,startup culture,teen business,innovation,tech startups,young founders,app creation,business ideas,teen success,entrepreneurial spirit,tech innovation,young business leaders',
            'views': 920,
            'likes': 78
        },
        {
            'id': 8,
            'headline': 'The Rise of Teen Activism in Politics',
            'content': 'Young people are becoming increasingly involved in political movements, from voting rights to social justice. Learn how teens are making their voices heard and driving real change in their communities and beyond.',
            'category': 'Social Issues',
            'source': 'CNN',
            'tags': 'politics,activism,teen activists,voting rights,social justice,political engagement,youth vote,civic engagement,political movements,democracy,teen politics,political awareness,social change,community organizing,political participation,teen leaders,political education,civic responsibility,political action,youth empowerment',
            'views': 1100,
            'likes': 95
        },
        {
            'id': 9,
            'headline': 'Space Exploration: What Teens Should Know About Mars Missions',
            'content': 'As space exploration advances, teenagers are the generation that will likely see humans land on Mars. Discover the latest developments in space technology and what this means for the future of humanity.',
            'category': 'Science',
            'source': 'NASA',
            'tags': 'space,exploration,Mars,NASA,astronomy,space technology,space missions,astronauts,space science,space exploration,space travel,planetary science,space research,space innovation,space engineering,space discovery,space future,space education,teen space interest,space careers',
            'views': 750,
            'likes': 62
        },
        {
            'id': 10,
            'headline': 'Digital Art and NFTs: The New Creative Economy for Teens',
            'content': 'Young artists are embracing digital art and NFTs as new ways to monetize their creativity. Learn about the opportunities and challenges in this emerging digital art market.',
            'category': 'Technology',
            'source': 'Art News',
            'tags': 'digital art,NFTs,blockchain,art,creativity,teen artists,digital creativity,art market,cryptocurrency,digital economy,creative economy,art technology,digital artists,art innovation,creative careers,digital media,art entrepreneurship,teen creativity,digital culture,art and technology',
            'views': 680,
            'likes': 48
        }
    ]
    
    try:
        with db:
            print("🔄 Updating existing articles with enhanced keywords...")
            
            # Update existing articles
            for article in enhanced_articles:
                db.update('articles', {
                    'tags': article['tags'],
                    'views': article['views'],
                    'likes': article['likes']
                }, 'id = ?', (article['id'],))
                print(f"✅ Updated article {article['id']}: {article['headline'][:50]}...")
            
            # Add new articles
            print("\n🔄 Adding new diverse articles...")
            for article in additional_articles:
                article_data = {
                    'headline': article['headline'],
                    'content': article['content'],
                    'category': article['category'],
                    'source': article['source'],
                    'tags': article['tags'],
                    'views': article['views'],
                    'likes': article['likes'],
                    'created_at': '2024-01-15T10:00:00'
                }
                db.insert('articles', article_data)
                print(f"✅ Added article: {article['headline'][:50]}...")
            
            print(f"\n🎉 Successfully enhanced {len(enhanced_articles)} existing articles and added {len(additional_articles)} new articles!")
            print("🔍 Search functionality is now much more powerful with comprehensive keywords!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    enhance_article_keywords()
