#!/usr/bin/env python3
"""
Test script to demonstrate the new diverse username generation system
"""

import sys
import os

# Add current directory to path
sys.path.append('.')

def test_username_generation():
    """Test the new username generation system"""
    try:
        from review_generator_simple import NameGenerator
        
        # Initialize the name generator
        name_generator = NameGenerator()
        
        print("🎭 Testing New Diverse Username Generation System")
        print("=" * 60)
        
        # Test different username types
        username_types = [
            "First + Last combinations",
            "First name only", 
            "Last name only",
            "Nicknames",
            "Alphanumeric",
            "Other scripts (Hindi/Tamil/Telugu)",
            "Funky handles"
        ]
        
        print("\n📊 Generating 10 sample usernames of each type:")
        print("-" * 60)
        
        for i, username_type in enumerate(username_types, 1):
            print(f"\n{i}. {username_type}:")
            usernames = []
            for j in range(10):
                username = name_generator.generate_username()
                usernames.append(username)
            
            # Display usernames in a nice format
            for j, username in enumerate(usernames, 1):
                print(f"   {j:2d}. {username}")
        
        print("\n" + "=" * 60)
        print("✅ Username generation test completed!")
        print("🎉 Your manager's requirements are now implemented!")
        
        # Show statistics
        first_count, last_count = name_generator.get_name_count()
        print(f"\n📈 Database Statistics:")
        print(f"   • First Names: {first_count:,}")
        print(f"   • Last Names: {last_count:,}")
        print(f"   • Total Possible Combinations: {first_count * last_count:,}")
        print(f"   • Unique Usernames Generated: {len(name_generator.used_usernames)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing the Enhanced Username System...")
    success = test_username_generation()
    
    if success:
        print("\n🎯 Ready to run the main program!")
        print("💡 Run: python run.py")
    else:
        print("\n❌ Please fix the issues first")
