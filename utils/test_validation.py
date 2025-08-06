"""Simplified validation test"""
import json
from pathlib import Path

# Test paths
test_ref = Path('data/material_reference.json')
test_recipes = Path('data/recipes_blacksmithing.json')

# Load test data
with open(test_ref) as f:
    ref_data = json.load(f)
    materials = set(ref_data['materials'])

with open(test_recipes) as f:
    recipes = json.load(f)['recipes']

# Simple validation
for recipe in recipes[:3]:  # Just test first 3 recipes
    print(f"Checking {recipe['recipe_name']}")
    for mat in recipe['materials']:
        if mat not in materials:
            print(f"  Missing material: {mat}")
        else:
            print(f"  Valid material: {mat}")
