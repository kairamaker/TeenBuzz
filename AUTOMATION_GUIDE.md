# TeenBuzz Daily Automation System

## 🎯 Overview

The TeenBuzz Daily Automation System automatically fetches fresh articles from major news sources every day, keeping your app's content current and engaging for teen users.

## 📁 System Components

### Core Files
- `daily_article_automation.py` - Main automation script
- `run_daily_fetch.sh` - Shell script wrapper
- `setup_cron_job.sh` - Cron job installation script
- `manage_automation.py` - Management and monitoring tool

### Supporting Files
- `advanced_article_fetcher.py` - RSS feed fetching logic
- `fetch_real_articles.py` - Article processing and enhancement
- `logs/` - Directory containing all automation logs

## 🚀 Quick Start

### 1. Install the Automation System
```bash
# Make scripts executable
chmod +x run_daily_fetch.sh setup_cron_job.sh manage_automation.py

# Install cron job (runs daily at 6:00 AM)
./setup_cron_job.sh
```

### 2. Test the System
```bash
# Test the automation manually
python manage_automation.py test

# Check system status
python manage_automation.py status
```

### 3. Monitor the System
```bash
# View recent logs
python manage_automation.py logs

# Check cron job status
python manage_automation.py check
```

## 📅 Automation Schedule

- **Daily Article Fetch**: 6:00 AM every day
- **Weekly Cleanup**: Sundays (removes articles older than 30 days)
- **Log Rotation**: Daily log files with date stamps

## 📊 What the System Does

### Daily Operations
1. **Fetches Articles**: Pulls from 6 major RSS feeds:
   - BBC Technology News
   - BBC Science & Environment
   - BBC Health
   - CNN World News
   - Reuters Technology
   - Reuters Science

2. **Enhances Content**: Automatically adds teen-focused context and explanations

3. **Categorizes Articles**: Assigns appropriate categories (Technology, Health, Science, etc.)

4. **Updates Database**: Adds new articles to the local SQLite database

5. **Logs Activity**: Records all operations with timestamps

### Weekly Operations
- **Cleanup**: Removes articles older than 30 days to keep database fresh
- **Statistics**: Generates category breakdown and article counts

## 🔧 Management Commands

### Status Check
```bash
python manage_automation.py status
```
Shows:
- Cron job status
- Database article count
- Log file information
- System health

### Manual Testing
```bash
python manage_automation.py test
```
Runs the automation system immediately for testing

### Log Viewing
```bash
python manage_automation.py logs
```
Displays recent automation logs and cron output

### Cron Job Management
```bash
# Install cron job
python manage_automation.py install

# Remove cron job
python manage_automation.py remove

# Check cron job status
python manage_automation.py check
```

## 📝 Log Files

### Daily Logs
- Location: `logs/daily_fetch_YYYYMMDD.log`
- Contains: Detailed automation process logs
- Format: Timestamp, level, message

### Cron Logs
- Location: `logs/cron.log`
- Contains: Cron job execution output
- Includes: Success/failure status and error messages

## 🛠️ Troubleshooting

### Common Issues

#### 1. Cron Job Not Running
```bash
# Check if cron job exists
crontab -l

# Reinstall cron job
./setup_cron_job.sh
```

#### 2. Database Connection Issues
```bash
# Check database status
python -c "from database_manager import get_database; print('DB OK' if get_database() else 'DB Error')"
```

#### 3. RSS Feed Issues
```bash
# Test RSS fetching manually
python -c "from advanced_article_fetcher import fetch_real_articles; print(len(fetch_real_articles()))"
```

#### 4. Permission Issues
```bash
# Fix script permissions
chmod +x run_daily_fetch.sh setup_cron_job.sh manage_automation.py
```

### Log Analysis

#### Check Recent Activity
```bash
# View today's automation log
tail -f logs/daily_fetch_$(date +%Y%m%d).log

# View cron output
tail -f logs/cron.log
```

#### Monitor System Health
```bash
# Check system status
python manage_automation.py status

# View all recent logs
python manage_automation.py logs
```

## 📈 Performance Metrics

### Expected Results
- **Articles Fetched**: 10-20 articles per day
- **Processing Time**: 30-60 seconds
- **Database Growth**: ~300-600 articles per month
- **Storage**: ~1-2 MB per month (articles + logs)

### Monitoring
- Check `logs/daily_fetch_*.log` for daily statistics
- Monitor database size with `python manage_automation.py status`
- Review cron logs for execution status

## 🔄 Maintenance

### Regular Tasks
1. **Weekly**: Check logs for errors
2. **Monthly**: Review database size and cleanup effectiveness
3. **Quarterly**: Update RSS feed sources if needed

### Backup Recommendations
- Backup the `logs/` directory
- Export database periodically
- Keep automation scripts in version control

## 🚨 Alerts and Notifications

### Success Indicators
- ✅ "Daily article automation completed successfully!"
- ✅ Articles added to database
- ✅ Log files created with timestamps

### Failure Indicators
- ❌ "Daily article automation failed!"
- ❌ No new articles in database
- ❌ Missing or empty log files

## 📞 Support

### Manual Override
If automation fails, you can manually fetch articles:
```bash
# Run automation manually
./run_daily_fetch.sh

# Or use the API endpoint
curl -X POST "http://localhost:5003/api/articles/fetch"
```

### System Recovery
```bash
# Reinstall automation system
./setup_cron_job.sh

# Test system
python manage_automation.py test

# Check status
python manage_automation.py status
```

---

## 🎉 Success!

Your TeenBuzz app now has a fully automated article system that:
- ✅ Fetches fresh content daily
- ✅ Enhances articles for teen audiences
- ✅ Maintains database health
- ✅ Provides comprehensive logging
- ✅ Includes monitoring tools

The system will run automatically every day at 6:00 AM, keeping your app's content fresh and engaging for your teen users!

