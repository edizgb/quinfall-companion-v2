import unittest
from PySide6.QtWidgets import QApplication
from data.enums import Profession, Recipe, ProfessionTier, ToolType
from ui.crafting_tab import CraftingTab
from data.player import Player

app = QApplication([])

class TestCraftingErrors(unittest.TestCase):
    def setUp(self):
        self.player = Player()
        self.crafting_tab = CraftingTab()
        self.crafting_tab.player = self.player
        
    def test_skill_level_error(self):
        recipe = Recipe("Test Item", Profession.WEAPONSMITH, 
                       ProfessionTier.MASTER, {}, ToolType.FORGE, 1)
        result = self.crafting_tab.craft_item(recipe)
        self.assertFalse(result)
        
    def test_tool_level_error(self):
        recipe = Recipe("Test Item", Profession.WEAPONSMITH,
                       ProfessionTier.APPRENTICE, {}, ToolType.FORGE, 5)
        result = self.crafting_tab.craft_item(recipe)
        self.assertFalse(result)
