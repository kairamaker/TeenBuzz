#!/bin/bash

# Daily Article Fetch Script for TeenBuzz
# This script runs the daily article automation

# Set the project directory
PROJECT_DIR="/Users/kairaschool/Downloads/TeenBuzz"
cd "$PROJECT_DIR"

# Activate virtual environment
source teenbuzz_env/bin/activate

# Run the daily automation
echo "🚀 Starting daily article fetch..."
python daily_article_automation.py

# Check exit status
if [ $? -eq 0 ]; then
    echo "✅ Daily fetch completed successfully!"
else
    echo "❌ Daily fetch failed!"
    exit 1
fi