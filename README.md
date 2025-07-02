# TeenBuzz - News for Teens

A pure Python Flask application that fetches and rewrites news articles specifically for teenagers using Perplexity AI.

## 🏗️ Architecture
- **Backend**: Python Flask (server-side rendering)
- **Frontend**: HTML/CSS (no JavaScript)
- **Database**: Supabase (PostgreSQL)
- **AI**: Perplexity API for teen-friendly news rewriting

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment Variables
Create a `.env` file in the project root:
```bash
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_anon_key_here
PERPLEXITY_API_KEY=your_perplexity_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

### 3. Setup Supabase Database
1. Create a new project at [supabase.com](https://supabase.com)
2. Go to SQL Editor and run the contents of `database_schema.sql`
3. Get your project URL and anon key from Settings > API

### 4. Get Perplexity API Key
1. Visit [perplexity.ai](https://perplexity.ai)
2. Sign up and get your API key
3. Add it to your `.env` file

### 5. Run the Application
```bash
python app.py
```

Visit `http://localhost:8000` to see your app!

## 📱 Features

### MVP Features (Current)
- ✅ Browse news by categories
- ✅ View individual articles
- ✅ Teen-friendly article rewriting
- ✅ Admin panel for fetching news
- ✅ Pure Python backend (no JavaScript)

### Future Features
- User registration and login
- Personalized news feeds
- Save/bookmark articles
- Comments and interactions
- Push notifications

## 🎯 Usage

### For Users
1. Visit the homepage
2. Browse categories or latest articles
3. Click on any article to read the full story
4. Articles are rewritten to be engaging for teens

### For Admins
1. Go to `/admin`
2. Enter a news topic (e.g., "climate change", "AI technology")
3. Select appropriate category
4. Click "Fetch Article" to get AI-rewritten news
5. Test database connection if needed

## 🛠️ Development

### Project Structure
```
TeenBuzz/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── database_schema.sql    # Database setup
├── templates/            # HTML templates
│   ├── index.html        # Home page
│   ├── article.html      # Article view
│   └── admin.html        # Admin panel
└── static/
    └── css/
        └── style.css     # Styles
```

### Key Routes
- `/` - Homepage with latest articles
- `/category/<category>` - Articles by category
- `/article/<id>` - Individual article view
- `/admin` - Admin panel
- `/admin/fetch-news` - Fetch new articles

## 🔧 Troubleshooting

### Common Issues
1. **Import errors**: Make sure you've installed all dependencies with `pip install -r requirements.txt`
2. **Database connection failed**: Check your Supabase URL and key in `.env`
3. **No articles showing**: Use the admin panel to fetch some articles first
4. **Perplexity API errors**: Verify your API key is correct

### Testing Database
Visit `/test-supabase` to check if your database connection is working.

## 🎨 Customization

### Adding New Categories
Edit the `NEWS_CATEGORIES` list in `app.py`:
```python
NEWS_CATEGORIES = [
    'Technology',
    'Entertainment',
    # Add your categories here
]
```

### Modifying AI Prompt
Edit the `fetch_news_from_perplexity()` function in `app.py` to customize how articles are rewritten.

## 📊 Success Metrics

### MVP Goals
- [ ] Successfully fetch and display articles
- [ ] Positive user feedback on article quality
- [ ] Low operational costs

### Future Goals
- Weekly active users
- Articles read per user
- User registration rate

## 🔑 Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Your Supabase project URL | Yes |
| `SUPABASE_KEY` | Your Supabase anon key | Yes |
| `PERPLEXITY_API_KEY` | Your Perplexity API key | Yes |
| `FLASK_ENV` | Flask environment (development/production) | No |
| `FLASK_DEBUG` | Enable debug mode | No |

## 📝 License

Built during summer internship 2025 by Kaira Khanna at British International School Abu Dhabi.

---

**Need help?** Check the admin panel for setup instructions and troubleshooting tips! 