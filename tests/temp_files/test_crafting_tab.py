from ui.base_tab import BaseTab
from PySide6.QtWidgets import QVBoxLayout, QLabel, QComboBox, QSlider, QHBoxLayout
from PySide6.QtCore import Qt
from data.enums import Profession, Recipe, ToolType, ProfessionTier, ProfessionCategory
from data.player import Player
import logging

logger = logging.getLogger(__name__)

CRAFTING_PROFESSIONS = [
    Profession.ARMORSMITH,
    Profession.WEAPONSMITH,
    Profession.ALCHEMY,
    Profession.COOKING,
    Profession.ENCHANTING,
    Profession.JEWELCRAFTING,
    Profession.TAILORING
]

class Recipe:
    def __init__(self, name, profession, tier, skill_required, tools_required, materials):
        self.name = name
        self.profession = profession
        self.tier = tier
        self.skill_required = skill_required
        self.tools_required = tools_required
        self.materials = materials
        # New metadata fields
        self.description = ""
        self.function = ""
        self.base_price = 0
        self.weight = 0.0
        self.source = ""
        
    def set_metadata(self, description, function, price, weight, source):
        """Set additional recipe metadata"""
        self.description = str(description)
        self.function = str(function)
        self.base_price = max(0, int(price))
        self.weight = max(0.0, float(weight))
        self.source = str(source)

CRAFTING_RECIPES = [
    # Weaponsmithing
    Recipe("Iron Dagger", Profession.WEAPONSMITH, ProfessionTier.APPRENTICE,
          {"Iron Ingot": 1}, ToolType.FORGE, 1, 1).set_metadata("A simple dagger.", "Melee", 10, 0.5, "Vendor"),
    Recipe("Steel Sword", Profession.WEAPONSMITH, ProfessionTier.JOURNEYMAN,
          {"Steel Ingot": 3}, ToolType.FORGE, 3, 10).set_metadata("A sturdy sword.", "Melee", 50, 1.2, "Vendor"),
    Recipe("Iron Sword", Profession.WEAPONSMITH, ProfessionTier.APPRENTICE,
          {"Iron Ingot": 2, "Coal": 1}, ToolType.FORGE, 1, 1).set_metadata("A basic sword.", "Melee", 5, 0.8, "Vendor"),
          
    # Armorsmithing  
    Recipe("Iron Chestplate", Profession.ARMORSMITH, ProfessionTier.APPRENTICE,
          {"Iron Ingot": 5}, ToolType.FORGE, 2, 5).set_metadata("Basic chest armor.", "Armor", 20, 2.5, "Vendor"),
    Recipe("Steel Helm", Profession.ARMORSMITH, ProfessionTier.JOURNEYMAN,
          {"Steel Ingot": 2}, ToolType.FORGE, 3, 12).set_metadata("A sturdy helm.", "Armor", 30, 1.0, "Vendor"),
    Recipe("Steel Armor", Profession.ARMORSMITH, ProfessionTier.JOURNEYMAN,
          {"Steel Ingot": 5, "Leather": 3}, ToolType.FORGE, 3, 10).set_metadata("A set of steel armor.", "Armor", 60, 4.0, "Vendor"),
          
    # Alchemy
    Recipe("Health Potion", Profession.ALCHEMY, ProfessionTier.APPRENTICE,
          {"Herbs": 2, "Water": 1}, ToolType.ALCHEMY_TABLE, 1, 1).set_metadata("Restores health.", "Potion", 5, 0.2, "Vendor"),
    Recipe("Mana Elixir", Profession.ALCHEMY, ProfessionTier.MASTER,
          {"Magic Essence": 3, "Crystal": 1}, ToolType.ALCHEMY_TABLE, 5, 20).set_metadata("Restores mana.", "Potion", 100, 0.5, "Vendor"),
          
    # Cooking
    Recipe("Grilled Meat", Profession.COOKING, ProfessionTier.APPRENTICE,
          {"Raw Meat": 1}, ToolType.COOKING_STATION, 1, 1).set_metadata("A simple meal.", "Food", 2, 0.3, "Vendor"),
    Recipe("Feast Platter", Profession.COOKING, ProfessionTier.JOURNEYMAN,
          {"Vegetables": 3, "Spices": 2}, ToolType.COOKING_STATION, 3, 15).set_metadata("A grand feast.", "Food", 50, 2.0, "Vendor")
]

class CraftingTab(BaseTab):
    def __init__(self):
        super().__init__("Crafting")
        self.player = Player()
        self.player.load()
        self.setup_ui()
        
    def setup_ui(self):
        self.layout = QVBoxLayout()
        
        # Profession selection
        self.profession_select = QComboBox()
        self.profession_select.addItems([
            p.name.replace('_', ' ')
            for p in CRAFTING_PROFESSIONS
        ])
        self.layout.addWidget(self.profession_select)
        
        # Skill level controls
        self.skill_level = QSlider(Qt.Horizontal)
        self.skill_level.setRange(1, 20)
        self.layout.addWidget(self.skill_level)
        
        # Tool level controls
        self.tool_level = QSlider(Qt.Horizontal)
        self.tool_level.setRange(1, 20)
        tool_layout = QHBoxLayout()
        tool_layout.addWidget(QLabel("Tool Level:"))
        tool_layout.addWidget(self.tool_level)
        self.layout.addLayout(tool_layout)
        
        # Recipe display
        self.recipe_display = QLabel("Select a profession to view recipes")
        self.layout.addWidget(self.recipe_display)
        
        self.label = QLabel("Crafting System - Work in Progress")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        # Connect signals
        self.profession_select.currentTextChanged.connect(self.update_recipes)
        self.skill_level.valueChanged.connect(self.on_skill_change)
        self.tool_level.valueChanged.connect(self.on_tool_change)

    def on_skill_change(self, value):
        profession = Profession[self.profession_select.currentText().replace(' ', '_')]
        self.player.skills[profession] = value
        self.player.save()

    def on_tool_change(self, value):
        # Map profession to tool type
        tool = ToolType.FORGE  # Simplified for demo
        self.player.tools[tool] = value
        self.player.save()

    def can_craft(self, recipe: Recipe) -> bool:
        skill_req = self.player.skills[recipe.profession] >= recipe.tier.value
        tool_req = self.player.tools[recipe.tools_required] >= recipe.skill_required
        return skill_req and tool_req

    def craft_item(self, recipe: Recipe):
        try:
            if not self.can_craft(recipe):
                missing = []
                if self.player.skills[recipe.profession] < recipe.tier.value:
                    missing.append(f"skill level {recipe.tier.value}")
                if self.player.tools[recipe.tools_required] < recipe.skill_required:
                    missing.append(f"tool level {recipe.skill_required}")
                raise ValueError(f"Cannot craft - missing requirements: {', '.join(missing)}")
            
            # Crafting logic here
            logger.info(f"Crafted: {recipe.name}")
            self.player.save()
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return False
        return True

    def update_recipes(self, profession_text):
        profession = Profession[profession_text.replace(' ', '_')]
        recipes = [r for r in CRAFTING_RECIPES if r.profession == profession]
        recipe_text = "\n".join(
            f"{r.name} (Req: Tool Lv{r.skill_required}, Skill Lv{r.tier.value}) - {r.description}"
            for r in recipes
        )
        self.recipe_display.setText(recipe_text)
