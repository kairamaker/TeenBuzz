#!/usr/bin/env python3
"""
Set up daily automation for article fetching at 9am
"""

import os
import subprocess
import sys
from pathlib import Path

def setup_daily_automation():
    """Set up cron job for daily article fetching at 9am"""
    try:
        # Get the current directory
        current_dir = Path(__file__).parent.absolute()
        script_path = current_dir / "fetch_real_articles_local.py"
        python_path = current_dir / "teenbuzz_env" / "bin" / "python"
        
        # Create the cron job command
        cron_command = f"0 9 * * * cd {current_dir} && {python_path} {script_path} >> {current_dir}/daily_fetch.log 2>&1"
        
        print("🔧 Setting up daily automation...")
        print(f"📁 Working directory: {current_dir}")
        print(f"🐍 Python path: {python_path}")
        print(f"📜 Script path: {script_path}")
        print(f"⏰ Cron command: {cron_command}")
        
        # Check if cron job already exists
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if "fetch_real_articles_local.py" in result.stdout:
                print("✅ Daily automation already set up!")
                return True
        except:
            pass
        
        # Add the cron job
        try:
            # Get existing crontab
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            existing_cron = result.stdout if result.returncode == 0 else ""
            
            # Add our new job
            new_cron = existing_cron + "\n" + cron_command + "\n"
            
            # Write to crontab
            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_cron)
            
            if process.returncode == 0:
                print("✅ Daily automation set up successfully!")
                print("📅 Articles will be fetched daily at 9:00 AM")
                print("📝 Logs will be saved to daily_fetch.log")
                return True
            else:
                print("❌ Failed to set up cron job")
                return False
                
        except Exception as e:
            print(f"❌ Error setting up cron job: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error in setup_daily_automation: {e}")
        return False

def create_manual_fetch_script():
    """Create a manual fetch script for testing"""
    script_content = """#!/bin/bash
# Manual article fetch script
cd "$(dirname "$0")"
source teenbuzz_env/bin/activate
python fetch_real_articles_local.py
"""
    
    script_path = Path(__file__).parent / "manual_fetch.sh"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make it executable
    os.chmod(script_path, 0o755)
    print(f"✅ Created manual fetch script: {script_path}")
    return True

if __name__ == "__main__":
    print("🚀 Setting up TeenBuzz Daily Automation...")
    
    # Create manual fetch script
    create_manual_fetch_script()
    
    # Set up cron job
    success = setup_daily_automation()
    
    if success:
        print("\n🎉 Daily automation setup complete!")
        print("\n📋 What's been set up:")
        print("  ✅ Daily article fetching at 9:00 AM")
        print("  ✅ Automatic log file (daily_fetch.log)")
        print("  ✅ Manual fetch script (manual_fetch.sh)")
        print("\n🔧 Manual commands:")
        print("  • Run manual fetch: ./manual_fetch.sh")
        print("  • Check cron jobs: crontab -l")
        print("  • View logs: tail -f daily_fetch.log")
    else:
        print("❌ Daily automation setup failed.")
        sys.exit(1)
