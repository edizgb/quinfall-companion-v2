#!/usr/bin/env python3
"""
Improved Crafting Tab with better UI/UX
Fixes:
- Proper scrolling (only recipe list scrolls, not entire window)
- Pagination options (5/10/25/50 recipes per page)
- Clear crafting action button
- Better layout organization
"""

from ui.base_tab import BaseTab
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                     QComboBox, QSlider, QPushButton, QTextEdit, 
                                     QSpinBox, QGroupBox, QScrollArea, QFrame,
                                     QToolTip, QSizePolicy, QButtonGroup, QRadioButton,
                                     QGridLayout, QSplitter)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon
from data.enums import Profession, ToolType, Recipe, ProfessionTier
from data.player import Player
from utils.recipe_loader import RecipeLoader
import json
from pathlib import Path

# Load recipes from all profession JSON files
def load_recipes():
    """Load all recipes from JSON files"""
    all_recipes = []
    
    recipe_files = {
        'blacksmithing': 'data/recipes_blacksmithing.json',
        'cooking': 'data/recipes_cooking.json',
        'woodworking': 'data/recipes_woodworking.json',
        'tailoring': 'data/recipes_tailoring.json',
        'alchemy': 'data/recipes_alchemy.json',
        'weaponsmith': 'data/recipes_weaponsmith.json',
        'armorsmith': 'data/recipes_armorsmith.json',
        'shipbuilding': 'data/recipes_shipbuilding.json'
    }
    
    for profession_name, file_path in recipe_files.items():
        try:
            full_path = Path(__file__).parent.parent / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    recipes = data.get('recipes', [])
                    print(f"Debug: Loading {len(recipes)} {profession_name} recipes from JSON")
                    
                    for i, recipe_data in enumerate(recipes, 1):
                        try:
                            # Map profession string to enum
                            prof_map = {
                                'blacksmithing': Profession.WEAPONSMITH,  # Map blacksmithing to weaponsmith
                                'weaponsmith': Profession.WEAPONSMITH,
                                'armorsmith': Profession.ARMORSMITH,
                                'alchemy': Profession.ALCHEMY,
                                'cooking': Profession.COOKING,
                                'woodworking': Profession.WOODWORKING,
                                'shipbuilding': Profession.SHIPBUILDING
                            }
                            
                            # Map profession to appropriate tool
                            tool_map = {
                                'blacksmithing': ToolType.FORGE,  # Blacksmithing recipes use forge
                                'weaponsmith': ToolType.FORGE,
                                'armorsmith': ToolType.ANVIL,
                                'alchemy': ToolType.ALCHEMY_TABLE,
                                'cooking': ToolType.COOKING_STATION,
                                'woodworking': ToolType.WORKBENCH,
                                'shipbuilding': ToolType.DOCK
                            }
                            
                            # Determine tier based on skill level
                            skill = recipe_data.get('skill_level', 1)
                            if skill <= 25:
                                tier = ProfessionTier.APPRENTICE
                            elif skill <= 50:
                                tier = ProfessionTier.JOURNEYMAN
                            elif skill <= 75:
                                tier = ProfessionTier.EXPERT
                            else:
                                tier = ProfessionTier.MASTER
                            
                            recipe = Recipe(
                                name=recipe_data['recipe_name'],  # Use 'recipe_name' from JSON
                                profession=prof_map.get(profession_name, Profession.WEAPONSMITH),
                                tier=tier,
                                materials=recipe_data.get('materials', {}),
                                tool=tool_map.get(profession_name, ToolType.FORGE),  # Map profession to tool
                                tool_level=recipe_data.get('tool_level', 1),
                                skill_level=skill
                            )
                            all_recipes.append(recipe)
                            print(f"Debug: Loaded {profession_name} recipe {i}: {recipe.name} (Skill: {recipe.skill_level})")
                        except Exception as e:
                            print(f"Error loading recipe {i} from {profession_name}: {e}")
                    
                    print(f"Debug: Successfully loaded {len(recipes)} {profession_name} recipes")
            else:
                print(f"Warning: Recipe file not found: {file_path}")
        except Exception as e:
            print(f"Error loading {profession_name} recipes: {e}")
    
    print(f"Debug: Total recipes loaded: {len(all_recipes)}")
    return all_recipes

CRAFTING_RECIPES = load_recipes()

class ImprovedCraftingTab(BaseTab):
    """Improved Crafting Tab with better UI/UX"""
    
    def __init__(self):
        super().__init__("Crafting")
        self.current_tool_type = "Basic"
        self.current_page = 1
        self.recipes_per_page = 10  # Default
        self.selected_recipe = None
        self.recipe_buttons = []
        self.player = Player()
        self.player.load()
        self.recipe_loader = RecipeLoader()
        self.recipes = []
        
        # Store skill levels per profession to avoid resetting
        self.profession_skills = {}
        
        self.load_preferences()
        self.setup_improved_ui()
        
        # Load initial profession skill
        self.load_profession_skill()
    
    def load_profession_skill(self):
        """Load saved skill level for current profession"""
        try:
            current_index = self.profession_combo.currentIndex()
            if current_index >= 0:
                profession = self.profession_combo.itemData(current_index)
                if profession in self.profession_skills:
                    # Block signals to prevent infinite loop
                    self.skill_level.blockSignals(True)
                    self.skill_level.setValue(self.profession_skills[profession])
                    self.skill_level.blockSignals(False)
                    self.skill_level_label.setText(str(self.profession_skills[profession]))
                    print(f"Debug: Loaded skill {self.profession_skills[profession]} for {profession}")
        except Exception as e:
            print(f"Error loading profession skill: {e}")
    
    def save_profession_skill(self):
        """Save current skill level for current profession"""
        try:
            current_index = self.profession_combo.currentIndex()
            if current_index >= 0:
                profession = self.profession_combo.itemData(current_index)
                skill_value = self.skill_level.value()
                self.profession_skills[profession] = skill_value
                print(f"Debug: Saved skill {skill_value} for {profession}")
                self.save_preferences()
        except Exception as e:
            print(f"Error saving profession skill: {e}")
    
    def get_current_profession(self):
        """Get currently selected profession"""
        current_index = self.profession_combo.currentIndex()
        if current_index >= 0:
            return self.profession_combo.itemData(current_index)
        return Profession.ALCHEMY
    
    def on_recipes_per_page_change(self, value):
        """Handle recipes per page selection change"""
        self.recipes_per_page = int(value)
        self.current_page = 1  # Reset to first page
        self.update_recipe_display()
        self.save_preferences()
    
    def on_profession_change(self):
        """Handle profession selection change"""
        self.current_page = 1
        self.update_recipes()
        self.update_recipe_display()
        self.update_inventory_display()
        self.load_profession_skill()
    
    def on_skill_change(self, value):
        """Handle skill level change"""
        self.skill_level_label.setText(str(value))
        self.update_recipe_display()
        self.save_profession_skill()
    
    def on_tool_change(self, value):
        """Handle tool tier change"""
        # Convert tool tier name to numeric value for filtering
        tier_map = {"Basic": 1, "Improved": 2, "Advanced": 3}
        tool_tier_value = tier_map.get(value, 1)
        
        print(f"Debug: Tool tier changed to: {value} (value: {tool_tier_value})")
        self.current_tool_type = value
        self.update_recipe_display()
        self.save_preferences()
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_recipe_display()
    
    def next_page(self):
        """Go to next page"""
        self.current_page += 1
        self.update_recipe_display()
    
    def update_recipes(self):
        """Update recipes based on current profession selection"""
        try:
            # Get the profession object directly from combo box data
            current_index = self.profession_combo.currentIndex()
            if current_index >= 0:
                profession = self.profession_combo.itemData(current_index)
            else:
                profession = Profession.WEAPONSMITH
        except (KeyError, AttributeError):
            profession = Profession.WEAPONSMITH
        
        # Load recipes for the selected profession
        self.recipes = self.recipe_loader.get_recipes_for_profession(profession)
        self.current_page = 1
        self.update_recipe_display()
    
    def update_recipe_display(self):
        """Update displayed recipes based on filters with pagination"""
        # Clear existing buttons
        for button in self.recipe_buttons:
            button.deleteLater()
        self.recipe_buttons.clear()
        
        # Get current profession
        try:
            # Get the profession object directly from combo box data
            current_index = self.profession_combo.currentIndex()
            if current_index >= 0:
                profession = self.profession_combo.itemData(current_index)
            else:
                profession = Profession.WEAPONSMITH
        except (KeyError, AttributeError):
            profession = Profession.WEAPONSMITH
        
        skill_level = self.skill_level.value()
        
        print(f"Debug: Profession={profession}, Skill={skill_level}, Recipes per page={self.recipes_per_page}")
        
        # Filter recipes
        filtered_recipes = []
        
        # Get current tool tier
        current_tool_tier = self.tool_level_combo.currentText()
        tier_map = {"Basic": 1, "Improved": 2, "Advanced": 3}
        max_tool_level = tier_map.get(current_tool_tier, 3)  # Default to Advanced
        
        for recipe in self.recipes:  # Use self.recipes instead of CRAFTING_RECIPES
            if (recipe.profession == profession and 
                recipe.skill_level <= skill_level and
                recipe.tool_level <= max_tool_level):
                filtered_recipes.append(recipe)
        
        print(f"Debug: Found {len(filtered_recipes)} recipes for {profession}")
        
        # Pagination
        total_pages = max(1, (len(filtered_recipes) + self.recipes_per_page - 1) // self.recipes_per_page)
        self.current_page = min(self.current_page, total_pages)
        
        start_idx = (self.current_page - 1) * self.recipes_per_page
        end_idx = start_idx + self.recipes_per_page
        page_recipes = filtered_recipes[start_idx:end_idx]
        
        print(f"Debug: Displaying {len(page_recipes)} recipe buttons on page {self.current_page}")
        
        # Update page controls
        self.page_label.setText(f"Page {self.current_page} of {total_pages}")
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < total_pages)
        
        # Create recipe buttons
        for recipe in page_recipes:
            button = self.create_recipe_button(recipe, skill_level)
            self.recipe_layout.insertWidget(self.recipe_layout.count() - 1, button)
            self.recipe_buttons.append(button)
        
        # Update material status
        self.update_material_status()
    
    def create_recipe_button(self, recipe, skill_level):
        """Create a clickable button for a recipe with all the formatting"""
        button = QPushButton()
        button.setCheckable(True)
        button.clicked.connect(lambda: self.select_recipe(recipe))
        
        # Determine difficulty color
        difficulty_colors = {
            "Easy": "#38a169",      # Green
            "Medium": "#d69e2e",    # Yellow
            "Hard": "#dd6b20",      # Orange
            "Expert": "#e53e3e"     # Red
        }
        
        if recipe.skill_level <= skill_level * 0.5:
            difficulty = "Easy"
        elif recipe.skill_level <= skill_level * 0.75:
            difficulty = "Medium"
        elif recipe.skill_level <= skill_level:
            difficulty = "Hard"
        else:
            difficulty = "Expert"
        
        color = difficulty_colors[difficulty]
        
        # Format materials
        materials_text = []
        for material, quantity in recipe.materials.items():
            available = self.player.get_item_count(material, "both")
            status = "✅" if available >= quantity else "❌"
            materials_text.append(f"{status} {material}: {available}/{quantity}")
        
        # Button text
        button_text = f"""
🔨 {recipe.name}
📊 Skill: {recipe.skill_level} ({difficulty})
📦 Materials: {', '.join(materials_text)}
        """.strip()
        
        button.setText(button_text)
        button.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 10px;
                border: 2px solid {color};
                border-radius: 5px;
                background-color: #2d3748;
                color: #e2e8f0;
                font-size: 11px;
                min-height: 60px;
            }}
            QPushButton:hover {{
                background-color: #4a5568;
            }}
            QPushButton:checked {{
                background-color: #3182ce;
                border-color: #63b3ed;
            }}
        """)
        
        return button
    
    def select_recipe(self, recipe):
        """Handle recipe selection"""
        # Uncheck other buttons
        for button in self.recipe_buttons:
            if button != self.sender():
                button.setChecked(False)
        
        self.selected_recipe = recipe
        self.craft_button.setEnabled(True)
        self.update_material_status()
        print(f"Selected recipe: {recipe.name}")
    
    def update_material_status(self):
        """Update material status display (for compatibility)"""
        # This method is called by other parts of the code
        # We now show this information in the inventory display instead
        self.update_inventory_display()
    
    def craft_selected_recipe(self):
        """Craft the currently selected recipe"""
        if not self.selected_recipe:
            print("No recipe selected for crafting")
            return
        
        recipe = self.selected_recipe
        quantity = self.craft_quantity_input.value()
        
        # Store materials before crafting for comparison
        materials_before = {}
        for material, needed in recipe.materials.items():
            materials_before[material] = self.player.storage_system.get_item_count(material)
        
        success, message = self.player.craft_item(recipe, quantity)
        
        if success:
            # Show detailed crafting results
            materials_consumed = {}
            for material, needed in recipe.materials.items():
                before = materials_before[material]
                after = self.player.storage_system.get_item_count(material)
                consumed = before - after
                if consumed > 0:
                    materials_consumed[material] = consumed
            
            # Create detailed feedback message
            feedback_lines = [
                f"✅ Successfully crafted {quantity}x {recipe.name}!",
                "",
                "📦 Materials Consumed:"
            ]
            
            for material, consumed in materials_consumed.items():
                current = self.player.storage_system.get_item_count(material)
                feedback_lines.append(f"  • {material}: -{consumed} (remaining: {current})")
            
            feedback_lines.extend([
                "",
                f"🎯 Items Added to Storage: {quantity}x {recipe.name}",
                f"⚡ Experience Gained: {recipe.skill_level * quantity} XP"
            ])
            
            detailed_message = "\n".join(feedback_lines)
            print(detailed_message)
            
            # Update displays
            self.update_material_status()
            self.update_recipe_display()
            self.update_inventory_display()
            self.update_crafting_history(detailed_message)
        else:
            print(f"❌ {message}")
    
    def reset_inventory(self, value=0):
        """Reset inventory to specified value"""
        try:
            self.player.reset_inventory(value)
            self.player.save()
            self.update_material_status()
            self.update_inventory_display()
            print(f"✅ Inventory reset to {value} for all materials")
        except Exception as e:
            print(f"❌ Error resetting inventory: {e}")
    
    def reset_storage_1k(self):
        """Reset storage to 1000 for all materials"""
        try:
            self.player.reset_storage(1000)
            self.player.save()
            self.update_material_status()
            self.update_inventory_display()
            print(f"✅ Storage reset to 1000 for all materials")
        except Exception as e:
            print(f"❌ Error resetting storage: {e}")
    
    def reset_storage_10k(self):
        """Reset storage to 10000 for all materials"""
        try:
            self.player.reset_storage(10000)
            self.player.save()
            self.update_material_status()
            self.update_inventory_display()
            print(f"✅ Storage reset to 10000 for all materials")
        except Exception as e:
            print(f"❌ Error resetting storage: {e}")
    
    def load_preferences(self):
        """Load user preferences"""
        try:
            prefs_file = Path(__file__).parent.parent / 'saves' / 'ui_preferences.json'
            if prefs_file.exists():
                with open(prefs_file, 'r') as f:
                    prefs = json.load(f)
                    self.recipes_per_page = prefs.get('recipes_per_page', 10)
                    
                    # Load profession skills if they exist
                    profession_skills = prefs.get('profession_skills', {})
                    for prof_name, skill_level in profession_skills.items():
                        try:
                            # Convert profession name to enum
                            profession = Profession[prof_name]
                            self.profession_skills[profession] = skill_level
                        except KeyError:
                            print(f"Warning: Unknown profession '{prof_name}' in preferences, skipping")
                            
                    # Load current tool type if it exists
                    current_tool_type = prefs.get('current_tool_type', 'Basic')
                    self.current_tool_type = current_tool_type
                    
                    # Set the tool level combo box to the saved value
                    tool_index = self.tool_level_combo.findText(current_tool_type)
                    if tool_index >= 0:
                        self.tool_level_combo.setCurrentIndex(tool_index)
            else:
                self.recipes_per_page = 10
        except Exception as e:
            print(f"Error loading preferences: {e}")
            self.recipes_per_page = 10
    
    def save_preferences(self):
        """Save user preferences to disk"""
        try:
            # Create saves directory if it doesn't exist
            prefs_file = Path(__file__).parent.parent / 'saves' / 'ui_preferences.json'
            prefs_file.parent.mkdir(exist_ok=True)
            
            # Convert profession skills to JSON-serializable format
            profession_skills_serializable = {}
            for profession, skill_level in self.profession_skills.items():
                profession_skills_serializable[profession.name] = skill_level
            
            # Save preferences
            prefs = {
                'recipes_per_page': self.recipes_per_page,
                'profession_skills': profession_skills_serializable,
                'current_tool_type': self.current_tool_type
            }
            
            with open(prefs_file, 'w') as f:
                json.dump(prefs, f, indent=2)
                
            print("Debug: UI preferences saved successfully")
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def update_inventory_display(self):
        """Update the inventory display"""
        try:
            inventory_text = "🎒 Crafted Items:\n"
            
            # Get all items that are likely crafted items (not raw materials)
            crafted_items = {}
            storage_system = self.player.storage_system
            
            # Common crafted items to display
            common_crafted = [
                "Bread", "Meat Stew", "Health Potion",
                "Iron Sword", "Iron Dagger", "Steel Longsword",
                "Wooden Bow", "Wooden Shield", "Elven Staff",
                "Linen Shirt", "Wool Cloak", "Silk Robe",
                "Minor Health Potion", "Mana Potion", "Greater Healing Elixir",
                "Small Fishing Boat", "Merchant Vessel", "War Galley"
            ]
            
            for item in common_crafted:
                count = storage_system.get_item_count(item)
                if count > 0:
                    crafted_items[item] = count
            
            if crafted_items:
                for item, count in crafted_items.items():
                    inventory_text += f"  • {item}: {count}\n"
            else:
                inventory_text += "  No crafted items yet\n"
            
            inventory_text += "\n📦 Raw Materials:\n"
            
            # Common raw materials
            raw_materials = [
                "wheat", "water", "iron", "wood", "leather", "cloth",
                "stone", "herbs", "meat", "fish", "coal", "oil"
            ]
            
            for material in raw_materials:
                count = storage_system.get_item_count(material)
                if count > 0:
                    inventory_text += f"  • {material}: {count}\n"
            
            self.inventory_display.setText(inventory_text)
            
        except Exception as e:
            self.inventory_display.setText(f"Error loading inventory: {e}")
    
    def update_crafting_history(self, message):
        """Update the crafting history display"""
        current_text = self.crafting_history.toPlainText()
        self.crafting_history.setText(f"{message}\n\n{current_text}")
    
    def clear_crafting_history(self):
        """Clear the crafting history display"""
        self.crafting_history.clear()

    def setup_improved_ui(self):
        """Setup improved UI with better layout and functionality"""
        # Create main layout
        main_layout = QHBoxLayout(self)
        
        # Left side - controls and recipe list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Right side - inventory and crafting history
        right_widget = QWidget()
        right_widget.setFixedWidth(300)
        right_layout = QVBoxLayout(right_widget)
        
        # Inventory Display
        inventory_group = QGroupBox("📦 Current Inventory")
        inventory_layout = QVBoxLayout(inventory_group)
        
        self.inventory_display = QTextEdit()
        self.inventory_display.setMaximumHeight(150)
        self.inventory_display.setReadOnly(True)
        inventory_layout.addWidget(self.inventory_display)
        
        # Crafting History
        history_group = QGroupBox("📋 Crafting History")
        history_layout = QVBoxLayout(history_group)
        
        self.crafting_history = QTextEdit()
        self.crafting_history.setMaximumHeight(200)
        self.crafting_history.setReadOnly(True)
        history_layout.addWidget(self.crafting_history)
        
        # Clear history button
        clear_history_btn = QPushButton("🗑️ Clear History")
        clear_history_btn.clicked.connect(self.clear_crafting_history)
        history_layout.addWidget(clear_history_btn)
        
        right_layout.addWidget(inventory_group)
        right_layout.addWidget(history_group)
        right_layout.addStretch()
        
        # Add to main layout
        main_layout.addWidget(left_widget, 2)  # 2/3 of space
        main_layout.addWidget(right_widget, 1)  # 1/3 of space
        
        # Profession selection
        profession_layout = QHBoxLayout()
        profession_layout.addWidget(QLabel("Profession:"))
        
        self.profession_combo = QComboBox()
        
        # Only add CRAFTING professions (not gathering or specialization)
        crafting_professions = [
            Profession.ALCHEMY,
            Profession.COOKING,
            Profession.WEAPONSMITH,
            Profession.ARMORSMITH,
            Profession.WOODWORKING,
            Profession.TAILORING,
            Profession.JEWELCRAFTING,
            Profession.ENCHANTING,
            Profession.INSCRIPTION,
            Profession.SHIPBUILDING
        ]
        
        for profession in crafting_professions:
            self.profession_combo.addItem(profession.name.replace('_', ' ').title(), profession)
        self.profession_combo.currentTextChanged.connect(self.on_profession_change)
        profession_layout.addWidget(self.profession_combo)
        
        profession_layout.addStretch()
        left_layout.addLayout(profession_layout)
        
        # Pagination controls
        pagination_group = QGroupBox("📄 Pagination")
        pagination_layout = QVBoxLayout(pagination_group)
        
        # Recipes per page selection
        per_page_layout = QHBoxLayout()
        per_page_layout.addWidget(QLabel("Recipes per page:"))
        
        self.recipes_per_page_combo = QComboBox()
        self.recipes_per_page_combo.addItems(["5", "10", "25", "50"])
        self.recipes_per_page_combo.setCurrentText("10")
        self.recipes_per_page_combo.currentTextChanged.connect(self.on_recipes_per_page_change)
        per_page_layout.addWidget(self.recipes_per_page_combo)
        pagination_layout.addLayout(per_page_layout)
        
        # Page navigation
        page_nav_layout = QHBoxLayout()
        self.prev_page_btn = QPushButton("◀ Previous")
        self.prev_page_btn.clicked.connect(self.prev_page)
        self.prev_page_btn.setEnabled(False)
        page_nav_layout.addWidget(self.prev_page_btn)
        
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setAlignment(Qt.AlignCenter)
        page_nav_layout.addWidget(self.page_label)
        
        self.next_page_btn = QPushButton("Next ▶")
        self.next_page_btn.clicked.connect(self.next_page)
        page_nav_layout.addWidget(self.next_page_btn)
        
        pagination_layout.addLayout(page_nav_layout)
        left_layout.addWidget(pagination_group)
        
        # Skill controls
        skill_group = QGroupBox("⚡ Skill & Tool Levels")
        skill_layout = QVBoxLayout(skill_group)
        
        # Skill level
        skill_level_layout = QHBoxLayout()
        skill_level_layout.addWidget(QLabel("Skill Level:"))
        self.skill_level = QSlider(Qt.Horizontal)
        self.skill_level.setRange(1, 100)
        self.skill_level.setValue(44)  # Default from logs
        self.skill_level.valueChanged.connect(self.on_skill_change)
        skill_level_layout.addWidget(self.skill_level)
        
        self.skill_level_label = QLabel("44")
        self.skill_level_label.setMinimumWidth(30)
        skill_level_layout.addWidget(self.skill_level_label)
        skill_layout.addLayout(skill_level_layout)
        
        # Tool level
        tool_level_layout = QHBoxLayout()
        tool_level_layout.addWidget(QLabel("Tool Tier:"))
        self.tool_level_combo = QComboBox()
        self.tool_level_combo.addItems(["Basic", "Improved", "Advanced"])
        self.tool_level_combo.currentTextChanged.connect(self.on_tool_change)
        tool_level_layout.addWidget(self.tool_level_combo)
        skill_layout.addLayout(tool_level_layout)
        
        left_layout.addWidget(skill_group)
        
        # Storage controls
        storage_group = QGroupBox("📦 Storage Management")
        storage_layout = QVBoxLayout(storage_group)
        
        # Reset buttons
        self.reset_inventory_btn = QPushButton("🎒 Reset Inventory (0)")
        self.reset_inventory_btn.clicked.connect(lambda: self.reset_inventory(0))
        storage_layout.addWidget(self.reset_inventory_btn)
        
        self.reset_storage_1k_btn = QPushButton("🏠 Reset Storage (1K)")
        self.reset_storage_1k_btn.clicked.connect(self.reset_storage_1k)
        storage_layout.addWidget(self.reset_storage_1k_btn)
        
        self.reset_storage_10k_btn = QPushButton("🏰 Reset Storage (10K)")
        self.reset_storage_10k_btn.clicked.connect(self.reset_storage_10k)
        storage_layout.addWidget(self.reset_storage_10k_btn)
        
        left_layout.addWidget(storage_group)
        
        # Crafting controls
        craft_group = QGroupBox("🔨 Crafting")
        craft_layout = QVBoxLayout(craft_group)
        
        # Quantity selection
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Quantity:"))
        self.craft_quantity_input = QSpinBox()
        self.craft_quantity_input.setRange(1, 999)
        self.craft_quantity_input.setValue(1)
        quantity_layout.addWidget(self.craft_quantity_input)
        craft_layout.addLayout(quantity_layout)
        
        # Craft button
        self.craft_button = QPushButton("🔨 Craft Selected Recipe")
        self.craft_button.clicked.connect(self.craft_selected_recipe)
        self.craft_button.setEnabled(False)  # Disabled until recipe selected
        self.craft_button.setStyleSheet("""
            QPushButton {
                background-color: #38a169;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2f855a;
            }
            QPushButton:disabled {
                background-color: #4a5568;
                color: #a0aec0;
            }
        """)
        craft_layout.addWidget(self.craft_button)
        
        left_layout.addWidget(craft_group)
        left_layout.addStretch()
        
        # Recipe list with proper scrolling
        recipe_group = QGroupBox("📜 Available Recipes")
        recipe_layout = QVBoxLayout(recipe_group)
        
        # Scrollable recipe area (THIS IS KEY - only this area scrolls)
        self.recipe_scroll_area = QScrollArea()
        self.recipe_scroll_area.setWidgetResizable(True)
        self.recipe_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.recipe_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.recipe_scroll_area.setMinimumHeight(400)
        
        # Container for recipe buttons
        self.recipe_container = QWidget()
        self.recipe_layout = QVBoxLayout(self.recipe_container)
        self.recipe_layout.setSpacing(5)
        self.recipe_layout.addStretch()  # Push buttons to top
        
        self.recipe_scroll_area.setWidget(self.recipe_container)
        recipe_layout.addWidget(self.recipe_scroll_area)
        
        left_layout.addWidget(recipe_group)
        
        # Load initial data
        self.update_recipes()
        self.update_inventory_display()
