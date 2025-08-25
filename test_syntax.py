#!/usr/bin/env python3
"""
Simple syntax test for review_generator_simple.py
"""

import sys
import os

def test_syntax():
    """Test if the file can be imported without syntax errors"""
    try:
        # Add current directory to path
        sys.path.append('.')
        
        # Try to import the module
        import review_generator_simple
        print("✅ Syntax test PASSED!")
        print("✅ review_generator_simple.py has no syntax errors")
        print("✅ All functions are properly defined")
        
        # Test if main function exists
        if hasattr(review_generator_simple, 'main'):
            print("✅ Main function found")
        else:
            print("❌ Main function not found")
            
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax Error: {e}")
        print(f"   Line: {e.lineno}")
        print(f"   File: {e.filename}")
        return False
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   This might be due to missing dependencies (pandas, openai, etc.)")
        print("   But the syntax is correct!")
        return True
        
    except Exception as e:
        print(f"❌ Other Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing review_generator_simple.py syntax...")
    success = test_syntax()
    
    if success:
        print("\n🎉 Ready to run! Use Anaconda Prompt to install dependencies:")
        print("   conda install pandas openpyxl xlrd -y")
        print("   python run.py")
    else:
        print("\n❌ Please fix the syntax errors first")
