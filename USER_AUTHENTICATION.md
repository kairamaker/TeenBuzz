# TeenBuzz User Authentication & Article Drawing

## 🎉 New Features Added!

TeenBuzz now has user authentication and the ability for users to "draw" (generate) their own articles from Perplexity AI!

## 🔐 User Authentication

### Features:
- **User Registration**: Teens can create accounts with username and password
- **User Login**: Secure login system with session management
- **User Profiles**: Personal dashboard showing drawn articles and statistics
- **Admin Access**: Special admin user with additional privileges

### Default Admin Account:
- **Username**: `admin`
- **Password**: `admin123`

## 🎲 Article Drawing System

### How It Works:
1. **User Registration**: Teens create an account at `/register`
2. **Login**: Users sign in at `/login`
3. **Draw Articles**: From their profile page, users can click "Draw a New Article"
4. **AI Generation**: The system fetches a random news topic from Perplexity AI
5. **Teen-Friendly Rewrite**: Articles are rewritten using your detailed guidelines
6. **Personal Collection**: Each user's drawn articles are tracked and displayed

### Rate Limiting:
- Users can only draw 1 article every 5 minutes
- This prevents abuse and ensures fair usage

### User Tracking:
- **Articles Table**: Now includes `drawn_by_user_id` field
- **User Draws Table**: Tracks every article draw with timestamp
- **Profile Stats**: Shows total articles drawn and draw history

## 🚀 Getting Started

### 1. Database Setup
First, you need to set up the new database tables. Run the updated SQL schema:

```sql
-- Copy and paste the contents of database_schema.sql into your Supabase SQL editor
```

### 2. Install Dependencies
```bash
pip install flask-login werkzeug
```

### 3. Run the App
```bash
python app.py
```

### 4. Access the Features
- **Home Page**: `http://localhost:8000`
- **Register**: `http://localhost:8000/register`
- **Login**: `http://localhost:8000/login`
- **Profile**: `http://localhost:8000/profile` (requires login)
- **Admin Panel**: `http://localhost:8000/admin`

## 📱 User Experience

### For New Users:
1. Visit TeenBuzz homepage
2. Click "Join to Draw Articles" button
3. Create an account with username and password
4. Get redirected to profile page
5. Click "Draw a New Article" to generate content

### For Returning Users:
1. Login with username and password
2. Access profile page to see drawn articles
3. Draw new articles or read existing ones
4. View draw history and statistics

## 🔧 Technical Details

### Database Schema Changes:
- **users**: Stores user accounts and authentication
- **articles**: Added `drawn_by_user_id` for tracking
- **user_draws**: Tracks article drawing activity

### Security Features:
- Password hashing with Werkzeug
- Session management with Flask-Login
- Row Level Security (RLS) policies
- Rate limiting for article drawing

### API Endpoints:
- `POST /draw-article`: Generate new article for logged-in user
- `GET /profile`: User's personal dashboard
- `POST /login`: User authentication
- `POST /register`: User registration

## 🎯 Benefits

### For Teens:
- **Personalized Experience**: Each user has their own article collection
- **Engagement**: Interactive "drawing" feature makes news fun
- **Ownership**: Users can see articles they've generated
- **Learning**: Track reading habits and interests

### For the Platform:
- **User Retention**: Login system encourages return visits
- **Content Generation**: Users help create more teen-friendly content
- **Analytics**: Track which topics and categories are popular
- **Community**: Build a user base of engaged teen readers

## 🔮 Future Enhancements

Potential features to add:
- **User Preferences**: Let users choose favorite categories
- **Social Features**: Share articles with friends
- **Achievements**: Badges for reading milestones
- **Reading Lists**: Save favorite articles
- **Comments**: Discuss articles with other teens

## 🛠️ Troubleshooting

### Common Issues:
1. **"Users table doesn't exist"**: Run the database schema first
2. **"Login not working"**: Check if admin user was created properly
3. **"Can't draw articles"**: Ensure Perplexity API key is configured
4. **"Rate limit error"**: Wait 5 minutes between draws

### Database Setup:
If you encounter database issues, manually run these SQL commands in Supabase:

```sql
-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Add user tracking to articles
ALTER TABLE articles ADD COLUMN IF NOT EXISTS drawn_by_user_id BIGINT REFERENCES users(id);

-- Create user draws tracking
CREATE TABLE IF NOT EXISTS user_draws (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) NOT NULL,
    article_id BIGINT REFERENCES articles(id) NOT NULL,
    drawn_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

**🎉 Enjoy your new TeenBuzz user authentication system!** 