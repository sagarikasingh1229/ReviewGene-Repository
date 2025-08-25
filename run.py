#!/usr/bin/env python3
"""
Simple launcher script for the Review Generator
"""

import sys
from pathlib import Path

try:
    # Try to import and run the simplified version
    from review_generator_simple import main
    main()
except ImportError:
    print("❌ Could not import review_generator_simple.py")
    print("💡 Make sure the file exists and all dependencies are installed")
    print("🔧 Try running: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 Check the configuration and try again") 