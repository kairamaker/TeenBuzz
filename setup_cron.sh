#!/bin/bash

# TeenBuzz Daily Article Fetch Setup Script
# This script sets up a cron job to automatically fetch articles daily

echo "🚀 Setting up TeenBuzz daily article fetch..."

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/auto_fetch_articles.py"

# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Error: auto_fetch_articles.py not found in $SCRIPT_DIR"
    exit 1
fi

# Make the Python script executable
chmod +x "$PYTHON_SCRIPT"

# Create a wrapper script that activates the virtual environment
WRAPPER_SCRIPT="$SCRIPT_DIR/run_daily_fetch.sh"
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
cd "$SCRIPT_DIR"
source teenbuzz_env/bin/activate
python auto_fetch_articles.py >> daily_fetch.log 2>&1
EOF

chmod +x "$WRAPPER_SCRIPT"

# Check if cron job already exists
EXISTING_CRON=$(crontab -l 2>/dev/null | grep "run_daily_fetch.sh" || true)

if [ -n "$EXISTING_CRON" ]; then
    echo "⚠️  Cron job already exists. Removing old one..."
    crontab -l 2>/dev/null | grep -v "run_daily_fetch.sh" | crontab -
fi

# Add new cron job to run daily at 9 AM
echo "0 9 * * * $WRAPPER_SCRIPT" | crontab -

echo "✅ Cron job set up successfully!"
echo "📅 Daily article fetch will run at 9:00 AM every day"
echo "📝 Logs will be saved to daily_fetch.log"
echo ""
echo "To view the cron job:"
echo "  crontab -l"
echo ""
echo "To remove the cron job:"
echo "  crontab -r"
echo ""
echo "To test the script manually:"
echo "  python auto_fetch_articles.py" 