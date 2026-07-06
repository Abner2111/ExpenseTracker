#!/usr/bin/env python3
"""
ExpenseTracker GUI Launcher
Simple launcher script for the ExpenseTracker GUI
"""

import sys
import os

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

# Change to src directory
os.chdir(src_path)

try:
    from gui import main
    main()
except ImportError as e:
    print(f"Error: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    input("Press Enter to exit...")
except Exception as e:
    print(f"Unexpected error: {e}")
    input("Press Enter to exit...")
