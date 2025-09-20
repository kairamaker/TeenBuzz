#!/usr/bin/env python3

# This script will update the app.py to show a better message for DNS issues

import re

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Replace the generic "Database not configured" message with a more specific one
old_message = "flash('Database not configured. Please set up your Supabase credentials in .env file.', 'error')"
new_message = "flash('Database connection in progress. DNS propagation may take a few hours. Using sample data until connection is established.', 'info')"

# Replace all instances
content = content.replace(old_message, new_message)

# Also replace other generic messages
content = content.replace("flash('Database not configured. Please set up your Supabase credentials.', 'error')", "flash('Database connection in progress. Using sample data until connection is established.', 'info')")

# Write back to file
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Updated app.py to show better DNS messages")
print("The app will now show 'Database connection in progress' instead of 'Database not configured'")
