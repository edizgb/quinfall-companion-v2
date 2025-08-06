"""
Recipe Loader for Quinfall Companion App
Loads recipes from JSON files and provides filtering functionality
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from data.enums import Profession, ToolType, ProfessionTier, Recipe

class RecipeLoader:
    """Loads and manages recipes from JSON files"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.recipes_cache = {}
        self.load_all_recipes()
    
    def load_all_recipes(self):
        """Load all recipes from JSON files"""
        recipe_files = {
            # CRAFTING PROFESSIONS (these have recipes)
            Profession.ALCHEMY: "recipes_alchemy.json",
            Profession.COOKING: "recipes_cooking.json", 
            Profession.WEAPONSMITH: "recipes_weaponsmith.json",
            Profession.ARMORSMITH: "recipes_armorsmith.json",
            Profession.WOODWORKING: "recipes_woodworking.json",
            Profession.SHIPBUILDING: "recipes_shipbuilding.json",
            # Legacy files that need proper mapping
            "BLACKSMITHING": "recipes_blacksmithing.json",
            "TAILORING": "recipes_tailoring.json"
        }
        
        for profession_key, filename in recipe_files.items():
            file_path = self.data_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        recipes = self._parse_recipes(data, profession_key)
                        
                        # Handle legacy profession mapping
                        if profession_key == "BLACKSMITHING":
                            # Split blacksmithing recipes between weaponsmith and armorsmith
                            weapon_recipes = []
                            armor_recipes = []
                            for recipe in recipes:
                                if any(weapon_word in recipe.name.lower() for weapon_word in 
                                      ['sword', 'dagger', 'axe', 'bow', 'staff', 'pickaxe']):
                                    recipe.profession = Profession.WEAPONSMITH
                                    weapon_recipes.append(recipe)
                                else:
                                    recipe.profession = Profession.ARMORSMITH
                                    armor_recipes.append(recipe)
                            
                            # Add to existing or create new
                            if Profession.WEAPONSMITH in self.recipes_cache:
                                self.recipes_cache[Profession.WEAPONSMITH].extend(weapon_recipes)
                            else:
                                self.recipes_cache[Profession.WEAPONSMITH] = weapon_recipes
                                
                            if Profession.ARMORSMITH in self.recipes_cache:
                                self.recipes_cache[Profession.ARMORSMITH].extend(armor_recipes)
                            else:
                                self.recipes_cache[Profession.ARMORSMITH] = armor_recipes
                                
                        elif profession_key == "TAILORING":
                            # TAILORING is now its own crafting profession
                            for recipe in recipes:
                                recipe.profession = Profession.TAILORING
                            
                            if Profession.TAILORING in self.recipes_cache:
                                self.recipes_cache[Profession.TAILORING].extend(recipes)
                            else:
                                self.recipes_cache[Profession.TAILORING] = recipes
                        else:
                            self.recipes_cache[profession_key] = recipes
                            
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    
    def _parse_recipes(self, data: Dict[str, Any], profession_key) -> List[Recipe]:
        """Parse recipe data from JSON"""
        recipes = []
        
        if "recipes" in data:
            recipe_list = data["recipes"]
        else:
            recipe_list = data
        
        for recipe_data in recipe_list:
            try:
                # Handle different JSON structures
                name = recipe_data.get("recipe_name") or recipe_data.get("name")
                if not name:
                    continue
                
                # Map profession
                if isinstance(profession_key, str):
                    if profession_key == "BLACKSMITHING":
                        profession = Profession.WEAPONSMITH  # Default, will be split later
                    elif profession_key == "TAILORING":
                        profession = Profession.TAILORING
                    else:
                        profession = Profession.WEAPONSMITH  # Default fallback
                else:
                    profession = profession_key
                
                # Get materials
                materials = recipe_data.get("materials", {})
                
                # Get skill level and determine tier
                skill_level = recipe_data.get("skill_level", 1)
                if skill_level <= 10:
                    tier = ProfessionTier.APPRENTICE
                elif skill_level <= 20:
                    tier = ProfessionTier.JOURNEYMAN
                else:
                    tier = ProfessionTier.MASTER
                
                # Map tool type based on profession
                tool_type_map = {
                    Profession.WEAPONSMITH: ToolType.FORGE,
                    Profession.ARMORSMITH: ToolType.ANVIL,
                    Profession.ALCHEMY: ToolType.ALCHEMY_TABLE,
                    Profession.COOKING: ToolType.COOKING_STATION,
                    Profession.WOODWORKING: ToolType.WORKBENCH,
                    Profession.JEWELCRAFTING: ToolType.JEWELING_TABLE,
                    Profession.ENCHANTING: ToolType.ENCHANTING_TABLE,
                    Profession.SHIPBUILDING: ToolType.SHIPYARD,
                    Profession.TAILORING: ToolType.LOOM,
                }
                
                tool_type = tool_type_map.get(profession, ToolType.WORKBENCH)
                tool_level = recipe_data.get("tool_level", 1)
                
                # Create recipe object
                recipe = Recipe(
                    name=name,
                    profession=profession,
                    tier=tier,
                    materials=materials,
                    tool=tool_type,
                    tool_level=tool_level,
                    skill_level=skill_level
                )
                
                recipes.append(recipe)
                
            except Exception as e:
                print(f"Error parsing recipe {recipe_data}: {e}")
                continue
        
        return recipes
    
    def get_recipes_for_profession(self, profession: Profession) -> List[Recipe]:
        """Get all recipes for a specific profession"""
        return self.recipes_cache.get(profession, [])
    
    def get_all_recipes(self) -> Dict[Profession, List[Recipe]]:
        """Get all loaded recipes"""
        return self.recipes_cache
    
    def get_recipe_by_name(self, name: str) -> Recipe:
        """Find a recipe by name across all professions"""
        for recipes in self.recipes_cache.values():
            for recipe in recipes:
                if recipe.name == name:
                    return recipe
        return None
    
    def filter_recipes_by_skill(self, profession: Profession, max_skill: int) -> List[Recipe]:
        """Filter recipes by maximum skill level"""
        recipes = self.get_recipes_for_profession(profession)
        return [recipe for recipe in recipes if recipe.skill_level <= max_skill]
    
    def filter_recipes_by_tool_level(self, profession: Profession, max_tool_level: int) -> List[Recipe]:
        """Filter recipes by maximum tool level"""
        recipes = self.get_recipes_for_profession(profession)
        return [recipe for recipe in recipes if recipe.tool_level <= max_tool_level]
