#!/usr/bin/env python3

# This script will create a clean home route that uses the local database

clean_home_route = '''@app.route('/')
def home():
    """Home page with latest articles"""
    try:
        # Use the configured database (local or cloud)
        if local_db:
            # Use local database
            flash(f'✅ Using local database: {get_database_status()}', 'success')
            articles = get_articles_from_db(limit=10)
            categories = local_db.select('categories')
            
            # Get "For You" articles (top 3 by views)
            for_you_articles = get_articles_from_db(limit=3, order_by='views', desc=True)
            
            # Get "Continue Reading" articles (recently viewed)
            continue_reading_articles = get_articles_from_db(limit=3, order_by='created_at', desc=True)
            
        elif supabase:
            # Use Supabase
            flash('✅ Connected to Supabase database', 'success')
            articles = get_articles_from_db(limit=10)
            categories = supabase.table('categories').select('*').execute().data or []
            
            # Get "For You" articles
            for_you_articles = get_articles_from_db(limit=3, order_by='views', desc=True)
            
            # Get "Continue Reading" articles  
            continue_reading_articles = get_articles_from_db(limit=3, order_by='created_at', desc=True)
            
        else:
            # Fallback to sample data
            flash('Database connection in progress. Showing sample articles while we connect to your database.', 'info')
            articles = get_sample_articles()
            categories = get_sample_categories()
            
            # Sample "For You" and "Continue Reading" articles
            for_you_articles = articles[:3]
            continue_reading_articles = articles[3:6]
        
        # Add reading progress for continue reading articles
        for article in continue_reading_articles:
            if 'read_progress' not in article:
                article['read_progress'] = 65
                article['last_read_time'] = '2 hours ago'
        
        return render_template('index_modern.html',
                             articles=articles,
                             for_you_articles=for_you_articles,
                             continue_reading_articles=continue_reading_articles,
                             categories=NEWS_CATEGORIES,
                             get_category_icon=get_category_icon,
                             format_date=format_date,
                             current_category='All',
                             page_title='Latest News',
                             current_date=datetime.now().strftime('%B %d, %Y'))
    
    except Exception as e:
        print(f"Error in home route: {e}")
        # Fallback to sample data on any error
        flash('Using sample data due to an error.', 'warning')
        articles = get_sample_articles()
        for_you_articles = articles[:3]
        continue_reading_articles = articles[3:6]
        
        return render_template('index_modern.html',
                             articles=articles,
                             for_you_articles=for_you_articles,
                             continue_reading_articles=continue_reading_articles,
                             categories=NEWS_CATEGORIES,
                             get_category_icon=get_category_icon,
                             format_date=format_date,
                             current_category='All',
                             page_title='Latest News',
                             current_date=datetime.now().strftime('%B %d, %Y'))
'''

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Find the start and end of the home route
start_marker = "@app.route('/')"
end_marker = "@app.route('/categories')"

start_pos = content.find(start_marker)
end_pos = content.find(end_marker)

if start_pos != -1 and end_pos != -1:
    # Replace the entire home route
    new_content = content[:start_pos] + clean_home_route + '\n\n' + content[end_pos:]
    
    # Write the updated content
    with open('app.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Fixed home route to use local database properly")
else:
    print("❌ Could not find home route markers")
