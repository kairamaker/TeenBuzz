#!/usr/bin/env python3
"""
Enhanced Search Keywords Script
Adds comprehensive keywords to articles for better search functionality
"""

import sqlite3
import os

def enhance_article_keywords():
    """Add comprehensive keywords to all articles for better search"""
    
    # Connect to local database
    db_path = 'teenbuzz_local.db'
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enhanced keywords for each article
    enhanced_keywords = {
        1: "AI,artificial intelligence,education,technology,students,learning,homework,study tools,personalized learning,academic success,teenagers,digital learning,smart studying,educational technology,AI tutoring,learning apps,study habits,academic performance,student life,tech for teens,chatgpt,openai,study tips,exam prep,homework help,smart learning,AI education,digital tutoring,learning assistance,study methods,academic tools,educational AI,student success,learning technology,AI study buddy,homework solutions,study strategies,academic support,learning innovation,tech education",
        
        2: "climate,environment,activism,sustainability,youth,global warming,green living,eco-friendly,renewable energy,carbon footprint,environmental justice,climate action,teen activists,earth day,conservation,recycling,green technology,environmental education,planet protection,climate solutions,climate change,environmental protection,green lifestyle,eco activism,climate crisis,environmental awareness,green living tips,sustainable living,climate action,environmental responsibility,green energy,eco-friendly lifestyle,climate solutions,environmental education,planet care,green technology,eco-conscious living,climate awareness,environmental action",
        
        3: "mental health,apps,wellness,teenagers,support,anxiety,depression,stress,meditation,mindfulness,therapy,self-care,emotional health,psychological support,teen mental health,wellness apps,mental wellness,coping strategies,emotional support,mental health awareness,mental health apps,wellness technology,stress relief,anxiety management,depression support,mental wellness,emotional wellbeing,psychological health,teen mental health,wellness tools,mental health resources,emotional support,stress management,anxiety relief,depression help,mental health awareness,wellness apps,emotional wellness,psychological support,mental health tips",
        
        4: "social media,privacy,technology,digital,platforms,Instagram,TikTok,Facebook,Twitter,digital safety,online privacy,cyberbullying,digital citizenship,internet safety,social networking,online presence,digital footprint,social media trends,teen social media,online security,social media safety,digital privacy,online safety,cyber safety,digital wellness,social media tips,online security,digital citizenship,internet privacy,social media awareness,digital safety tips,online protection,cyber security,social media education,digital literacy,online behavior,social media guidelines,digital responsibility,internet safety tips",
        
        5: "career,workplace,gen z,success,work-life balance,jobs,employment,career advice,professional development,workplace culture,remote work,entrepreneurship,career goals,job market,workplace trends,career planning,professional growth,workplace diversity,career success,teen careers,job search,career development,professional skills,workplace success,career guidance,job opportunities,career planning,professional growth,workplace skills,career advice,teen employment,career exploration,professional development,workplace culture,career goals,success strategies,career planning,professional skills,career guidance,teen careers",
        
        6: "music,science,brain,emotions,research,neuroscience,psychology,music therapy,studying,relaxation,emotional regulation,teen brain,music psychology,neural pathways,music and learning,emotional intelligence,music research,brain development,music benefits,teen psychology,music science,neuroscience,music therapy,emotional regulation,music psychology,brain research,music and emotions,neural pathways,music benefits,psychological effects,music research,emotional intelligence,music therapy,neuroscience research,music psychology,emotional regulation,music benefits,psychological effects,music research,emotional intelligence",
        
        7: "entrepreneurship,startups,apps,innovation,teen entrepreneurs,business,technology,young innovators,app development,startup culture,teen business,innovation,tech startups,young founders,app creation,business ideas,teen success,entrepreneurial spirit,tech innovation,young business leaders,teen entrepreneurship,startup success,business innovation,tech entrepreneurship,young entrepreneurs,startup culture,app development,business ideas,entrepreneurial success,tech startups,young business leaders,startup innovation,business development,entrepreneurial spirit,tech innovation,startup success,business ideas,entrepreneurial journey,tech entrepreneurship",
        
        8: "politics,activism,teen activists,voting rights,social justice,political engagement,youth vote,civic engagement,political movements,democracy,teen politics,political awareness,social change,community organizing,political participation,teen leaders,political education,civic responsibility,political action,youth empowerment,political activism,teen politics,civic engagement,political participation,social justice,political awareness,democratic participation,political education,civic responsibility,political action,youth empowerment,political engagement,teen activism,political participation,social change,political awareness,civic engagement,political education,political action,youth empowerment",
        
        9: "space,exploration,Mars,NASA,astronomy,space technology,space missions,astronauts,space science,space exploration,space travel,planetary science,space research,space innovation,space engineering,space discovery,space future,space education,teen space interest,space careers,space exploration,astronomy,space technology,space missions,astronauts,space science,space travel,planetary science,space research,space innovation,space engineering,space discovery,space future,space education,teen space interest,space careers,space exploration,astronomy,space technology",
        
        10: "digital art,NFTs,blockchain,art,creativity,teen artists,digital creativity,art market,cryptocurrency,digital economy,creative economy,art technology,digital artists,art innovation,creative careers,digital media,art entrepreneurship,teen creativity,digital culture,art and technology,digital art,blockchain art,art technology,digital creativity,art innovation,creative careers,digital media,art entrepreneurship,teen creativity,digital culture,art and technology,digital art market,blockchain technology,art innovation,creative economy,digital artists,art technology,creative careers,digital media"
    }
    
    print("🔍 Enhancing search keywords for all articles...")
    
    for article_id, keywords in enhanced_keywords.items():
        try:
            cursor.execute("""
                UPDATE articles 
                SET tags = ? 
                WHERE id = ?
            """, (keywords, article_id))
            
            # Get article title for confirmation
            cursor.execute("SELECT headline FROM articles WHERE id = ?", (article_id,))
            title = cursor.fetchone()[0]
            
            print(f"✅ Enhanced keywords for: {title[:50]}...")
            
        except Exception as e:
            print(f"❌ Error updating article {article_id}: {e}")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("\n🎉 Search keywords enhanced successfully!")
    print("📊 Users can now search for articles using:")
    print("   • Technology terms: AI, apps, social media, digital art, entrepreneurship")
    print("   • Health terms: mental health, wellness, stress, anxiety, therapy")
    print("   • Environment terms: climate, sustainability, green living, activism")
    print("   • Science terms: space, Mars, music, neuroscience, research")
    print("   • Social terms: politics, activism, career, workplace, success")
    print("   • And many more specific keywords!")

if __name__ == "__main__":
    enhance_article_keywords()
