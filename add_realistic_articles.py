#!/usr/bin/env python3
"""
Add realistic, longer articles to the database
"""

from database_manager import get_database
from datetime import datetime
import random

def add_realistic_articles():
    """Add realistic articles with longer content"""
    db = get_database()
    if not db:
        print("❌ Database connection failed")
        return False
    
    realistic_articles = [
        {
            'headline': 'How AI is Revolutionizing Education for Teenagers',
            'content': '''Artificial Intelligence is transforming the way teenagers learn and interact with educational content. From personalized learning platforms to AI-powered tutoring systems, technology is making education more accessible and engaging than ever before.

One of the most significant developments is the rise of AI tutoring systems that can adapt to individual learning styles. These systems analyze how students learn best and adjust their teaching methods accordingly. For example, if a student learns better through visual content, the AI will prioritize diagrams, charts, and videos in their lessons.

Another exciting development is the use of AI in language learning. Apps like Duolingo and Babbel use machine learning algorithms to create personalized lesson plans that focus on areas where students need the most improvement. This targeted approach helps students learn languages more efficiently.

AI is also being used to detect learning disabilities early. By analyzing patterns in how students interact with educational content, AI systems can identify potential issues like dyslexia or ADHD and recommend appropriate interventions.

However, there are also concerns about AI in education. Some worry that over-reliance on AI might reduce critical thinking skills or create a digital divide between students who have access to these technologies and those who don't.

Despite these concerns, the potential benefits of AI in education are enormous. As these technologies continue to develop, we can expect to see even more innovative ways to help teenagers learn and grow.''',
            'category': 'Technology',
            'tags': 'AI, education, learning, technology, teenagers, tutoring, personalized learning',
            'source': 'TechEd Today',
            'url': 'https://techedtoday.com/ai-education-teenagers',
            'views': random.randint(50, 500),
            'likes': random.randint(10, 100)
        },
        {
            'headline': 'The Mental Health Crisis Among Teenagers: What Parents Need to Know',
            'content': '''The mental health crisis among teenagers has reached alarming proportions, with rates of anxiety, depression, and suicide attempts increasing dramatically over the past decade. Understanding the causes and knowing how to help is crucial for parents, educators, and healthcare providers.

Social media plays a significant role in this crisis. Studies show that teenagers who spend more than three hours a day on social media are twice as likely to experience symptoms of anxiety and depression. The constant comparison to others' curated lives, cyberbullying, and the pressure to maintain a perfect online presence all contribute to mental health issues.

Academic pressure is another major factor. The competitive nature of modern education, combined with the pressure to excel in multiple areas, creates an environment of chronic stress. Many teenagers report feeling overwhelmed by the expectations placed on them by parents, teachers, and society.

The COVID-19 pandemic has exacerbated these issues. Isolation, disrupted routines, and uncertainty about the future have taken a toll on teenagers' mental health. Many have struggled with the transition to online learning and the loss of social connections.

Warning signs that parents should watch for include changes in sleep patterns, appetite, or mood; withdrawal from friends and activities; declining academic performance; and expressions of hopelessness or worthlessness.

Early intervention is crucial. Parents should create an open, non-judgmental environment where teenagers feel comfortable discussing their feelings. Professional help from therapists or counselors can be invaluable, and there are many resources available for families dealing with mental health issues.

Schools also have a role to play in supporting student mental health. Many are implementing programs to teach coping skills, reduce stigma, and provide access to mental health resources.

The good news is that mental health issues are treatable, and with the right support, teenagers can learn to manage their symptoms and thrive. The key is recognizing the problem early and seeking appropriate help.''',
            'category': 'Health',
            'tags': 'mental health, teenagers, anxiety, depression, social media, parents, education',
            'source': 'Teen Health Weekly',
            'url': 'https://teenhealthweekly.com/mental-health-crisis',
            'views': random.randint(100, 800),
            'likes': random.randint(20, 150)
        },
        {
            'headline': 'Climate Change: How Teen Activists Are Leading the Fight for Our Planet',
            'content': '''Teenage climate activists around the world are proving that age is just a number when it comes to fighting for environmental justice. From Greta Thunberg's school strikes to local community initiatives, young people are driving meaningful change in the fight against climate change.

The youth climate movement has gained unprecedented momentum in recent years. Millions of teenagers have participated in climate strikes, demanding action from world leaders and corporations. These young activists understand that they will bear the brunt of climate change's effects, and they're not waiting for adults to solve the problem.

One of the most powerful aspects of the teen climate movement is its global reach. Through social media and digital platforms, young activists can connect, share ideas, and coordinate actions across continents. This has created a truly international movement that transcends borders and cultures.

Teen activists are also using innovative approaches to raise awareness. Some have created viral social media campaigns, while others have organized community clean-up events or started environmental clubs at their schools. Many are using their creativity to make climate science more accessible and engaging for their peers.

The movement has also highlighted the intersectionality of climate change. Teen activists recognize that environmental issues are connected to social justice, economic inequality, and human rights. They're advocating for solutions that address these interconnected problems.

However, teen climate activists also face significant challenges. They often encounter skepticism from adults who dismiss their concerns or question their knowledge. Some face harassment or even threats for their activism. Despite these obstacles, they continue to push forward with determination and hope.

The impact of teen climate activism is already visible. Many schools and universities have committed to divesting from fossil fuels, and some governments have implemented more ambitious climate policies in response to youth pressure.

Looking ahead, teen climate activists are focusing on building long-term solutions. They're not just protesting; they're also working on practical projects like community gardens, renewable energy initiatives, and environmental education programs.

The message from teen climate activists is clear: the time for action is now, and everyone has a role to play in protecting our planet for future generations.''',
            'category': 'Environment',
            'tags': 'climate change, activism, teenagers, environment, Greta Thunberg, social justice, sustainability',
            'source': 'EcoTeen News',
            'url': 'https://ecoteennews.com/teen-climate-activists',
            'views': random.randint(200, 1000),
            'likes': random.randint(50, 200)
        },
        {
            'headline': 'The Future of Work: How Teenagers Can Prepare for Jobs That Don\'t Exist Yet',
            'content': '''The job market is evolving at an unprecedented pace, with new careers emerging while traditional ones disappear. For teenagers preparing to enter the workforce, this presents both challenges and opportunities. Understanding how to adapt and prepare for an uncertain future is crucial for success.

One of the most significant trends is the rise of remote work. The COVID-19 pandemic accelerated this shift, and many companies are now offering permanent remote positions. This means teenagers need to develop digital communication skills, self-discipline, and the ability to work independently.

Artificial intelligence and automation are also reshaping the job market. While some jobs may be replaced by machines, new opportunities are emerging in AI development, data analysis, and human-AI collaboration. Teenagers should focus on developing skills that complement rather than compete with AI.

The gig economy is another important trend. More people are working as freelancers, consultants, or independent contractors. This requires entrepreneurial skills, self-marketing abilities, and financial management knowledge.

Soft skills are becoming increasingly important. As automation handles more routine tasks, human skills like creativity, emotional intelligence, and critical thinking are in high demand. Teenagers should focus on developing these abilities through activities like debate, art, volunteer work, and leadership roles.

Digital literacy is essential for almost any career. This goes beyond basic computer skills to include understanding of digital tools, online security, and the ability to learn new technologies quickly.

Financial literacy is another crucial skill. With the rise of cryptocurrency, digital banking, and new investment options, teenagers need to understand how to manage money in a digital world.

Networking and relationship-building skills are more important than ever. In a global, digital economy, the ability to connect with people from different cultures and backgrounds is invaluable.

Education is also evolving. Traditional degrees are still valuable, but alternative credentials like certifications, bootcamps, and online courses are becoming more accepted. Teenagers should consider a mix of formal education and practical experience.

The key is to stay adaptable and curious. The jobs of the future will require people who can learn quickly, think creatively, and adapt to change. By developing these skills now, teenagers can position themselves for success in whatever the future holds.''',
            'category': 'Education',
            'tags': 'future of work, careers, teenagers, remote work, AI, gig economy, skills, education',
            'source': 'Future Careers Today',
            'url': 'https://futurecareerstoday.com/teen-job-preparation',
            'views': random.randint(80, 600),
            'likes': random.randint(15, 120)
        },
        {
            'headline': 'Social Media and Teen Identity: Navigating the Digital World',
            'content': '''Social media has become an integral part of teenage life, shaping how young people form their identities, build relationships, and understand the world around them. While these platforms offer opportunities for connection and self-expression, they also present unique challenges for developing minds.

Identity formation is one of the most complex aspects of teenage development, and social media adds new layers to this process. Teenagers often use these platforms to experiment with different aspects of their personality, trying on different identities and seeing how they're received by their peers.

The pressure to present a perfect image online can be overwhelming. Many teenagers feel compelled to curate their social media presence to show only their best moments, leading to a disconnect between their online persona and their real-life experiences. This can contribute to feelings of inadequacy and anxiety.

Social comparison is another significant issue. When teenagers constantly see their peers' highlight reels, they may feel that their own lives don't measure up. This can lead to decreased self-esteem and increased feelings of loneliness and depression.

However, social media also provides opportunities for positive identity development. Many teenagers use these platforms to explore their interests, connect with like-minded peers, and find communities where they feel accepted and understood.

The key is finding a healthy balance. Parents and educators can help teenagers develop critical thinking skills about social media content, encouraging them to question what they see and remember that online representations are often curated and edited.

Digital citizenship is an important concept for teenagers to understand. This includes knowing how to protect their privacy, recognizing and avoiding cyberbullying, and understanding the long-term consequences of their online actions.

Mental health awareness is crucial when it comes to social media use. Teenagers should be encouraged to take breaks from social media when they feel overwhelmed, and to seek help if they're struggling with their mental health.

The future of social media and teen identity is still evolving. As new platforms emerge and existing ones change, teenagers will need to continue adapting and developing new skills to navigate the digital world safely and effectively.

Ultimately, the goal is to help teenagers use social media as a tool for positive self-expression and connection, while maintaining their mental health and well-being in the process.''',
            'category': 'Social Issues',
            'tags': 'social media, identity, teenagers, mental health, digital citizenship, self-esteem, online safety',
            'source': 'Digital Youth Today',
            'url': 'https://digitalyouthtoday.com/social-media-identity',
            'views': random.randint(150, 700),
            'likes': random.randint(25, 130)
        }
    ]
    
    print("🔄 Adding realistic articles to database...")
    
    for article in realistic_articles:
        try:
            # Check if article already exists
            existing = db.select('articles', where='headline = ?', params=(article['headline'],), limit=1)
            if existing:
                print(f"⏭️  Skipping existing article: {article['headline'][:50]}...")
                continue
            
            # Add created_at timestamp
            article['created_at'] = datetime.now().isoformat()
            article['updated_at'] = datetime.now().isoformat()
            
            # Insert article
            article_id = db.insert('articles', article)
            print(f"✅ Added article: {article['headline'][:50]}...")
            
        except Exception as e:
            print(f"❌ Error adding article: {e}")
    
    print("🎉 Realistic articles added successfully!")
    return True

if __name__ == "__main__":
    add_realistic_articles()

