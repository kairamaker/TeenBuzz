#!/usr/bin/env python3

# This script will update app.py to support database toggling

import re

def update_app_for_database_toggle():
    """Update app.py to support local/cloud database toggling"""
    
    # Read the current app.py
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Add database manager import at the top
    if 'from database_manager import' not in content:
        # Find the import section and add our import
        import_section = content.find('from dotenv import load_dotenv')
        if import_section != -1:
            # Add after the dotenv import
            insert_point = content.find('\n', import_section) + 1
            content = content[:insert_point] + 'from database_manager import get_database, get_database_status\n' + content[insert_point:]
    
    # Add database toggle routes
    toggle_routes = '''
@app.route('/admin/database-toggle')
def database_toggle():
    """Database toggle admin page"""
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('home'))
    
    current_db = get_database_status()
    return render_template('database_toggle.html', current_database=current_db)

@app.route('/admin/switch-to-local')
def switch_to_local():
    """Switch to local database"""
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('home'))
    
    from database_manager import switch_to_local
    switch_to_local()
    flash('Switched to local database', 'success')
    return redirect(url_for('database_toggle'))

@app.route('/admin/switch-to-cloud')
def switch_to_cloud():
    """Switch to cloud database"""
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('home'))
    
    from database_manager import switch_to_cloud
    switch_to_cloud()
    flash('Switched to cloud database', 'success')
    return redirect(url_for('database_toggle'))

'''
    
    # Add the toggle routes before the main block
    main_block = content.find("if __name__ == '__main__':")
    if main_block != -1:
        content = content[:main_block] + toggle_routes + '\n' + content[main_block:]
    
    # Update the database connection logic
    # Find the supabase initialization section
    supabase_init = content.find('supabase = None')
    if supabase_init != -1:
        # Replace the supabase initialization with our toggle logic
        old_init = '''supabase = None
try:
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    if SUPABASE_URL and SUPABASE_KEY and not SUPABASE_URL.startswith('your_') and not SUPABASE_KEY.startswith('your_'):
        print(f"Initializing Supabase client with URL: {SUPABASE_URL}")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Test the connection
        test_result = supabase.table('articles').select('*').limit(1).execute()
        print("Supabase connection test successful")
    else:
        print("Supabase credentials not configured or are placeholders")
except Exception as e:
    print(f"Warning: Could not initialize Supabase client: {e}")
    supabase = None'''
        
        new_init = '''# Initialize database (local or cloud)
supabase = None
local_db = None

try:
    from database_manager import get_database, get_database_status
    db_instance = get_database()
    
    if db_instance is None:
        # Use Supabase (cloud)
        SUPABASE_URL = os.getenv('SUPABASE_URL')
        SUPABASE_KEY = os.getenv('SUPABASE_KEY')
        
        if SUPABASE_URL and SUPABASE_KEY and not SUPABASE_URL.startswith('your_') and not SUPABASE_KEY.startswith('your_'):
            print(f"Initializing Supabase client with URL: {SUPABASE_URL}")
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            # Test the connection
            test_result = supabase.table('articles').select('*').limit(1).execute()
            print("Supabase connection test successful")
        else:
            print("Supabase credentials not configured or are placeholders")
    else:
        # Use local database
        local_db = db_instance
        print(f"Using local database: {get_database_status()}")
        
except Exception as e:
    print(f"Warning: Could not initialize database: {e}")
    supabase = None
    local_db = None'''
    
    content = content.replace(old_init, new_init)
    
    # Add helper function for database operations
    helper_function = '''
def get_articles_from_db(limit=None, category=None, order_by='created_at', desc=True):
    """Get articles from either local or cloud database"""
    if local_db:
        # Use local database
        with local_db:
            query = "SELECT * FROM articles"
            params = []
            
            if category:
                query += " WHERE category = ?"
                params.append(category)
            
            if order_by:
                order_direction = "DESC" if desc else "ASC"
                query += f" ORDER BY {order_by} {order_direction}"
            
            if limit:
                query += f" LIMIT {limit}"
            
            return local_db.execute_query(query, tuple(params))
    else:
        # Use Supabase
        if not supabase:
            return []
        
        query = supabase.table('articles').select('*')
        
        if category:
            query = query.eq('category', category)
        
        if order_by:
            query = query.order(order_by, desc=desc)
        
        if limit:
            query = query.limit(limit)
        
        result = query.execute()
        return result.data or []

def insert_article_to_db(article_data):
    """Insert article into either local or cloud database"""
    if local_db:
        # Use local database
        with local_db:
            return local_db.insert('articles', article_data)
    else:
        # Use Supabase
        if not supabase:
            return None
        
        result = supabase.table('articles').insert(article_data).execute()
        return result.data[0] if result.data else None

'''
    
    # Add the helper function before the routes
    routes_start = content.find('@app.route')
    if routes_start != -1:
        content = content[:routes_start] + helper_function + '\n' + content[routes_start:]
    
    # Write the updated content
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("✅ Updated app.py to support database toggling")
    print("✅ Added local/cloud database switch functionality")
    print("✅ Added admin routes for database management")

if __name__ == "__main__":
    update_app_for_database_toggle()
