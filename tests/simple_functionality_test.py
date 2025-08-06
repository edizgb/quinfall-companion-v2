#!/usr/bin/env python3
"""
Simple Functionality Test for Quinfall Companion App
Tests core functionality without complex GUI automation.
"""

import sys
import json
import os
import logging
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)

def test_recipe_loading():
    """Test multi-file recipe loading"""
    logger.info("🔍 Testing Recipe Loading...")
    
    try:
        from ui.crafting_tab import CRAFTING_RECIPES, load_recipes
        
        # Test recipe loading
        recipes = load_recipes()
        total_count = len(recipes)
        
        logger.info(f"✅ Loaded {total_count} recipes total")
        
        # Count by profession
        prof_counts = {}
        for recipe in recipes:
            prof_name = recipe.profession.name if hasattr(recipe.profession, 'name') else str(recipe.profession)
            prof_counts[prof_name] = prof_counts.get(prof_name, 0) + 1
        
        logger.info("📊 Recipes by profession:")
        for prof, count in prof_counts.items():
            logger.info(f"   {prof}: {count} recipes")
        
        # Test specific professions
        expected_profs = ['WEAPONSMITH', 'COOKING', 'WOODWORKING', 'TAILORING', 'ALCHEMY']
        found_profs = list(prof_counts.keys())
        
        success = len(set(expected_profs) & set(found_profs)) >= 4
        
        if success:
            logger.info("✅ Multi-file recipe loading: SUCCESS")
        else:
            logger.error("❌ Multi-file recipe loading: FAILED")
            
        return success, total_count, prof_counts
        
    except Exception as e:
        logger.error(f"❌ Recipe loading failed: {e}")
        return False, 0, {}

def test_recipe_data_integrity():
    """Test recipe data integrity"""
    logger.info("\n🔍 Testing Recipe Data Integrity...")
    
    try:
        from ui.crafting_tab import CRAFTING_RECIPES
        
        issues = []
        valid_recipes = 0
        
        for i, recipe in enumerate(CRAFTING_RECIPES):
            # Check required fields
            if not hasattr(recipe, 'name') or not recipe.name:
                issues.append(f"Recipe {i}: Missing name")
                continue
                
            if not hasattr(recipe, 'profession'):
                issues.append(f"Recipe {recipe.name}: Missing profession")
                continue
                
            if not hasattr(recipe, 'skill_level') or recipe.skill_level < 1:
                issues.append(f"Recipe {recipe.name}: Invalid skill level")
                continue
                
            if not hasattr(recipe, 'materials') or not recipe.materials:
                issues.append(f"Recipe {recipe.name}: Missing materials")
                continue
                
            valid_recipes += 1
        
        logger.info(f"✅ Valid recipes: {valid_recipes}/{len(CRAFTING_RECIPES)}")
        
        if issues:
            logger.warning("⚠️ Issues found:")
            for issue in issues[:5]:  # Show first 5 issues
                logger.warning(f"   {issue}")
            if len(issues) > 5:
                logger.warning(f"   ... and {len(issues)-5} more issues")
        else:
            logger.info("✅ All recipes have valid data structure")
            
        return len(issues) == 0, valid_recipes, issues
        
    except Exception as e:
        logger.error(f"❌ Recipe data integrity test failed: {e}")
        return False, 0, [str(e)]

def test_price_data():
    """Test price data availability"""
    logger.info("\n🔍 Testing Price Data...")
    
    try:
        from ui.crafting_tab import CRAFTING_RECIPES
        
        recipes_with_prices = 0
        recipes_without_prices = 0
        
        for recipe in CRAFTING_RECIPES:
            has_material_prices = hasattr(recipe, 'material_prices') and recipe.material_prices
            has_output_prices = hasattr(recipe, 'output_prices') and recipe.output_prices
            
            if has_material_prices and has_output_prices:
                recipes_with_prices += 1
            else:
                recipes_without_prices += 1
        
        logger.info(f"✅ Recipes with price data: {recipes_with_prices}")
        logger.warning(f"⚠️ Recipes without price data: {recipes_without_prices}")
        
        price_coverage = recipes_with_prices / len(CRAFTING_RECIPES) * 100
        logger.info(f"📊 Price data coverage: {price_coverage:.1f}%")
        
        return price_coverage > 50, recipes_with_prices, recipes_without_prices
        
    except Exception as e:
        logger.error(f"❌ Price data test failed: {e}")
        return False, 0, 0

def test_player_persistence():
    """Test player data persistence"""
    logger.info("\n🔍 Testing Player Data Persistence...")
    
    try:
        from data.player import Player
        
        # Create test player
        player = Player()
        
        # Set test values
        test_skill = 42
        test_tool = 33
        test_profession = "WEAPONSMITH"
        
        player.skills[test_profession] = test_skill
        player.tools[test_profession] = test_tool
        player.tool_types[test_profession] = "Advanced"
        
        # Save
        player.save()
        logger.info("✅ Player data saved")
        
        # Load new instance
        player2 = Player()
        player2.load()
        
        # Check values
        loaded_skill = player2.skills.get(test_profession, 0)
        loaded_tool = player2.tools.get(test_profession, 0)
        loaded_tool_type = player2.tool_types.get(test_profession, "Basic")
        
        skill_match = loaded_skill == test_skill
        tool_match = loaded_tool == test_tool
        tool_type_match = loaded_tool_type == "Advanced"
        
        logger.info(f"✅ Skill persistence: {skill_match} ({loaded_skill} == {test_skill})")
        logger.info(f"✅ Tool persistence: {tool_match} ({loaded_tool} == {test_tool})")
        logger.info(f"✅ Tool type persistence: {tool_type_match} ({loaded_tool_type} == Advanced)")
        
        return skill_match and tool_match and tool_type_match
        
    except Exception as e:
        logger.error(f"❌ Player persistence test failed: {e}")
        return False

def main():
    """Run all functionality tests"""
    logger.info("🎯 QUINFALL COMPANION - FUNCTIONALITY TEST")
    logger.info("=" * 50)
    
    results = {}
    
    # Test 1: Recipe Loading
    recipe_success, total_recipes, prof_counts = test_recipe_loading()
    results['recipe_loading'] = recipe_success
    
    # Test 2: Recipe Data Integrity
    integrity_success, valid_recipes, issues = test_recipe_data_integrity()
    results['data_integrity'] = integrity_success
    
    # Test 3: Price Data
    price_success, with_prices, without_prices = test_price_data()
    results['price_data'] = price_success
    
    # Test 4: Player Persistence
    persistence_success = test_player_persistence()
    results['persistence'] = persistence_success
    
    # Final Report
    logger.info("\n" + "=" * 50)
    logger.info("📊 FINAL FUNCTIONALITY REPORT")
    logger.info("=" * 50)
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    logger.info(f"Tests Passed: {passed}/{total}")
    logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
    
    logger.info("\nDetailed Results:")
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"  {status}: {test_name}")
    
    # Key Metrics
    logger.info(f"\n📈 Key Metrics:")
    logger.info(f"  Total Recipes: {total_recipes}")
    logger.info(f"  Valid Recipes: {valid_recipes}")
    logger.info(f"  Professions: {len(prof_counts)}")
    logger.info(f"  Recipes with Prices: {with_prices}")

    # Conclusion
    if passed == total:
        logger.info("\n🎉 ALL FUNCTIONALITY TESTS PASSED!")
        logger.info("✅ Multi-file recipe loading works")
        logger.info("✅ Recipe data integrity is good")
        logger.info("✅ Price data is available")
        logger.info("✅ Player persistence works")
        logger.info("\n🚀 READY TO PROCEED:")
        logger.info("   1. Add more crafting professions")
        logger.info("   2. Implement gathering system")
        logger.info("   3. Add specialization tracking")
        logger.info("   4. Implement API sync")
        logger.info("   5. Add proper logging")
        return True
    else:
        logger.info(f"\n⚠️ {total-passed} TESTS FAILED")
        logger.info("Review issues above before proceeding")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
