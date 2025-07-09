# TeenBuzz New Features

## 🚀 New Features Implemented

### 1. Automatic Daily Article Fetching
- **Script**: `auto_fetch_articles.py`
- **Function**: Automatically fetches 5 trending news articles daily
- **Schedule**: Runs at 9:00 AM daily via cron job
- **Features**:
  - Prevents duplicate articles on the same day
  - Fetches from multiple news sources
  - Rewrites articles in teen-friendly language
  - Stores articles with proper metadata

### 2. Current Date Display
- **Location**: Homepage and category pages
- **Format**: "Month Day, Year" (e.g., "December 15, 2024")
- **Style**: Beautiful gradient banner with calendar icon

### 3. User Preferences Form
- **Route**: `/preferences`
- **Features**:
  - Email collection for user engagement
  - Topic selection (checkboxes for all categories)
  - Saves preferences to database
  - Updates existing preferences if email exists
- **Database**: New `user_preferences` table

### 4. Smart Category Filtering
- **Behavior**: Only shows categories that have articles
- **Dynamic**: Updates based on available content
- **Clean UI**: No empty category buttons

### 5. Enhanced Article Cards
- **Date Badge**: Prominent date display on each article
- **Position**: Top-right corner of article image
- **Style**: Dark overlay with calendar icon

## 📋 Setup Instructions

### 1. Database Setup
Run this SQL in your Supabase dashboard:
```sql
-- Add user preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    topics TEXT[], -- Array of selected topics
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for email lookups
CREATE INDEX IF NOT EXISTS idx_user_preferences_email ON user_preferences(email);

-- Enable RLS
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can insert preferences" ON user_preferences FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can update their own preferences" ON user_preferences FOR UPDATE USING (true);
CREATE POLICY "Users can view their own preferences" ON user_preferences FOR SELECT USING (true);
```

### 2. Automatic Article Fetching Setup
```bash
# Make the setup script executable
chmod +x setup_cron.sh

# Run the setup script
./setup_cron.sh
```

### 3. Test the Features
```bash
# Test automatic article fetching manually
python auto_fetch_articles.py

# Run the Flask app
python app.py
```

## 🎯 Feature Details

### Automatic Article Fetching
- **Sources**: The Guardian, New York Times, BBC News, CNN, Yahoo News, Teen Vogue, BuzzFeed, NPR News
- **Categories**: Technology, Entertainment, Sports, Health, Environment, Education, Social Issues, Science, Gaming, Music
- **Topics**: Trending news, breaking news, top stories, viral news, important news
- **Rate Limiting**: Only fetches if less than 5 articles exist for the current day

### User Preferences
- **Email Validation**: Required field with proper email format
- **Topic Selection**: Multiple selection allowed
- **Persistence**: Saves to database with timestamps
- **Updates**: Can modify existing preferences

### UI Improvements
- **Current Date**: Prominent display on all pages
- **Smart Categories**: Only shows categories with content
- **Date Badges**: Clear article publication dates
- **Responsive Design**: Works on all device sizes

## 🔧 Configuration

### Environment Variables
Make sure your `.env` file has:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
PERPLEXITY_API_KEY=your_perplexity_api_key
```

### Cron Job Management
```bash
# View current cron jobs
crontab -l

# Remove all cron jobs
crontab -r

# Edit cron jobs manually
crontab -e
```

## 📊 Monitoring

### Logs
- **Daily Fetch Log**: `daily_fetch.log`
- **Application Logs**: Check Flask console output
- **Database**: Monitor article count in Supabase

### Success Indicators
- ✅ 5 new articles appear daily
- ✅ Current date displays correctly
- ✅ User preferences save successfully
- ✅ Only populated categories show in filter
- ✅ Article dates display prominently

## 🚨 Troubleshooting

### Common Issues
1. **Articles not fetching**: Check Perplexity API key
2. **Cron job not running**: Verify cron service is active
3. **Database errors**: Check Supabase connection
4. **UI issues**: Clear browser cache

### Debug Commands
```bash
# Test article fetching
python auto_fetch_articles.py

# Check cron job
crontab -l

# View logs
tail -f daily_fetch.log

# Test database connection
python test_db_connection.py
```

## 🎉 Benefits

1. **Automated Content**: Fresh articles daily without manual intervention
2. **User Engagement**: Email collection for future features
3. **Better UX**: Smart filtering and clear date display
4. **Scalable**: Easy to modify categories and sources
5. **Teen-Friendly**: All content rewritten for target audience 