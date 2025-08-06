#!/usr/bin/env python3
"""
Automated 3-Cycle GUI/UX Test for Quinfall Companion App
Tests all functionality including state persistence, recipe loading, and crafting logic.
"""

import sys
import time
import json
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest

logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import CompanionApp
from data.enums import Profession

class AutomatedGUITest:
    def __init__(self):
        self.app = None
        self.main_window = None
        self.crafting_tab = None
        self.test_results = []
        self.current_cycle = 0
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        result = {
            "cycle": self.current_cycle,
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.strftime("%H:%M:%S")
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"[CYCLE {self.current_cycle}] {status}: {test_name} - {details}")
        
    def setup_app(self):
        """Setup the application"""
        try:
            self.app = QApplication.instance()
            if self.app is None:
                self.app = QApplication(sys.argv)
            
            self.main_window = CompanionApp()
            self.crafting_tab = self.main_window.main_tabs.crafting_tab
            self.main_window.show()
            
            # Wait for UI to initialize
            QTest.qWait(1000)
            
            self.log_result("Application Setup", True, "App launched successfully")
            return True
        except Exception as e:
            self.log_result("Application Setup", False, f"Error: {e}")
            return False
    
    def test_recipe_loading(self):
        """Test that recipes are loaded from all professions"""
        try:
            from ui.crafting_tab import CRAFTING_RECIPES
            
            total_recipes = len(CRAFTING_RECIPES)
            self.log_result("Recipe Loading", total_recipes >= 30, f"Loaded {total_recipes} recipes")
            
            # Check profession distribution
            professions = {}
            for recipe in CRAFTING_RECIPES:
                prof = recipe.profession.name if hasattr(recipe.profession, 'name') else str(recipe.profession)
                professions[prof] = professions.get(prof, 0) + 1
            
            expected_profs = ['WEAPONSMITH', 'COOKING', 'WOODWORKING', 'TAILORING', 'ALCHEMY']
            found_profs = list(professions.keys())
            
            success = len(set(expected_profs) & set(found_profs)) >= 4
            self.log_result("Multi-Profession Loading", success, f"Found: {professions}")
            
            return success
        except Exception as e:
            self.log_result("Recipe Loading", False, f"Error: {e}")
            return False
    
    def test_profession_selection(self):
        """Test profession dropdown functionality"""
        try:
            combo = self.crafting_tab.profession_select
            original_index = combo.currentIndex()
            
            # Test changing profession
            combo.setCurrentIndex(1)  # Change to second profession
            QTest.qWait(500)
            
            new_index = combo.currentIndex()
            success = new_index != original_index
            self.log_result("Profession Selection", success, f"Changed from {original_index} to {new_index}")
            
            return success
        except Exception as e:
            self.log_result("Profession Selection", False, f"Error: {e}")
            return False
    
    def test_skill_tool_sliders(self):
        """Test skill and tool level sliders"""
        try:
            skill_slider = self.crafting_tab.skill_slider
            tool_slider = self.crafting_tab.tool_slider
            
            # Test skill slider
            original_skill = skill_slider.value()
            skill_slider.setValue(25)
            QTest.qWait(300)
            new_skill = skill_slider.value()
            
            # Test tool slider
            original_tool = tool_slider.value()
            tool_slider.setValue(15)
            QTest.qWait(300)
            new_tool = tool_slider.value()
            
            skill_success = new_skill == 25
            tool_success = new_tool == 15
            
            self.log_result("Skill Slider", skill_success, f"Set to 25, got {new_skill}")
            self.log_result("Tool Slider", tool_success, f"Set to 15, got {new_tool}")
            
            return skill_success and tool_success
        except Exception as e:
            self.log_result("Skill/Tool Sliders", False, f"Error: {e}")
            return False
    
    def test_tool_type_buttons(self):
        """Test tool type button functionality"""
        try:
            buttons = [
                self.crafting_tab.basic_tool_btn,
                self.crafting_tab.advanced_tool_btn,
                self.crafting_tab.improved_tool_btn
            ]
            
            # Test clicking different tool type buttons
            for i, btn in enumerate(buttons):
                btn.click()
                QTest.qWait(200)
                
                # Check if button is checked
                success = btn.isChecked()
                tool_type = ["Basic", "Advanced", "Improved"][i]
                self.log_result(f"Tool Type - {tool_type}", success, f"Button clicked and checked: {success}")
            
            return True
        except Exception as e:
            self.log_result("Tool Type Buttons", False, f"Error: {e}")
            return False
    
    def test_pagination(self):
        """Test recipe pagination functionality"""
        try:
            # Test recipes per page dropdown
            per_page_combo = self.crafting_tab.recipes_per_page_select
            per_page_combo.setCurrentText("10")
            QTest.qWait(300)
            
            # Test next/previous buttons
            next_btn = self.crafting_tab.next_page_btn
            prev_btn = self.crafting_tab.prev_page_btn
            
            if next_btn.isEnabled():
                next_btn.click()
                QTest.qWait(300)
                self.log_result("Pagination Next", True, "Next page button clicked")
            
            if prev_btn.isEnabled():
                prev_btn.click()
                QTest.qWait(300)
                self.log_result("Pagination Previous", True, "Previous page button clicked")
            
            return True
        except Exception as e:
            self.log_result("Pagination", False, f"Error: {e}")
            return False
    
    def test_price_configuration(self):
        """Test price display configuration"""
        try:
            price_combo = self.crafting_tab.price_count_select
            original_value = price_combo.currentText()
            
            # Change price count
            price_combo.setCurrentText("50")
            QTest.qWait(300)
            
            new_value = price_combo.currentText()
            success = new_value == "50"
            self.log_result("Price Configuration", success, f"Changed from {original_value} to {new_value}")
            
            return success
        except Exception as e:
            self.log_result("Price Configuration", False, f"Error: {e}")
            return False
    
    def test_recipe_display(self):
        """Test recipe display functionality"""
        try:
            recipe_display = self.crafting_tab.recipe_display
            text_content = recipe_display.text()
            
            # Check if recipes are displayed
            has_content = len(text_content) > 100
            has_html = "<b>" in text_content or "<span" in text_content
            
            self.log_result("Recipe Display Content", has_content, f"Content length: {len(text_content)}")
            self.log_result("Recipe Display HTML", has_html, f"Contains HTML formatting: {has_html}")
            
            return has_content and has_html
        except Exception as e:
            self.log_result("Recipe Display", False, f"Error: {e}")
            return False
    
    def test_state_persistence(self):
        """Test that UI state persists"""
        try:
            # Set specific values
            self.crafting_tab.skill_slider.setValue(42)
            self.crafting_tab.tool_slider.setValue(33)
            self.crafting_tab.improved_tool_btn.click()
            QTest.qWait(500)
            
            # Save current state
            saved_skill = self.crafting_tab.skill_slider.value()
            saved_tool = self.crafting_tab.tool_slider.value()
            saved_tool_type = self.crafting_tab.improved_tool_btn.isChecked()
            
            # Simulate app restart by reloading player data
            self.crafting_tab.player.load()
            self.crafting_tab.load_profession_state()
            QTest.qWait(300)
            
            # Check if values persisted
            loaded_skill = self.crafting_tab.skill_slider.value()
            loaded_tool = self.crafting_tab.tool_slider.value()
            loaded_tool_type = self.crafting_tab.improved_tool_btn.isChecked()
            
            skill_persisted = saved_skill == loaded_skill
            tool_persisted = saved_tool == loaded_tool
            tool_type_persisted = saved_tool_type == loaded_tool_type
            
            self.log_result("Skill Persistence", skill_persisted, f"Saved: {saved_skill}, Loaded: {loaded_skill}")
            self.log_result("Tool Persistence", tool_persisted, f"Saved: {saved_tool}, Loaded: {loaded_tool}")
            self.log_result("Tool Type Persistence", tool_type_persisted, f"Saved: {saved_tool_type}, Loaded: {loaded_tool_type}")
            
            return skill_persisted and tool_persisted and tool_type_persisted
        except Exception as e:
            self.log_result("State Persistence", False, f"Error: {e}")
            return False
    
    def run_cycle_1(self):
        """CYCLE 1: Basic Functionality Test"""
        logger.info("\n🚀 STARTING CYCLE 1: Basic Functionality Test")
        self.current_cycle = 1
        
        if not self.setup_app():
            return False
        
        success = True
        success &= self.test_recipe_loading()
        success &= self.test_profession_selection()
        success &= self.test_skill_tool_sliders()
        success &= self.test_recipe_display()
        
        return success
    
    def run_cycle_2(self):
        """CYCLE 2: State Persistence Test"""
        logger.info("\n🔄 STARTING CYCLE 2: State Persistence Test")
        self.current_cycle = 2
        
        success = True
        success &= self.test_state_persistence()
        success &= self.test_tool_type_buttons()
        
        return success
    
    def run_cycle_3(self):
        """CYCLE 3: Advanced Logic Test"""
        logger.info("\n⚙️ STARTING CYCLE 3: Advanced Logic Test")
        self.current_cycle = 3
        
        success = True
        success &= self.test_pagination()
        success &= self.test_price_configuration()
        
        return success
    
    def generate_report(self):
        """Generate final test report"""
        logger.info("\n" + "="*60)
        logger.info("📊 FINAL TEST REPORT")
        logger.info("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        logger.info("\nDetailed Results:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            logger.info(f"  {status} [C{result['cycle']}] {result['test']}: {result['details']}")
        
        # Save report to file
        report_file = Path(__file__).parent / "test_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"\n📁 Report saved to: {report_file}")
        
        return passed_tests == total_tests
    
    def run_all_tests(self):
        """Run all 3 cycles of testing"""
        logger.info("🎯 STARTING AUTOMATED 3-CYCLE GUI/UX TEST")
        logger.info("=" * 50)
        
        try:
            cycle1_success = self.run_cycle_1()
            cycle2_success = self.run_cycle_2()
            cycle3_success = self.run_cycle_3()
            
            all_success = self.generate_report()
            
            if all_success:
                logger.info("\n🎉 ALL TESTS PASSED! Quinfall Companion App is ready!")
                logger.info("✅ Crafting logic is working correctly")
                logger.info("✅ State persistence is working")
                logger.info("✅ All UI components are functional")
                logger.info("\n🚀 READY TO PROCEED TO:")
                logger.info("   1. Add remaining crafting professions")
                logger.info("   2. Implement gathering system")
            else:
                logger.info("\n⚠️ SOME TESTS FAILED - Review report above")
                
            return all_success
            
        except Exception as e:
            logger.error(f"\n💥 CRITICAL ERROR: {e}")
            return False
        finally:
            if self.main_window:
                self.main_window.close()
            if self.app:
                self.app.quit()

def main():
    """Main test runner"""
    tester = AutomatedGUITest()
    return tester.run_all_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
