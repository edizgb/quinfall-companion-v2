from ui.base_tab import BaseTab
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                     QComboBox, QSlider, QPushButton, QTextEdit, 
                                     QSpinBox, QGroupBox, QScrollArea, QFrame,
                                     QToolTip, QSizePolicy, QButtonGroup, QRadioButton,
                                     QGridLayout)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QIcon
from utils.icon_manager import icon_manager
from data.enums import Profession, Recipe, ToolType, ProfessionTier, ProfessionCategory
from data.player import Player
from typing import List
import json
from pathlib import Path
from ui.notifications import RecipeUpdateNotifier
import logging

logger = logging.getLogger(__name__)
from utils.recipe_utils import compare_recipes

CRAFTING_PROFESSIONS = [
    Profession.ARMORSMITH,
    Profession.WEAPONSMITH,
    Profession.ALCHEMY,
    Profession.COOKING,
    Profession.ENCHANTING,
    Profession.JEWELCRAFTING,
    Profession.TAILORING,
    Profession.WOODWORKING
]

RECIPE_FILES = {
    'weaponsmith': Path(__file__).parent.parent / 'data' / 'recipes_weaponsmith.json',
    'armorsmith': Path(__file__).parent.parent / 'data' / 'recipes_armorsmith.json',
    'cooking': Path(__file__).parent.parent / 'data' / 'recipes_cooking.json',
    'woodworking': Path(__file__).parent.parent / 'data' / 'recipes_woodworking.json',
    'tailoring': Path(__file__).parent.parent / 'data' / 'recipes_tailoring.json',
    'alchemy': Path(__file__).parent.parent / 'data' / 'recipes_alchemy.json'
}

def load_recipes() -> List[Recipe]:
    """Load recipes from all profession JSON files"""
    all_recipes = []
    
    for profession_name, recipe_file in RECIPE_FILES.items():
        try:
            if not recipe_file.exists():
                logger.debug(f"Recipe file not found: {recipe_file}")
                continue
                
            with open(recipe_file, 'r') as f:
                data = json.load(f)
                recipes = []
                logger.debug(f"Loading {len(data['recipes'])} {profession_name} recipes from JSON")
                
                for i, item in enumerate(data['recipes']):
                    try:
                        # Create a simple recipe object with required attributes
                        recipe = type('Recipe', (), {
                            'name': item['recipe_name'],
                            'profession': Profession[item['profession'].upper()],
                            'skill_level': item['skill_level'],
                            'materials': item['materials'],
                            'tool_level': item.get('tool_level', 1),
                            'weight': item.get('weight', 1.0),
                            'base_price': item.get('base_price', 0),
                            'craft_time': item.get('craft_time', 60),
                            'source': item.get('source', 'Unknown')
                        })()
                        
                        # Add price data if available
                        if 'material_prices' in item:
                            recipe.material_prices = item['material_prices']
                        if 'output_prices' in item:
                            recipe.output_prices = item['output_prices']
                        
                        recipes.append(recipe)
                        logger.debug(f"Loaded {profession_name} recipe {i+1}: {recipe.name} (Skill: {recipe.skill_level})")
                        
                    except Exception as recipe_error:
                        logger.error(f"Error loading {profession_name} recipe {i+1}: {recipe_error}")
                        continue
                        
                all_recipes.extend(recipes)
                logger.debug(f"Successfully loaded {len(recipes)} {profession_name} recipes")
                
        except Exception as e:
            logger.error(f"Error loading {profession_name} recipes file: {e}")
            continue
    
    logger.debug(f"Total recipes loaded: {len(all_recipes)}")
    return all_recipes

CRAFTING_RECIPES = load_recipes()

class CraftingTab(BaseTab):
    def __init__(self, player=None):
        super().__init__("Crafting")
        self.notifier = RecipeUpdateNotifier(self)
        self.current_versions = {}  # Track recipe versions
        self.current_tool_type = "Basic"
        self.current_page = 1
        self.recipes_per_page = 10
        self.selected_recipe = None  # Track currently selected recipe
        self.recipe_buttons = []  # Track recipe buttons for selection
        self.player = player if player else Player()
        if not player:
            self.player.load()
        self.load_preferences()
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
        
        # Price count selection
        price_layout = QHBoxLayout()
        price_layout.addWidget(QLabel("📊 Show lowest prices:"))
        self.price_count_select = QComboBox()
        self.price_count_select.addItems(["5", "10", "25", "50"])
        self.price_count_select.setCurrentText("25")  # Default
        self.price_count_select.currentTextChanged.connect(self.on_price_count_change)
        self.price_count_select.setToolTip("Select how many lowest prices to display")
        price_layout.addWidget(self.price_count_select)
        price_layout.addStretch()
        self.layout.addLayout(price_layout)
        
        # Recipe pagination controls
        pagination_layout = QHBoxLayout()
        pagination_layout.addWidget(QLabel("📋 Recipes per page:"))
        self.recipes_per_page_combo = QComboBox()
        self.recipes_per_page_combo.addItems(["5", "10", "25", "50"])
        self.recipes_per_page_combo.setCurrentText("10")
        self.recipes_per_page_combo.currentTextChanged.connect(self.update_recipe_display)
        self.recipes_per_page_combo.setToolTip("Select how many recipes to display per page")
        pagination_layout.addWidget(self.recipes_per_page_combo)
        
        # Page navigation
        self.prev_page_btn = QPushButton("◀ Previous")
        self.prev_page_btn.clicked.connect(self.prev_page)
        self.prev_page_btn.setToolTip("Go to previous page of recipes")
        self.prev_page_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a5568;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6578;
            }
            QPushButton:disabled {
                background-color: #2d3748;
                color: #718096;
            }
        """)
        pagination_layout.addWidget(self.prev_page_btn)
        
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setStyleSheet("font-weight: bold; color: #e2e8f0;")
        pagination_layout.addWidget(self.page_label)
        
        self.next_page_btn = QPushButton("Next ▶")
        self.next_page_btn.clicked.connect(self.next_page)
        self.next_page_btn.setToolTip("Go to next page of recipes")
        self.next_page_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a5568;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6578;
            }
            QPushButton:disabled {
                background-color: #2d3748;
                color: #718096;
            }
        """)
        pagination_layout.addWidget(self.next_page_btn)
        
        pagination_layout.addStretch()
        self.layout.addLayout(pagination_layout)
        
        # Skill level controls
        skill_layout = QHBoxLayout()
        skill_layout.addWidget(QLabel("Skill Level:"))
        self.skill_level = QSlider(Qt.Horizontal)
        self.skill_level.setRange(1, 100)
        self.skill_level_label = QLabel("1")
        self.skill_level_label.setMinimumWidth(30)
        skill_layout.addWidget(self.skill_level)
        skill_layout.addWidget(self.skill_level_label)
        self.layout.addLayout(skill_layout)
        
        # Tool level controls
        tool_layout = QVBoxLayout()
        
        # Tool type selection
        tool_type_layout = QHBoxLayout()
        tool_type_layout.addWidget(QLabel("Tool Type:"))
        
        self.tool_type_group = QButtonGroup()
        self.tool_basic = QPushButton("Basic")
        self.tool_advanced = QPushButton("Advanced")
        self.tool_improved = QPushButton("Improved")
        
        # Make buttons checkable
        self.tool_basic.setCheckable(True)
        self.tool_advanced.setCheckable(True)
        self.tool_improved.setCheckable(True)
        
        # Add to button group
        self.tool_type_group.addButton(self.tool_basic, 0)
        self.tool_type_group.addButton(self.tool_advanced, 1)
        self.tool_type_group.addButton(self.tool_improved, 2)
        
        # Set default selection
        self.tool_basic.setChecked(True)
        self.current_tool_type = "Basic"
        
        tool_type_layout.addWidget(self.tool_basic)
        tool_type_layout.addWidget(self.tool_advanced)
        tool_type_layout.addWidget(self.tool_improved)
        tool_layout.addLayout(tool_type_layout)
        
        # Tool level slider
        tool_level_layout = QHBoxLayout()
        tool_level_layout.addWidget(QLabel("Tool Level:"))
        self.tool_level = QSlider(Qt.Horizontal)
        self.tool_level.setRange(1, 100)
        self.tool_level_label = QLabel("1")
        self.tool_level_label.setMinimumWidth(30)
        tool_level_layout.addWidget(self.tool_level)
        tool_level_layout.addWidget(self.tool_level_label)
        tool_layout.addLayout(tool_level_layout)
        
        self.layout.addLayout(tool_layout)
        
        # Inventory and Storage Management
        inventory_storage_layout = QVBoxLayout()
        inventory_storage_layout.addWidget(QLabel("📦 Inventory & Storage Management"))
        
        # Reset buttons layout
        reset_layout = QHBoxLayout()
        
        # Inventory reset buttons
        inventory_group = QHBoxLayout()
        inventory_group.addWidget(QLabel("Inventory:"))
        self.reset_inventory_0_btn = QPushButton("Reset to 0")
        self.reset_inventory_1k_btn = QPushButton("Set to 1K")
        self.reset_inventory_10k_btn = QPushButton("Set to 10K")
        
        self.reset_inventory_0_btn.clicked.connect(lambda: self.reset_inventory(0))
        inventory_group.addWidget(self.reset_inventory_0_btn)
        
        self.reset_storage_1k_btn = QPushButton("🏦 Reset Storage (1K)")
        self.reset_storage_1k_btn.clicked.connect(self.reset_storage_1k)
        self.reset_storage_1k_btn.setToolTip("Reset all storage locations to 1000 items each\nStandard storage amount for testing")
        self.reset_storage_1k_btn.setStyleSheet("""
            QPushButton {
                background-color: #3182ce;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2c5aa0;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #2a4365;
                transform: translateY(0px);
            }
        """)
        inventory_group.addWidget(self.reset_storage_1k_btn)
        
        self.reset_storage_10k_btn = QPushButton("🏰 Reset Storage (10K)")
        self.reset_storage_10k_btn.clicked.connect(self.reset_storage_10k)
        self.reset_storage_10k_btn.setToolTip("Reset all storage locations to 10000 items each\nHigh-end storage amount for advanced testing")
        self.reset_storage_10k_btn.setStyleSheet("""
            QPushButton {
                background-color: #38a169;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2f855a;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #276749;
                transform: translateY(0px);
            }
        """)
        inventory_group.addWidget(self.reset_storage_10k_btn)
        
        reset_layout.addLayout(inventory_group)
        
        # Enhanced crafting controls
        craft_layout = QHBoxLayout()
        
        self.craft_selected_btn = QPushButton("⚒️ Craft Selected Recipe")
        self.craft_selected_btn.clicked.connect(self.craft_selected_recipe)
        self.craft_selected_btn.setToolTip("Craft the currently selected recipe\nWill deduct materials from inventory and storage")
        self.craft_selected_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            }
            QPushButton:pressed {
                background: linear-gradient(135deg, #4c51bf 0%, #553c9a 100%);
                transform: translateY(0px);
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }
            QPushButton:disabled {
                background: #4a5568;
                color: #a0aec0;
                transform: none;
                box-shadow: none;
            }
        """)
        craft_layout.addWidget(self.craft_selected_btn)
        
        # Material status indicator
        self.material_status_label = QLabel("💡 Select a recipe to see material availability")
        self.material_status_label.setStyleSheet("""
            QLabel {
                color: #cbd5e0;
                font-size: 12px;
                font-style: italic;
                padding: 8px;
                background: rgba(45, 55, 72, 0.3);
                border-radius: 4px;
                border-left: 3px solid #4a5568;
            }
        """)
        self.material_status_label.setToolTip("Shows the availability status of materials for the selected recipe")
        craft_layout.addWidget(self.material_status_label)
        
        reset_layout.addLayout(craft_layout)
        
        inventory_storage_layout.addLayout(reset_layout)
        
        # Quantity input
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("🔨 Craft:"))
        
        self.craft_quantity_input = QSpinBox()
        self.craft_quantity_input.setRange(1, 999)
        self.craft_quantity_input.setValue(1)
        quantity_layout.addWidget(self.craft_quantity_input)
        craft_layout.addWidget(QLabel("Quantity:"))
        craft_layout.addWidget(self.craft_quantity_input)
        
        self.craft_button = QPushButton("🔨 Craft Selected Recipe")
        self.craft_button.clicked.connect(self.craft_selected_recipe)
        craft_layout.addWidget(self.craft_button)
        
        craft_layout.addStretch()
        inventory_storage_layout.addLayout(craft_layout)
        
        # Material status display
        self.material_status_label = QLabel("Select a recipe to see material requirements")
        self.material_status_label.setWordWrap(True)
        self.material_status_label.setStyleSheet("""
            QLabel {
                border: 1px solid #666;
                border-radius: 4px;
                padding: 8px;
                background-color: #2a2a2a;
                color: #ffffff;
                font-size: 10px;
            }
        """)
        inventory_storage_layout.addWidget(self.material_status_label)
        
        self.layout.addLayout(inventory_storage_layout)
        
        # Recipe display with enhanced styling - Replace QLabel with scrollable button area
        recipe_container = QWidget()
        recipe_container_layout = QVBoxLayout(recipe_container)
        
        # Create scroll area for recipes
        self.recipe_scroll = QScrollArea()
        self.recipe_scroll.setWidgetResizable(True)
        self.recipe_scroll.setMinimumHeight(300)
        self.recipe_scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid #4a90e2;
                border-radius: 8px;
                background-color: #404040;
            }
            QScrollArea > QWidget > QWidget {
                background-color: #404040;
            }
        """)
        
        # Container for recipe buttons
        self.recipe_container = QWidget()
        self.recipe_layout = QVBoxLayout(self.recipe_container)
        self.recipe_layout.setSpacing(5)
        self.recipe_scroll.setWidget(self.recipe_container)
        
        recipe_container_layout.addWidget(QLabel("📋 Available Recipes (Click to Select):"))
        recipe_container_layout.addWidget(self.recipe_scroll)
        self.layout.addWidget(recipe_container)
        
        self.label = QLabel("Crafting System - Work in Progress")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        # Load saved levels for current profession
        self.load_profession_levels()
        
        # Connect signals
        self.profession_select.currentTextChanged.connect(self.update_recipes)
        self.profession_select.currentTextChanged.connect(self.load_profession_levels)
        self.skill_level.valueChanged.connect(self.on_skill_change)
        self.tool_level.valueChanged.connect(self.on_tool_change)
        self.price_count_select.currentTextChanged.connect(self.on_price_count_change)
        self.tool_type_group.buttonClicked.connect(self.on_tool_type_change)

    def on_skill_change(self, value):
        profession = Profession[self.profession_select.currentText().replace(' ', '_')]
        self.player.skills[profession] = value
        self.skill_level_label.setText(str(value))
        self.player.save()
        self.update_recipe_display()

    def on_tool_change(self, value):
        # Save tool level per profession
        profession = Profession[self.profession_select.currentText().replace(' ', '_')]
        if not hasattr(self.player, 'profession_tool_levels'):
            self.player.profession_tool_levels = {}
        self.player.profession_tool_levels[profession] = value
        self.tool_level_label.setText(str(value))
        self.player.save()
        self.update_recipe_display()
    
    def on_price_count_change(self, value):
        """Handle price count selection change"""
        self.save_preferences()
        self.update_recipe_display()
    
    def on_recipes_per_page_change(self, value):
        """Handle recipes per page selection change"""
        self.recipes_per_page = int(value)
        self.current_page = 1  # Reset to first page
        self.update_recipe_display()
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_recipe_display()
    
    def next_page(self):
        """Go to next page"""
        # Calculate total pages based on filtered recipes
        current_profession = Profession[self.profession_select.currentText().replace(' ', '_')]
        skill_level = self.player.skills.get(current_profession, 1)
        filtered = [r for r in CRAFTING_RECIPES 
                   if r.profession == current_profession 
                   and r.skill_level <= skill_level]
        total_pages = max(1, (len(filtered) + self.recipes_per_page - 1) // self.recipes_per_page)
        
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_recipe_display()
    
    def on_tool_type_change(self, button):
        """Handle tool type button selection change"""
        tool_types = ["Basic", "Advanced", "Improved"]
        self.current_tool_type = tool_types[self.tool_type_group.id(button)]
        
        # Save tool type preference per profession
        profession = Profession[self.profession_select.currentText().replace(' ', '_')]
        if not hasattr(self.player, 'tool_types'):
            self.player.tool_types = {}
        self.player.tool_types[profession] = self.current_tool_type
        
        self.player.save()
        self.update_recipe_display()

    def can_craft(self, recipe: Recipe) -> bool:
        skill_req = self.player.skills[recipe.profession] >= recipe.tier.value
        tool_req = self.player.tools[recipe.required_tool] >= recipe.tool_level
        return skill_req and tool_req

    def craft_item(self, recipe: Recipe):
        try:
            if not self.can_craft(recipe):
                missing = []
                if self.player.skills[recipe.profession] < recipe.tier.value:
                    missing.append(f"skill level {recipe.tier.value}")
                if self.player.tools[recipe.required_tool] < recipe.tool_level:
                    missing.append(f"tool level {recipe.tool_level}")
                raise ValueError(f"Cannot craft - missing requirements: {', '.join(missing)}")
            
            # Crafting logic here
            logger.info(f"Crafted: {recipe.name}")
            self.player.save()
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return False
        return True

    def update_recipes(self, profession_text):
        """Update recipes when profession changes"""
        self.current_page = 1  # Reset to first page when profession changes
        self.update_recipe_display()

    def update_recipe_display(self):
        """Update displayed recipes based on filters with pagination"""
        try:
            current_profession = Profession[self.profession_select.currentText().replace(' ', '_')]
            skill_level = self.player.skills.get(current_profession, 1)
            price_count = int(self.price_count_select.currentText())
            
            logger.debug(f"Profession={current_profession}, Skill={skill_level}, Price Count={price_count}")
        
            # Filter recipes by profession and skill level
            filtered = [r for r in CRAFTING_RECIPES 
                       if r.profession == current_profession 
                       and r.skill_level <= skill_level]
            
            logger.debug(f"Found {len(filtered)} recipes for {current_profession}")
            filtered.sort(key=lambda x: (x.skill_level, x.name))
            
            # Calculate pagination
            total_recipes = len(filtered)
            total_pages = max(1, (total_recipes + self.recipes_per_page - 1) // self.recipes_per_page)
            
            # Ensure current page is valid
            if self.current_page > total_pages:
                self.current_page = total_pages
            
            # Get recipes for current page
            start_idx = (self.current_page - 1) * self.recipes_per_page
            end_idx = start_idx + self.recipes_per_page
            page_recipes = filtered[start_idx:end_idx]
            
            # Update pagination controls
            self.page_label.setText(f"Page {self.current_page} of {total_pages} ({total_recipes} recipes)")
            self.prev_page_btn.setEnabled(self.current_page > 1)
            self.next_page_btn.setEnabled(self.current_page < total_pages)
            
            # Clear existing recipe buttons
            for button in self.recipe_buttons:
                button.deleteLater()
            self.recipe_buttons.clear()
            
            # Create recipe buttons
            if not page_recipes:
                no_recipes_label = QLabel(f"No recipes available for {current_profession} at skill level {skill_level}")
                no_recipes_label.setStyleSheet("color: #cbd5e0; font-style: italic; padding: 20px;")
                no_recipes_label.setAlignment(Qt.AlignCenter)
                self.recipe_layout.addWidget(no_recipes_label)
                self.recipe_buttons.append(no_recipes_label)
                self.page_label.setText("Page 1 of 1 (0 recipes)")
                self.prev_page_btn.setEnabled(False)
                self.next_page_btn.setEnabled(False)
            else:
                for recipe in page_recipes:
                    button = self.create_recipe_button(recipe, skill_level, price_count)
                    self.recipe_layout.addWidget(button)
                    self.recipe_buttons.append(button)
                    
                    # If this was the previously selected recipe, keep it selected
                    if self.selected_recipe and recipe.name == self.selected_recipe.name:
                        button.setChecked(True)
            
            # Add stretch to push buttons to top
            self.recipe_layout.addStretch()
            
            logger.debug(f"Displaying {len(page_recipes)} recipe buttons on page {self.current_page}")
            
        except Exception as e:
            logger.error(f"Error in update_recipe_display: {e}")
            # Show error in recipe area
            error_label = QLabel(f"Error loading recipes: {e}")
            error_label.setStyleSheet("color: #f87171; padding: 20px;")
            self.recipe_layout.addWidget(error_label)

    def create_recipe_button(self, recipe, skill_level, price_count):
        """Create a clickable button for a recipe with all the formatting"""
        button = QPushButton()
        button.setCheckable(True)
        button.clicked.connect(lambda checked, r=recipe: self.select_recipe(r))
        
        # Get profession icon
        prof_icon = icon_manager.get_profession_icon(recipe.profession.name.lower())
        
        # Color-coded recipe name based on skill level
        if recipe.skill_level <= 10:
            skill_color = "#4ade80"  # Bright green for easy
        elif recipe.skill_level <= 30:
            skill_color = "#fbbf24"  # Bright yellow for medium
        elif recipe.skill_level <= 60:
            skill_color = "#fb923c"  # Bright orange for hard
        else:
            skill_color = "#f87171"  # Bright red for expert
        
        # Build button text with recipe info
        button_text = f"{prof_icon} {recipe.name} (Tool Lv{getattr(recipe, 'tool_level', 1)}, Skill Lv{recipe.skill_level})"
        
        # Add price/material information
        if hasattr(recipe, 'material_prices') and hasattr(recipe, 'output_prices'):
            # Calculate profit
            total_material_cost = sum(sum(recipe.material_prices[mat][:price_count])/len(recipe.material_prices[mat][:price_count]) * qty 
                                    for mat, qty in recipe.materials.items() if mat in recipe.material_prices)
            output_prices = recipe.output_prices[:price_count]
            avg_output = sum(output_prices) / len(output_prices)
            profit = avg_output - total_material_cost
            
            profit_text = f"Profit: {profit:.1f}g" if profit > 0 else f"Loss: {abs(profit):.1f}g"
            button_text += f"\n💰 {profit_text}"
        else:
            # Show material availability
            available_materials = []
            missing_materials = []
            for material, quantity in recipe.materials.items():
                available = self.player.get_item_count(material, "both")
                if available >= quantity:
                    available_materials.append(f"{material}: {available}/{quantity}")
                else:
                    missing_materials.append(f"{material}: {available}/{quantity}")
            
            if missing_materials:
                button_text += f"\n❌ Missing: {', '.join(missing_materials[:2])}"
                if len(missing_materials) > 2:
                    button_text += f" (+{len(missing_materials)-2} more)"
            else:
                button_text += f"\n✅ All materials available"
        
        button.setText(button_text)
        
        # Style the button
        button.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 10px;
                border: 2px solid #666;
                border-radius: 6px;
                background-color: #2a2a2a;
                color: {skill_color};
                font-size: 11px;
                font-weight: bold;
                min-height: 60px;
            }}
            QPushButton:hover {{
                background-color: #3a3a3a;
                border-color: #4a90e2;
            }}
            QPushButton:checked {{
                background-color: #4a90e2;
                border-color: #60a5fa;
                color: white;
            }}
        """)
        
        return button
    
    def select_recipe(self, recipe):
        """Handle recipe selection"""
        # Uncheck all other recipe buttons
        for btn in self.recipe_buttons:
            if btn.isChecked() and btn.text() != f"{icon_manager.get_profession_icon(recipe.profession.name.lower())} {recipe.name}":
                btn.setChecked(False)
        
        self.selected_recipe = recipe
        self.update_material_status()
        logger.info(f"Selected recipe: {recipe.name}")
    
    def update_material_status(self):
        """Update the material status display for selected recipe"""
        if not self.selected_recipe:
            self.material_status_label.setText("💡 Select a recipe to see material availability")
            return
        
        recipe = self.selected_recipe
        status_parts = []
        
        for material, quantity in recipe.materials.items():
            available = self.player.get_item_count(material, "both")
            if available >= quantity:
                status = "✅"
            else:
                status = "❌"
            
            status_parts.append(
                f"  {status} {material}: {available} / {quantity}"
            )
        
        status_text = f"📋 {recipe.name} Materials:\n" + "\n".join(status_parts)
        self.material_status_label.setText(status_text)
    
    def get_selected_recipe(self):
        """Get currently selected recipe from display"""
        return self.selected_recipe
    
    def load_preferences(self):
        """Load user preferences for price display"""
        try:
            prefs_file = Path(__file__).parent.parent / 'saves' / 'ui_preferences.json'
            if prefs_file.exists():
                with open(prefs_file, 'r') as f:
                    prefs = json.load(f)
                    self.price_count_preference = prefs.get('price_count', 5)
            else:
                self.price_count_preference = 5
        except Exception as e:
            logger.error(f"Error loading preferences: {e}")
            self.price_count_preference = 5
    
    def load_profession_levels(self):
        """Load saved skill and tool levels for current profession"""
        try:
            profession = Profession[self.profession_select.currentText().replace(' ', '_')]
            
            # Load skill level
            skill_level = self.player.skills.get(profession, 1)
            self.skill_level.setValue(skill_level)
            self.skill_level_label.setText(str(skill_level))
            
            # Load tool level per profession (not just ToolType.FORGE)
            if not hasattr(self.player, 'profession_tool_levels'):
                self.player.profession_tool_levels = {}
            tool_level = self.player.profession_tool_levels.get(profession, 1)
            self.tool_level.setValue(tool_level)
            self.tool_level_label.setText(str(tool_level))
            
            # Load tool type preference (default to Basic)
            tool_type_pref = getattr(self.player, 'tool_types', {}).get(profession, "Basic")
            if tool_type_pref == "Advanced":
                self.tool_advanced.setChecked(True)
                self.current_tool_type = "Advanced"
            elif tool_type_pref == "Improved":
                self.tool_improved.setChecked(True)
                self.current_tool_type = "Improved"
            else:
                self.tool_basic.setChecked(True)
                self.current_tool_type = "Basic"
            
            # Update recipe display
            self.update_recipe_display()
        except Exception as e:
            logger.error(f"Error loading profession levels: {e}")
    
    def save_preferences(self):
        """Save user preferences for price display"""
        try:
            prefs_file = Path(__file__).parent.parent / 'saves' / 'ui_preferences.json'
            prefs_file.parent.mkdir(exist_ok=True)
            
            prefs = {'price_count': int(self.price_count_select.currentText())}
            
            with open(prefs_file, 'w') as f:
                json.dump(prefs, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving preferences: {e}")

    def check_for_updates(self, recipe):
        """Check if recipe has been updated"""
        current_version = self.current_versions.get(recipe.name)
        if current_version and recipe.version != current_version:
            changes = compare_recipes(recipe, self.get_latest_recipe(recipe.name))
            if changes:
                self.notifier.show_update_alert(changes)
        self.current_versions[recipe.name] = recipe.version
    
    def reset_inventory(self, value=0):
        """Reset inventory to specified value"""
        try:
            self.player.reset_inventory(value)
            self.player.save()
            self.update_material_status()
            logger.info(f"✅ Inventory reset to {value} for all materials")
        except Exception as e:
            logger.error(f"❌ Error resetting inventory: {e}")
    
    def reset_storage(self, value=1000):
        """Reset storage to specified value"""
        try:
            self.player.reset_storage(value)
            self.player.save()
            self.update_material_status()
            logger.info(f"✅ Storage reset to {value} for all materials")
        except Exception as e:
            logger.error(f"❌ Error resetting storage: {e}")
    
    def reset_storage_1k(self):
        """Reset storage to 1000 for all materials"""
        self.reset_storage(1000)
    
    def reset_storage_10k(self):
        """Reset storage to 10000 for all materials"""
        self.reset_storage(10000)
    
    def craft_selected_recipe(self):
        """Craft the currently selected recipe"""
        recipe = self.get_selected_recipe()
        if recipe:
            self.craft_item(recipe)
        else:
            logger.warning("No recipe selected for crafting")
