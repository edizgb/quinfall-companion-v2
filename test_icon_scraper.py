#!/usr/bin/env python3
"""
Test script for automatic icon discovery from Quinfall Wiki
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.icon_manager import QuinfallIconManager

def main():
    print("🔍 Testing Quinfall Wiki Icon Scraper...")
    print("=" * 50)
    
    # Initialize icon manager
    icon_manager = QuinfallIconManager()
    
    # Test automatic icon discovery
    try:
        new_icons = icon_manager.auto_discover_icons()
        
        print("\n" + "=" * 50)
        print(f"📊 SUMMARY: Found {len(new_icons)} icons")
        print("=" * 50)
        
        if new_icons:
            print("\n🎯 New icons discovered:")
            for name, url in sorted(new_icons.items()):
                print(f"  • {name}")
                print(f"    {url}")
                print()
        else:
            print("\n⚠️  No new icons found (may already be cached)")
            
        # Show all known icons
        print(f"\n📋 Total known icons: {len(icon_manager.known_icons)}")
        for name, url in sorted(icon_manager.known_icons.items()):
            if url:  # Only show icons with actual URLs
                print(f"  ✅ {name}")
        
    except Exception as e:
        print(f"❌ Error during icon discovery: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
