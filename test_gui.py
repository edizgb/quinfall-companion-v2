#!/usr/bin/env python3
"""
GUI Test Script for Quinfall Companion
Tests basic functionality and value persistence in 2 rounds
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_gui.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required modules can be imported"""
    logger.info("🔍 Testing imports...")
    
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow
        logger.info("✅ PySide6 import successful")
    except ImportError as e:
        logger.error(f"❌ PySide6 import failed: {e}")
        return False
    
    try:
        from ui.main_window import MainTabs
        from ui.crafting_tab import CraftingTab
        from ui.gathering_tab import GatheringTab
        from ui.specialization_tab import SpecializationTab
        from data.player import Player
        logger.info("✅ All UI modules import successful")
    except ImportError as e:
        logger.error(f"❌ UI module import failed: {e}")
        return False
    
    return True

def test_player_system():
    """Test player system functionality"""
    logger.info("🧪 Testing Player System...")
    
    try:
        from data.player import Player
        
        # Create test player
        player = Player()
        logger.info(f"✅ Player created with {len(player.skills)} skills")
        
        # Test skill modification
        from data.enums import Profession
        original_blacksmithing = player.skills.get(Profession.BLACKSMITHING, 1)
        player.skills[Profession.BLACKSMITHING] = 50
        logger.info(f"✅ Blacksmithing skill changed from {original_blacksmithing} to 50")
        
        # Test save/load
        player.save()
        logger.info("✅ Player data saved")
        
        # Create new player instance and load
        player2 = Player()
        player2.load()
        loaded_blacksmithing = player2.skills.get(Profession.BLACKSMITHING, 1)
        
        if loaded_blacksmithing == 50:
            logger.info("✅ Player data persistence verified")
            return True
        else:
            logger.error(f"❌ Data persistence failed: expected 50, got {loaded_blacksmithing}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Player system test failed: {e}")
        return False

def test_storage_system():
    """Test storage system functionality"""
    logger.info("🧪 Testing Storage System...")
    
    try:
        from data.storage_system import QuinfallStorageSystem, StorageLocation
        
        # Create storage system
        storage = QuinfallStorageSystem("test_player")
        logger.info("✅ Storage system created")
        
        # Test item management
        storage.set_item_count("Iron Ore", 100, StorageLocation.PLAYER_INVENTORY)
        count = storage.get_item_count("Iron Ore", StorageLocation.PLAYER_INVENTORY)
        
        if count == 100:
            logger.info("✅ Storage item management works")
        else:
            logger.error(f"❌ Storage failed: expected 100, got {count}")
            return False
        
        # Test save/load
        storage.save()
        logger.info("✅ Storage data saved")
        
        # Load in new instance
        storage2 = QuinfallStorageSystem("test_player")
        storage2.load()
        loaded_count = storage2.get_item_count("Iron Ore", StorageLocation.PLAYER_INVENTORY)
        
        if loaded_count == 100:
            logger.info("✅ Storage data persistence verified")
            return True
        else:
            logger.error(f"❌ Storage persistence failed: expected 100, got {loaded_count}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Storage system test failed: {e}")
        return False

def test_recipe_data():
    """Test recipe data loading"""
    logger.info("🧪 Testing Recipe Data...")
    
    try:
        from ui.crafting_tab import CRAFTING_RECIPES, load_recipes
        logger.info(f"✅ Loaded {len(CRAFTING_RECIPES)} recipes")
        
        # Test recipe structure
        if CRAFTING_RECIPES:
            sample_recipe = CRAFTING_RECIPES[0]
            required_fields = ['name', 'profession', 'skill_level', 'materials']
            
            for field in required_fields:
                if not hasattr(sample_recipe, field):
                    logger.error(f"❌ Recipe missing field: {field}")
                    return False
            
            # Test recipe by profession
            from data.enums import Profession
            prof_counts = {}
            for recipe in CRAFTING_RECIPES:
                prof_name = recipe.profession.name if hasattr(recipe.profession, 'name') else str(recipe.profession)
                prof_counts[prof_name] = prof_counts.get(prof_name, 0) + 1
            
            logger.info(f"✅ Recipe distribution: {prof_counts}")
            logger.info("✅ Recipe structure validated")
            return True
        else:
            logger.warning("⚠️ No recipes loaded")
            return False
            
    except Exception as e:
        logger.error(f"❌ Recipe data test failed: {e}")
        return False

def test_gui_creation():
    """Test GUI creation without showing it"""
    logger.info("🧪 Testing GUI Creation...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from main import CompanionApp
        
        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create main window
        window = CompanionApp()
        logger.info("✅ Main window created successfully")
        
        # Test tabs
        if hasattr(window, 'tabs'):
            logger.info("✅ Tabs system initialized")
        else:
            logger.error("❌ Tabs system not found")
            return False
        
        # Don't show the window, just test creation
        window.close()
        logger.info("✅ GUI creation test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ GUI creation test failed: {e}")
        return False

def run_test_round(round_num):
    """Run a complete test round"""
    logger.info(f"🚀 Starting Test Round {round_num}")
    
    tests = [
        ("Import Test", test_imports),
        ("Player System", test_player_system),
        ("Storage System", test_storage_system),
        ("Recipe Data", test_recipe_data),
        ("GUI Creation", test_gui_creation)
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"Running {test_name}...")
        results[test_name] = test_func()
        
    # Summary
    passed = sum(results.values())
    total = len(results)
    logger.info(f"📊 Round {round_num} Results: {passed}/{total} tests passed")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {test_name}: {status}")
    
    return results

def main():
    """Main test function"""
    logger.info("🎯 Quinfall Companion GUI Test Suite")
    logger.info("=" * 50)
    
    # Round 1: Initial test
    round1_results = run_test_round(1)
    
    logger.info("\n" + "=" * 50)
    logger.info("⏳ Waiting between test rounds...")
    
    # Round 2: Persistence test
    round2_results = run_test_round(2)
    
    # Final summary
    logger.info("\n" + "=" * 50)
    logger.info("📋 FINAL TEST SUMMARY")
    logger.info("=" * 50)
    
    all_tests = set(round1_results.keys()) | set(round2_results.keys())
    
    for test_name in all_tests:
        r1 = "✅" if round1_results.get(test_name, False) else "❌"
        r2 = "✅" if round2_results.get(test_name, False) else "❌"
        logger.info(f"{test_name}: Round 1: {r1}, Round 2: {r2}")
    
    # Check for persistence issues
    persistence_issues = []
    for test_name in all_tests:
        if round1_results.get(test_name, False) and not round2_results.get(test_name, False):
            persistence_issues.append(test_name)
    
    if persistence_issues:
        logger.warning(f"⚠️ Potential persistence issues in: {', '.join(persistence_issues)}")
    else:
        logger.info("✅ No persistence issues detected")
    
    # Overall result
    total_r1 = sum(round1_results.values())
    total_r2 = sum(round2_results.values())
    total_tests = len(all_tests)
    
    logger.info(f"🎯 Overall: Round 1: {total_r1}/{total_tests}, Round 2: {total_r2}/{total_tests}")
    
    if total_r1 == total_tests and total_r2 == total_tests:
        logger.info("🎉 ALL TESTS PASSED! Application is ready for use.")
        return True
    else:
        logger.warning("⚠️ Some tests failed. Check logs for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
