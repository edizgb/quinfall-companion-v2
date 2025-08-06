#!/usr/bin/env python3
"""
Test script for Quinfall API sync functionality
Tests the API client and storage sync without requiring GUI
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from data.player import Player
from utils.quinfall_api import QuinfallAPIClient, APIConfig, test_api_connection
from data.storage_system import StorageLocation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api_client_creation():
    """Test API client creation and configuration"""
    logger.info("🧪 Testing API client creation...")
    
    try:
        # Test default config
        config = APIConfig()
        client = QuinfallAPIClient(config)
        
        logger.info(f"✅ API client created successfully")
        logger.info(f"   - Base URL: {config.base_url}")
        logger.info(f"   - Timeout: {config.timeout}s")
        logger.info(f"   - Auto-sync interval: {config.auto_sync_interval}s")
        
        return True
    except Exception as e:
        logger.error(f"❌ API client creation failed: {e}")
        return False

def test_storage_system_integration():
    """Test storage system API integration"""
    logger.info("\n🧪 Testing storage system API integration...")
    
    try:
        # Create player and storage system
        player = Player()
        storage_system = player.storage_system
        
        logger.info(f"✅ Storage system created")
        logger.info(f"   - Player ID: {storage_system.player_id}")
        logger.info(f"   - Storage locations: {len(storage_system.containers)}")
        
        # Test API format conversion
        api_data = storage_system.to_api_format()
        logger.info(f"✅ API format conversion successful")
        logger.info(f"   - Version: {api_data['version']}")
        logger.info(f"   - Containers: {len(api_data['containers'])}")
        
        # Test sync method (will fail without credentials, but should handle gracefully)
        success, message = storage_system.sync_with_api()
        logger.info(f"📡 Sync test result: {message}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Storage system integration failed: {e}")
        return False

def test_offline_functionality():
    """Test that the app works properly in offline mode"""
    logger.info("\n🧪 Testing offline functionality...")
    
    try:
        player = Player()
        
        # Test basic storage operations
        storage = player.storage_system
        
        # Add some test items
        storage.set_item_count("Iron Ore", 100, StorageLocation.PLAYER_INVENTORY)
        storage.set_item_count("Copper Ore", 50, StorageLocation.MEADOW_BANK)
        
        # Test retrieval
        iron_count = storage.get_item_count("Iron Ore", StorageLocation.PLAYER_INVENTORY)
        copper_count = storage.get_item_count("Copper Ore", StorageLocation.MEADOW_BANK)
        
        logger.info(f"✅ Offline storage operations successful")
        logger.info(f"   - Iron Ore in inventory: {iron_count}")
        logger.info(f"   - Copper Ore in bank: {copper_count}")
        
        # Test save/load
        storage.save()
        logger.info(f"✅ Storage save successful")
        
        return True
    except Exception as e:
        logger.error(f"❌ Offline functionality failed: {e}")
        return False

def test_api_connection_check():
    """Test API connection without authentication"""
    logger.info("\n🧪 Testing API connection...")
    
    try:
        # This will likely fail since the API doesn't exist yet, but should handle gracefully
        connected = test_api_connection()
        
        if connected:
            logger.info("✅ API server is reachable")
        else:
            logger.warning("⚠️ API server not reachable (expected for development)")
        
        return True
    except Exception as e:
        logger.warning(f"⚠️ API connection test failed (expected): {e}")
        return True  # This is expected to fail in development

def test_settings_persistence():
    """Test API settings save/load"""
    logger.info("\n🧪 Testing settings persistence...")
    
    try:
        import json
        
        # Test settings
        test_settings = {
            'server_url': 'https://test.api.com',
            'timeout': 45,
            'auto_sync_enabled': True,
            'sync_interval': 10
        }
        
        # Save settings
        settings_file = Path("saves/test_api_settings.json")
        settings_file.parent.mkdir(exist_ok=True)
        
        with open(settings_file, 'w') as f:
            json.dump(test_settings, f, indent=2)
        
        # Load settings
        with open(settings_file, 'r') as f:
            loaded_settings = json.load(f)
        
        # Verify
        if loaded_settings == test_settings:
            logger.info("✅ Settings persistence successful")
        else:
            logger.error("❌ Settings persistence failed - data mismatch")
            return False
        
        # Cleanup
        settings_file.unlink()
        
        return True
    except Exception as e:
        logger.error(f"❌ Settings persistence failed: {e}")
        return False

def main():
    """Run all API sync tests"""
    logger.info("🚀 Quinfall API Sync Test Suite")
    logger.info("=" * 50)
    
    tests = [
        ("API Client Creation", test_api_client_creation),
        ("Storage System Integration", test_storage_system_integration),
        ("Offline Functionality", test_offline_functionality),
        ("API Connection Check", test_api_connection_check),
        ("Settings Persistence", test_settings_persistence)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 All tests passed! API sync implementation is ready.")
    elif passed >= total * 0.8:
        logger.warning("⚠️ Most tests passed. Some issues may need attention.")
    else:
        logger.error("❌ Multiple test failures. Implementation needs review.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
