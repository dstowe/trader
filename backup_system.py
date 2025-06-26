# backup_system.py
import os
import shutil
from datetime import datetime

def backup_trading_system():
    """Create a backup of the entire trading system"""
    backup_name = f"trading_system_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Copy entire directory
    shutil.copytree('.', backup_name, ignore=shutil.ignore_patterns('*.db', '__pycache__', '*.pyc'))
    print(f"✅ Backup created: {backup_name}")

if __name__ == "__main__":
    backup_trading_system()