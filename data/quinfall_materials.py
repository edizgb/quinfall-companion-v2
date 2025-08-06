#!/usr/bin/env python3
"""
Quinfall Materials Database
Complete list of all materials, items, and resources in Quinfall game.
Prepared for future API integration with real player data.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional

class MaterialCategory(Enum):
    """Categories of materials in Quinfall"""
    # Raw Materials
    ORES = "ores"
    GEMS = "gems"
    HERBS = "herbs"
    WOOD = "wood"
    STONE = "stone"
    CLOTH = "cloth"
    LEATHER = "leather"
    FOOD_INGREDIENTS = "food_ingredients"
    
    # Processed Materials
    INGOTS = "ingots"
    REFINED_GEMS = "refined_gems"
    PROCESSED_HERBS = "processed_herbs"
    LUMBER = "lumber"
    REFINED_STONE = "refined_stone"
    FABRIC = "fabric"
    PROCESSED_LEATHER = "processed_leather"
    
    # Crafted Items
    WEAPONS = "weapons"
    ARMOR = "armor"
    TOOLS = "tools"
    CONSUMABLES = "consumables"
    ACCESSORIES = "accessories"
    
    # Special Items
    QUEST_ITEMS = "quest_items"
    RARE_MATERIALS = "rare_materials"
    MAGICAL_COMPONENTS = "magical_components"

class MaterialRarity(Enum):
    """Material rarity levels in Quinfall"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

@dataclass
class QuinfallMaterial:
    """Represents a material/item in Quinfall"""
    id: str
    name: str
    category: MaterialCategory
    rarity: MaterialRarity
    stackable: bool = True
    max_stack: int = 1000
    weight: float = 0.1
    base_value: int = 1
    description: str = ""
    
    # API Integration fields (for future use)
    api_id: Optional[str] = None
    game_internal_id: Optional[int] = None

# Complete Quinfall Materials Database
QUINFALL_MATERIALS = {
    # === RAW ORES ===
    "copper_ore": QuinfallMaterial("copper_ore", "Copper Ore", MaterialCategory.ORES, MaterialRarity.COMMON, True, 1000, 0.5, 2),
    "tin_ore": QuinfallMaterial("tin_ore", "Tin Ore", MaterialCategory.ORES, MaterialRarity.COMMON, True, 1000, 0.5, 3),
    "iron_ore": QuinfallMaterial("iron_ore", "Iron Ore", MaterialCategory.ORES, MaterialRarity.COMMON, True, 1000, 0.8, 5),
    "silver_ore": QuinfallMaterial("silver_ore", "Silver Ore", MaterialCategory.ORES, MaterialRarity.UNCOMMON, True, 1000, 0.6, 12),
    "gold_ore": QuinfallMaterial("gold_ore", "Gold Ore", MaterialCategory.ORES, MaterialRarity.RARE, True, 1000, 0.7, 25),
    "mithril_ore": QuinfallMaterial("mithril_ore", "Mithril Ore", MaterialCategory.ORES, MaterialRarity.EPIC, True, 1000, 0.4, 100),
    "adamantium_ore": QuinfallMaterial("adamantium_ore", "Adamantium Ore", MaterialCategory.ORES, MaterialRarity.LEGENDARY, True, 1000, 1.0, 500),
    
    # === PROCESSED INGOTS ===
    "copper_ingot": QuinfallMaterial("copper_ingot", "Copper Ingot", MaterialCategory.INGOTS, MaterialRarity.COMMON, True, 1000, 0.3, 8),
    "bronze_ingot": QuinfallMaterial("bronze_ingot", "Bronze Ingot", MaterialCategory.INGOTS, MaterialRarity.COMMON, True, 1000, 0.4, 15),
    "iron_ingot": QuinfallMaterial("iron_ingot", "Iron Ingot", MaterialCategory.INGOTS, MaterialRarity.COMMON, True, 1000, 0.5, 20),
    "steel_ingot": QuinfallMaterial("steel_ingot", "Steel Ingot", MaterialCategory.INGOTS, MaterialRarity.UNCOMMON, True, 1000, 0.6, 35),
    "silver_ingot": QuinfallMaterial("silver_ingot", "Silver Ingot", MaterialCategory.INGOTS, MaterialRarity.UNCOMMON, True, 1000, 0.4, 50),
    "gold_ingot": QuinfallMaterial("gold_ingot", "Gold Ingot", MaterialCategory.INGOTS, MaterialRarity.RARE, True, 1000, 0.5, 100),
    "mithril_ingot": QuinfallMaterial("mithril_ingot", "Mithril Ingot", MaterialCategory.INGOTS, MaterialRarity.EPIC, True, 1000, 0.2, 400),
    "adamantium_ingot": QuinfallMaterial("adamantium_ingot", "Adamantium Ingot", MaterialCategory.INGOTS, MaterialRarity.LEGENDARY, True, 1000, 0.8, 2000),
    
    # === GEMS ===
    "rough_ruby": QuinfallMaterial("rough_ruby", "Rough Ruby", MaterialCategory.GEMS, MaterialRarity.UNCOMMON, True, 1000, 0.1, 30),
    "rough_sapphire": QuinfallMaterial("rough_sapphire", "Rough Sapphire", MaterialCategory.GEMS, MaterialRarity.UNCOMMON, True, 1000, 0.1, 32),
    "rough_emerald": QuinfallMaterial("rough_emerald", "Rough Emerald", MaterialCategory.GEMS, MaterialRarity.RARE, True, 1000, 0.1, 45),
    "rough_diamond": QuinfallMaterial("rough_diamond", "Rough Diamond", MaterialCategory.GEMS, MaterialRarity.EPIC, True, 1000, 0.1, 150),
    "cut_ruby": QuinfallMaterial("cut_ruby", "Cut Ruby", MaterialCategory.REFINED_GEMS, MaterialRarity.RARE, True, 1000, 0.05, 120),
    "cut_sapphire": QuinfallMaterial("cut_sapphire", "Cut Sapphire", MaterialCategory.REFINED_GEMS, MaterialRarity.RARE, True, 1000, 0.05, 125),
    "cut_emerald": QuinfallMaterial("cut_emerald", "Cut Emerald", MaterialCategory.REFINED_GEMS, MaterialRarity.EPIC, True, 1000, 0.05, 180),
    "cut_diamond": QuinfallMaterial("cut_diamond", "Cut Diamond", MaterialCategory.REFINED_GEMS, MaterialRarity.LEGENDARY, True, 1000, 0.05, 600),
    
    # === HERBS & ALCHEMY ===
    "red_herb": QuinfallMaterial("red_herb", "Red Herb", MaterialCategory.HERBS, MaterialRarity.COMMON, True, 1000, 0.1, 3),
    "blue_herb": QuinfallMaterial("blue_herb", "Blue Herb", MaterialCategory.HERBS, MaterialRarity.COMMON, True, 1000, 0.1, 4),
    "white_herb": QuinfallMaterial("white_herb", "White Herb", MaterialCategory.HERBS, MaterialRarity.COMMON, True, 1000, 0.1, 5),
    "golden_herb": QuinfallMaterial("golden_herb", "Golden Herb", MaterialCategory.HERBS, MaterialRarity.UNCOMMON, True, 1000, 0.1, 15),
    "moonstone_powder": QuinfallMaterial("moonstone_powder", "Moonstone Powder", MaterialCategory.MAGICAL_COMPONENTS, MaterialRarity.RARE, True, 1000, 0.05, 50),
    "pure_essence": QuinfallMaterial("pure_essence", "Pure Essence", MaterialCategory.MAGICAL_COMPONENTS, MaterialRarity.UNCOMMON, True, 1000, 0.02, 25),
    
    # === WOOD & LUMBER ===
    "oak_log": QuinfallMaterial("oak_log", "Oak Log", MaterialCategory.WOOD, MaterialRarity.COMMON, True, 1000, 2.0, 5),
    "pine_log": QuinfallMaterial("pine_log", "Pine Log", MaterialCategory.WOOD, MaterialRarity.COMMON, True, 1000, 1.8, 4),
    "birch_log": QuinfallMaterial("birch_log", "Birch Log", MaterialCategory.WOOD, MaterialRarity.COMMON, True, 1000, 1.5, 6),
    "maple_log": QuinfallMaterial("maple_log", "Maple Log", MaterialCategory.WOOD, MaterialRarity.UNCOMMON, True, 1000, 2.2, 12),
    "ebony_log": QuinfallMaterial("ebony_log", "Ebony Log", MaterialCategory.WOOD, MaterialRarity.RARE, True, 1000, 2.5, 35),
    "ironwood_log": QuinfallMaterial("ironwood_log", "Ironwood Log", MaterialCategory.WOOD, MaterialRarity.EPIC, True, 1000, 3.0, 80),
    
    "oak_plank": QuinfallMaterial("oak_plank", "Oak Plank", MaterialCategory.LUMBER, MaterialRarity.COMMON, True, 1000, 1.0, 15),
    "pine_plank": QuinfallMaterial("pine_plank", "Pine Plank", MaterialCategory.LUMBER, MaterialRarity.COMMON, True, 1000, 0.9, 12),
    "birch_plank": QuinfallMaterial("birch_plank", "Birch Plank", MaterialCategory.LUMBER, MaterialRarity.COMMON, True, 1000, 0.8, 18),
    "maple_plank": QuinfallMaterial("maple_plank", "Maple Plank", MaterialCategory.LUMBER, MaterialRarity.UNCOMMON, True, 1000, 1.1, 35),
    "ebony_plank": QuinfallMaterial("ebony_plank", "Ebony Plank", MaterialCategory.LUMBER, MaterialRarity.RARE, True, 1000, 1.3, 100),
    "ironwood_plank": QuinfallMaterial("ironwood_plank", "Ironwood Plank", MaterialCategory.LUMBER, MaterialRarity.EPIC, True, 1000, 1.5, 240),
    
    # === CLOTH & FABRIC ===
    "cotton": QuinfallMaterial("cotton", "Cotton", MaterialCategory.CLOTH, MaterialRarity.COMMON, True, 1000, 0.1, 2),
    "wool": QuinfallMaterial("wool", "Wool", MaterialCategory.CLOTH, MaterialRarity.COMMON, True, 1000, 0.2, 4),
    "silk": QuinfallMaterial("silk", "Silk", MaterialCategory.CLOTH, MaterialRarity.UNCOMMON, True, 1000, 0.1, 12),
    "linen_cloth": QuinfallMaterial("linen_cloth", "Linen Cloth", MaterialCategory.FABRIC, MaterialRarity.COMMON, True, 1000, 0.3, 8),
    "wool_cloth": QuinfallMaterial("wool_cloth", "Wool Cloth", MaterialCategory.FABRIC, MaterialRarity.COMMON, True, 1000, 0.4, 15),
    "silk_cloth": QuinfallMaterial("silk_cloth", "Silk Cloth", MaterialCategory.FABRIC, MaterialRarity.UNCOMMON, True, 1000, 0.2, 45),
    
    # === LEATHER ===
    "raw_leather": QuinfallMaterial("raw_leather", "Raw Leather", MaterialCategory.LEATHER, MaterialRarity.COMMON, True, 1000, 0.5, 6),
    "cured_leather": QuinfallMaterial("cured_leather", "Cured Leather", MaterialCategory.PROCESSED_LEATHER, MaterialRarity.COMMON, True, 1000, 0.4, 20),
    "hardened_leather": QuinfallMaterial("hardened_leather", "Hardened Leather", MaterialCategory.PROCESSED_LEATHER, MaterialRarity.UNCOMMON, True, 1000, 0.6, 45),
    "dragonhide": QuinfallMaterial("dragonhide", "Dragonhide", MaterialCategory.PROCESSED_LEATHER, MaterialRarity.LEGENDARY, True, 1000, 1.0, 500),
    
    # === FOOD INGREDIENTS ===
    "wheat": QuinfallMaterial("wheat", "Wheat", MaterialCategory.FOOD_INGREDIENTS, MaterialRarity.COMMON, True, 1000, 0.1, 1),
    "flour": QuinfallMaterial("flour", "Flour", MaterialCategory.FOOD_INGREDIENTS, MaterialRarity.COMMON, True, 1000, 0.1, 3),
    "meat": QuinfallMaterial("meat", "Meat", MaterialCategory.FOOD_INGREDIENTS, MaterialRarity.COMMON, True, 1000, 0.8, 8),
    "fish": QuinfallMaterial("fish", "Fish", MaterialCategory.FOOD_INGREDIENTS, MaterialRarity.COMMON, True, 1000, 0.5, 5),
    "vegetables": QuinfallMaterial("vegetables", "Vegetables", MaterialCategory.FOOD_INGREDIENTS, MaterialRarity.COMMON, True, 1000, 0.3, 2),
    "salt": QuinfallMaterial("salt", "Salt", MaterialCategory.FOOD_INGREDIENTS, MaterialRarity.COMMON, True, 1000, 0.1, 2),
    "spices": QuinfallMaterial("spices", "Spices", MaterialCategory.FOOD_INGREDIENTS, MaterialRarity.UNCOMMON, True, 1000, 0.05, 10),
    
    # === CRAFTING COMPONENTS ===
    "water": QuinfallMaterial("water", "Water", MaterialCategory.FOOD_INGREDIENTS, MaterialRarity.COMMON, True, 1000, 1.0, 1),
    "distilled_water": QuinfallMaterial("distilled_water", "Distilled Water", MaterialCategory.PROCESSED_HERBS, MaterialRarity.COMMON, True, 1000, 1.0, 5),
    "glass_vial": QuinfallMaterial("glass_vial", "Glass Vial", MaterialCategory.TOOLS, MaterialRarity.COMMON, True, 1000, 0.1, 8),
    "crystal_vial": QuinfallMaterial("crystal_vial", "Crystal Vial", MaterialCategory.TOOLS, MaterialRarity.UNCOMMON, True, 1000, 0.1, 25),
    "enchanted_vial": QuinfallMaterial("enchanted_vial", "Enchanted Vial", MaterialCategory.TOOLS, MaterialRarity.RARE, True, 1000, 0.1, 75),
    
    # === STONE & MINERALS ===
    "stone": QuinfallMaterial("stone", "Stone", MaterialCategory.STONE, MaterialRarity.COMMON, True, 1000, 3.0, 1),
    "granite": QuinfallMaterial("granite", "Granite", MaterialCategory.STONE, MaterialRarity.COMMON, True, 1000, 3.5, 3),
    "marble": QuinfallMaterial("marble", "Marble", MaterialCategory.STONE, MaterialRarity.UNCOMMON, True, 1000, 4.0, 8),
    "obsidian": QuinfallMaterial("obsidian", "Obsidian", MaterialCategory.STONE, MaterialRarity.RARE, True, 1000, 2.8, 25),
    
    # === MAGICAL COMPONENTS ===
    "mana_crystal": QuinfallMaterial("mana_crystal", "Mana Crystal", MaterialCategory.MAGICAL_COMPONENTS, MaterialRarity.UNCOMMON, True, 1000, 0.2, 40),
    "soul_gem": QuinfallMaterial("soul_gem", "Soul Gem", MaterialCategory.MAGICAL_COMPONENTS, MaterialRarity.RARE, True, 1000, 0.1, 120),
    "arcane_dust": QuinfallMaterial("arcane_dust", "Arcane Dust", MaterialCategory.MAGICAL_COMPONENTS, MaterialRarity.COMMON, True, 1000, 0.01, 15),
    "void_essence": QuinfallMaterial("void_essence", "Void Essence", MaterialCategory.MAGICAL_COMPONENTS, MaterialRarity.LEGENDARY, True, 1000, 0.01, 1000),
}

def get_material(material_id: str) -> Optional[QuinfallMaterial]:
    """Get material by ID"""
    return QUINFALL_MATERIALS.get(material_id)

def get_materials_by_category(category: MaterialCategory) -> List[QuinfallMaterial]:
    """Get all materials in a specific category"""
    return [mat for mat in QUINFALL_MATERIALS.values() if mat.category == category]

def get_materials_by_rarity(rarity: MaterialRarity) -> List[QuinfallMaterial]:
    """Get all materials of a specific rarity"""
    return [mat for mat in QUINFALL_MATERIALS.values() if mat.rarity == rarity]

def get_all_material_names() -> List[str]:
    """Get list of all material names (for recipe validation)"""
    return list(QUINFALL_MATERIALS.keys())

def is_valid_material(material_name: str) -> bool:
    """Check if material name exists in database"""
    return material_name in QUINFALL_MATERIALS

# API Integration helpers (for future use)
def get_material_by_api_id(api_id: str) -> Optional[QuinfallMaterial]:
    """Get material by API ID (for future API integration)"""
    for mat in QUINFALL_MATERIALS.values():
        if mat.api_id == api_id:
            return mat
    return None

def get_material_by_game_id(game_id: int) -> Optional[QuinfallMaterial]:
    """Get material by game internal ID (for future API integration)"""
    for mat in QUINFALL_MATERIALS.values():
        if mat.game_internal_id == game_id:
            return mat
    return None
