#!/usr/bin/env python3
"""
TeenBuzz Automation Management Script
Provides commands to manage the daily article automation system
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_DIR = Path(__file__).parent

def run_command(command, description):
    """Run a command and return the result"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def check_cron_job():
    """Check if the cron job is set up"""
    print("🔍 Checking cron job status...")
    try:
        result = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
        if "run_daily_fetch.sh" in result.stdout:
            print("✅ Cron job is installed")
            for line in result.stdout.split('\n'):
                if "run_daily_fetch.sh" in line and not line.startswith('#'):
                    print(f"📅 Schedule: {line}")
            return True
        else:
            print("❌ Cron job not found")
            return False
    except Exception as e:
        print(f"❌ Error checking cron job: {e}")
        return False

def view_logs():
    """View recent automation logs"""
    print("📋 Recent automation logs:")
    
    # Check today's log
    today_log = PROJECT_DIR / "logs" / f"daily_fetch_{datetime.now().strftime('%Y%m%d')}.log"
    if today_log.exists():
        print(f"\n📅 Today's log ({today_log.name}):")
        with open(today_log, 'r') as f:
            lines = f.readlines()
            # Show last 20 lines
            for line in lines[-20:]:
                print(f"  {line.strip()}")
    else:
        print("📅 No log file for today")
    
    # Check cron log
    cron_log = PROJECT_DIR / "logs" / "cron.log"
    if cron_log.exists():
        print(f"\n⏰ Cron log ({cron_log.name}):")
        with open(cron_log, 'r') as f:
            lines = f.readlines()
            # Show last 10 lines
            for line in lines[-10:]:
                print(f"  {line.strip()}")
    else:
        print("⏰ No cron log file")

def test_automation():
    """Test the automation system"""
    print("🧪 Testing automation system...")
    script_path = PROJECT_DIR / "run_daily_fetch.sh"
    
    if not script_path.exists():
        print("❌ Automation script not found")
        return False
    
    return run_command(f"bash {script_path}", "Running daily fetch test")

def install_cron():
    """Install the cron job"""
    print("🔧 Installing cron job...")
    script_path = PROJECT_DIR / "setup_cron_job.sh"
    
    if not script_path.exists():
        print("❌ Cron setup script not found")
        return False
    
    return run_command(f"bash {script_path}", "Installing cron job")

def remove_cron():
    """Remove the cron job"""
    print("🗑️ Removing cron job...")
    try:
        # Get current crontab
        result = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ No crontab found")
            return False
        
        # Remove TeenBuzz lines
        lines = result.stdout.split('\n')
        filtered_lines = [line for line in lines if "run_daily_fetch.sh" not in line and "TeenBuzz" not in line]
        
        # Write back to crontab
        if filtered_lines:
            new_crontab = '\n'.join(filtered_lines)
            subprocess.run("crontab -", input=new_crontab, shell=True, text=True)
        else:
            subprocess.run("crontab -r", shell=True)
        
        print("✅ Cron job removed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error removing cron job: {e}")
        return False

def show_status():
    """Show automation system status"""
    print("📊 TeenBuzz Automation System Status")
    print("=" * 50)
    
    # Check cron job
    cron_installed = check_cron_job()
    
    # Check log files
    logs_dir = PROJECT_DIR / "logs"
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        print(f"\n📁 Log files: {len(log_files)} found")
        for log_file in log_files:
            size = log_file.stat().st_size
            modified = datetime.fromtimestamp(log_file.stat().st_mtime)
            print(f"  - {log_file.name} ({size} bytes, modified: {modified.strftime('%Y-%m-%d %H:%M')})")
    else:
        print("\n📁 No logs directory found")
    
    # Check database
    try:
        sys.path.insert(0, str(PROJECT_DIR))
        from database_manager import get_database
        
        db = get_database()
        if db:
            total_articles = db.execute_query("SELECT COUNT(*) as count FROM articles")[0]['count']
            print(f"\n💾 Database: {total_articles} articles")
        else:
            print("\n💾 Database: Not connected")
    except Exception as e:
        print(f"\n💾 Database: Error - {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="TeenBuzz Automation Management")
    parser.add_argument("command", choices=[
        "status", "test", "install", "remove", "logs", "check"
    ], help="Command to run")
    
    args = parser.parse_args()
    
    if args.command == "status":
        show_status()
    elif args.command == "test":
        test_automation()
    elif args.command == "install":
        install_cron()
    elif args.command == "remove":
        remove_cron()
    elif args.command == "logs":
        view_logs()
    elif args.command == "check":
        check_cron_job()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("TeenBuzz Automation Management")
        print("=" * 40)
        print("Available commands:")
        print("  status  - Show system status")
        print("  test    - Test automation system")
        print("  install - Install cron job")
        print("  remove  - Remove cron job")
        print("  logs    - View recent logs")
        print("  check   - Check cron job status")
        print("\nUsage: python manage_automation.py <command>")
    else:
        main()

