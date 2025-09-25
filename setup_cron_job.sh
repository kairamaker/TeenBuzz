#!/bin/bash

# Setup Cron Job for TeenBuzz Daily Article Fetch
# This script sets up automatic daily article fetching

PROJECT_DIR="/Users/kairaschool/Downloads/TeenBuzz"
SCRIPT_PATH="$PROJECT_DIR/run_daily_fetch.sh"

echo "🔧 Setting up cron job for TeenBuzz daily article fetch..."

# Check if the script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Error: Script not found at $SCRIPT_PATH"
    exit 1
fi

# Make sure the script is executable
chmod +x "$SCRIPT_PATH"

# Create a temporary cron file
TEMP_CRON="/tmp/teenbuzz_cron"

# Get current crontab
crontab -l > "$TEMP_CRON" 2>/dev/null || touch "$TEMP_CRON"

# Check if the job already exists
if grep -q "run_daily_fetch.sh" "$TEMP_CRON"; then
    echo "⚠️ Cron job already exists. Updating..."
    # Remove existing job
    grep -v "run_daily_fetch.sh" "$TEMP_CRON" > "${TEMP_CRON}.new"
    mv "${TEMP_CRON}.new" "$TEMP_CRON"
fi

# Add the new cron job (runs daily at 6:00 AM)
echo "# TeenBuzz Daily Article Fetch - runs daily at 6:00 AM" >> "$TEMP_CRON"
echo "0 6 * * * $SCRIPT_PATH >> $PROJECT_DIR/logs/cron.log 2>&1" >> "$TEMP_CRON"

# Install the new crontab
crontab "$TEMP_CRON"

# Clean up
rm "$TEMP_CRON"

echo "✅ Cron job installed successfully!"
echo "📅 The script will run daily at 6:00 AM"
echo "📝 Logs will be saved to: $PROJECT_DIR/logs/cron.log"
echo ""
echo "To view current cron jobs: crontab -l"
echo "To remove the cron job: crontab -e (then delete the TeenBuzz line)"
echo "To test the script manually: $SCRIPT_PATH"

