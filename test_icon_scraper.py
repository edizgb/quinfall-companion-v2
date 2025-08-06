#!/usr/bin/env python3
"""
Test script for automatic icon discovery from Quinfall Wiki
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.icon_manager import QuinfallIconManager
import traceback
import logging

logger = logging.getLogger(__name__)

def main():
    logger.info("🔍 Testing Quinfall Wiki Icon Scraper...")
    logger.info("=" * 50)
    
    # Initialize icon manager
    icon_manager = QuinfallIconManager()
    
    # Test automatic icon discovery
    try:
        new_icons = icon_manager.auto_discover_icons()
        
        logger.info("\n" + "=" * 50)
        logger.info(f"📊 SUMMARY: Found {len(new_icons)} icons")
        logger.info("=" * 50)
        
        if new_icons:
            logger.info("\n🎯 New icons discovered:")
            for name, url in sorted(new_icons.items()):
                logger.info(f"  • {name}")
                logger.info(f"    {url}")
                logger.info("")
        else:
            logger.info("\n⚠️  No new icons found (may already be cached)")
            
        # Show all known icons
        logger.info(f"\n📋 Total known icons: {len(icon_manager.known_icons)}")
        for name, url in sorted(icon_manager.known_icons.items()):
            if url:  # Only show icons with actual URLs
                logger.info(f"  ✅ {name}")
        
    except Exception as e:
        logger.error(f"❌ Error during icon discovery: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
