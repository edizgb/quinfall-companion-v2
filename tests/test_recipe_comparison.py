"""
Test cases for recipe comparison utilities
"""
import unittest
from utils.recipe_utils import compare_materials, compare_output_stats, compare_profession_reqs

class TestRecipeComparison(unittest.TestCase):
    def test_material_comparison(self):
        old = {"iron": 2, "coal": 1}
        new = {"iron": 3, "steel": 1}
        result = compare_materials(old, new)
        self.assertEqual(result["iron"]["action"], "quantity_changed")
        self.assertEqual(result["coal"]["action"], "removed")
        self.assertEqual(result["steel"]["action"], "added")

    def test_output_stats_comparison(self):
        old = {"damage": 10, "durability": 100}
        new = {"damage": 15, "weight": 5}
        result = compare_output_stats(old, new)
        self.assertEqual(result["damage"]["action"], "value_changed")
        self.assertEqual(result["durability"]["action"], "removed")
        self.assertEqual(result["weight"]["action"], "added")

    def test_profession_comparison(self):
        old = {"profession": "blacksmith", "skill_level": 2}
        new = {"profession": "armorsmith", "skill_level": 3}
        result = compare_profession_reqs(old, new)
        self.assertEqual(result["profession"]["old"], "blacksmith")
        self.assertEqual(result["skill_level"]["new"], 3)

if __name__ == "__main__":
    unittest.main()
