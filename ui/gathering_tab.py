from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider, 
                             QPushButton, QTextEdit, QSpinBox, QGroupBox, QGridLayout,
                             QProgressBar, QFrame, QScrollArea, QWidget)
from PySide6.QtCore import Qt, QTimer
from ui.base_tab import BaseTab
from data.enums import GatheringProfession, Profession
from data.player import Player
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class GatheringTab(BaseTab):
    def __init__(self):
        super().__init__("Gathering")
        self.player = Player()
        self.player.load()
        
        # Gathering data
        self.gathering_locations = self.load_gathering_locations()
        self.resource_data = self.load_resource_data()
        
        # UI state
        self.current_profession = GatheringProfession.MINING
        self.current_location = None
        self.gathering_timer = QTimer()
        self.gathering_timer.timeout.connect(self.simulate_gathering)
        
        self.setup_ui()
        logger.info("🌿 Gathering tab initialized")

    def setup_ui(self):
        """Setup the complete gathering UI"""
        main_layout = QVBoxLayout()
        
        # Header
        header = QLabel("🌿 Quinfall Gathering System")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #4ade80; margin: 10px;")
        main_layout.addWidget(header)
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Profession Selection Section
        prof_group = self.create_profession_section()
        content_layout.addWidget(prof_group)
        
        # Location and Resources Section
        location_group = self.create_location_section()
        content_layout.addWidget(location_group)
        
        # Gathering Tools Section
        tools_group = self.create_tools_section()
        content_layout.addWidget(tools_group)
        
        # Active Gathering Section
        gathering_group = self.create_gathering_section()
        content_layout.addWidget(gathering_group)
        
        # Inventory Status Section
        inventory_group = self.create_inventory_section()
        content_layout.addWidget(inventory_group)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
        
        # Initialize displays
        self.update_profession_display()
        self.update_location_display()
        self.update_tools_display()
        self.update_inventory_display()

    def create_profession_section(self):
        """Create profession selection and skill display section"""
        group = QGroupBox("⚒️ Gathering Profession & Skills")
        layout = QGridLayout()
        
        # Profession selection
        layout.addWidget(QLabel("Profession:"), 0, 0)
        self.profession_select = QComboBox()
        self.profession_select.addItems([
            "Mining ⛏️", "Lumberjack 🪓", "Harvester 🌾", 
            "Fishing 🎣", "Hunter 🏹", "Animal Keeper 🐄"
        ])
        self.profession_select.currentTextChanged.connect(self.on_profession_change)
        layout.addWidget(self.profession_select, 0, 1)
        
        # Skill level display and control
        layout.addWidget(QLabel("Current Skill:"), 1, 0)
        self.skill_level_label = QLabel("1")
        self.skill_level_label.setStyleSheet("font-weight: bold; color: #60a5fa;")
        layout.addWidget(self.skill_level_label, 1, 1)
        
        # Skill adjustment (for testing/admin)
        layout.addWidget(QLabel("Adjust Skill:"), 2, 0)
        self.skill_slider = QSlider(Qt.Horizontal)
        self.skill_slider.setRange(1, 100)
        self.skill_slider.setValue(1)
        self.skill_slider.valueChanged.connect(self.on_skill_change)
        layout.addWidget(self.skill_slider, 2, 1)
        
        # Experience progress
        layout.addWidget(QLabel("Experience:"), 3, 0)
        self.exp_progress = QProgressBar()
        self.exp_progress.setRange(0, 100)
        self.exp_progress.setValue(0)
        layout.addWidget(self.exp_progress, 3, 1)
        
        group.setLayout(layout)
        return group

    def create_location_section(self):
        """Create location selection and resource display section"""
        group = QGroupBox("🗺️ Gathering Locations & Resources")
        layout = QVBoxLayout()
        
        # Location selection
        location_layout = QHBoxLayout()
        location_layout.addWidget(QLabel("Location:"))
        self.location_select = QComboBox()
        self.location_select.currentTextChanged.connect(self.on_location_change)
        location_layout.addWidget(self.location_select)
        
        self.travel_button = QPushButton("🚶 Travel Here")
        self.travel_button.clicked.connect(self.travel_to_location)
        location_layout.addWidget(self.travel_button)
        
        layout.addLayout(location_layout)
        
        # Available resources display
        self.resources_display = QTextEdit()
        self.resources_display.setMaximumHeight(120)
        self.resources_display.setReadOnly(True)
        self.resources_display.setStyleSheet("background-color: #1e293b; color: #e2e8f0; border: 1px solid #475569;")
        layout.addWidget(QLabel("Available Resources:"))
        layout.addWidget(self.resources_display)
        
        group.setLayout(layout)
        return group

    def create_tools_section(self):
        """Create gathering tools section"""
        group = QGroupBox("🔧 Gathering Tools")
        layout = QGridLayout()
        
        # Tool type selection
        layout.addWidget(QLabel("Tool Type:"), 0, 0)
        self.tool_type_select = QComboBox()
        self.tool_type_select.addItems(["Basic", "Advanced", "Improved", "Master"])
        self.tool_type_select.currentTextChanged.connect(self.on_tool_change)
        layout.addWidget(self.tool_type_select, 0, 1)
        
        # Tool level
        layout.addWidget(QLabel("Tool Level:"), 1, 0)
        self.tool_level_spin = QSpinBox()
        self.tool_level_spin.setRange(1, 100)
        self.tool_level_spin.valueChanged.connect(self.on_tool_level_change)
        layout.addWidget(self.tool_level_spin, 1, 1)
        
        # Tool efficiency display
        layout.addWidget(QLabel("Efficiency:"), 2, 0)
        self.efficiency_label = QLabel("100%")
        self.efficiency_label.setStyleSheet("color: #4ade80; font-weight: bold;")
        layout.addWidget(self.efficiency_label, 2, 1)
        
        # Durability (for future implementation)
        layout.addWidget(QLabel("Durability:"), 3, 0)
        self.durability_progress = QProgressBar()
        self.durability_progress.setRange(0, 100)
        self.durability_progress.setValue(100)
        layout.addWidget(self.durability_progress, 3, 1)
        
        group.setLayout(layout)
        return group

    def create_gathering_section(self):
        """Create active gathering section"""
        group = QGroupBox("⚡ Active Gathering")
        layout = QVBoxLayout()
        
        # Gathering controls
        controls_layout = QHBoxLayout()
        
        self.resource_select = QComboBox()
        controls_layout.addWidget(QLabel("Target Resource:"))
        controls_layout.addWidget(self.resource_select)
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 1000)
        self.quantity_spin.setValue(10)
        controls_layout.addWidget(QLabel("Quantity:"))
        controls_layout.addWidget(self.quantity_spin)
        
        layout.addLayout(controls_layout)
        
        # Gathering buttons
        button_layout = QHBoxLayout()
        self.start_gathering_btn = QPushButton("🚀 Start Gathering")
        self.start_gathering_btn.clicked.connect(self.start_gathering)
        self.start_gathering_btn.setStyleSheet("background-color: #059669; color: white; font-weight: bold;")
        
        self.stop_gathering_btn = QPushButton("⏹️ Stop Gathering")
        self.stop_gathering_btn.clicked.connect(self.stop_gathering)
        self.stop_gathering_btn.setEnabled(False)
        self.stop_gathering_btn.setStyleSheet("background-color: #dc2626; color: white; font-weight: bold;")
        
        button_layout.addWidget(self.start_gathering_btn)
        button_layout.addWidget(self.stop_gathering_btn)
        layout.addLayout(button_layout)
        
        # Gathering progress
        layout.addWidget(QLabel("Progress:"))
        self.gathering_progress = QProgressBar()
        self.gathering_progress.setRange(0, 100)
        layout.addWidget(self.gathering_progress)
        
        # Gathering log
        layout.addWidget(QLabel("Gathering Log:"))
        self.gathering_log = QTextEdit()
        self.gathering_log.setMaximumHeight(100)
        self.gathering_log.setReadOnly(True)
        self.gathering_log.setStyleSheet("background-color: #0f172a; color: #e2e8f0; border: 1px solid #475569;")
        layout.addWidget(self.gathering_log)
        
        group.setLayout(layout)
        return group

    def create_inventory_section(self):
        """Create inventory status section"""
        group = QGroupBox("📦 Inventory Status")
        layout = QVBoxLayout()
        
        # Inventory summary
        self.inventory_display = QTextEdit()
        self.inventory_display.setMaximumHeight(100)
        self.inventory_display.setReadOnly(True)
        self.inventory_display.setStyleSheet("background-color: #1e293b; color: #e2e8f0; border: 1px solid #475569;")
        layout.addWidget(self.inventory_display)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        
        self.bank_items_btn = QPushButton("🏦 Bank Items")
        self.bank_items_btn.clicked.connect(self.bank_gathered_items)
        
        self.sell_items_btn = QPushButton("💰 Quick Sell")
        self.sell_items_btn.clicked.connect(self.sell_gathered_items)
        
        actions_layout.addWidget(self.bank_items_btn)
        actions_layout.addWidget(self.sell_items_btn)
        layout.addLayout(actions_layout)
        
        group.setLayout(layout)
        return group

    def load_gathering_locations(self):
        """Load gathering locations data"""
        # Quinfall gathering locations with authentic names
        return {
            "Mining": [
                "Quinfall City Mines", "Iron Hills", "Copper Valley", 
                "Gold Ridge", "Crystal Caverns", "Deep Mines"
            ],
            "Lumberjack": [
                "Whispering Woods", "Ancient Forest", "Pine Grove", 
                "Darkwood", "Sacred Grove", "Timber Valley"
            ],
            "Harvester": [
                "Golden Fields", "Harvest Plains", "Fertile Valley", 
                "Grain Meadows", "Crop Lands", "Agricultural District"
            ],
            "Fishing": [
                "Quinfall Harbor", "Crystal Lake", "River Bend", 
                "Deep Sea", "Mountain Stream", "Fishing Docks"
            ],
            "Hunter": [
                "Hunting Grounds", "Wild Plains", "Beast Territory", 
                "Monster Lair", "Creature Habitat", "Wilderness"
            ],
            "Animal Keeper": [
                "Animal Sanctuary", "Wildlife Reserve", "Petting Zoo", 
                "Conservation Area", "Nature Preserve", "Zoo"
            ]
        }

    def load_resource_data(self):
        """Load resource data for each profession"""
        return {
            "Mining": {
                "Copper Ore": {"level": 1, "exp": 5, "value": 2.5},
                "Iron Ore": {"level": 10, "exp": 10, "value": 5.0},
                "Silver Ore": {"level": 25, "exp": 20, "value": 12.0},
                "Gold Ore": {"level": 40, "exp": 35, "value": 25.0},
                "Mithril Ore": {"level": 60, "exp": 50, "value": 45.0},
                "Adamant Ore": {"level": 80, "exp": 75, "value": 80.0}
            },
            "Lumberjack": {
                "Oak Wood": {"level": 1, "exp": 5, "value": 3.0},
                "Pine Wood": {"level": 8, "exp": 8, "value": 4.5},
                "Birch Wood": {"level": 20, "exp": 15, "value": 8.0},
                "Maple Wood": {"level": 35, "exp": 25, "value": 15.0},
                "Ebony Wood": {"level": 55, "exp": 40, "value": 30.0},
                "Ancient Wood": {"level": 75, "exp": 60, "value": 55.0}
            },
            "Harvester": {
                "Wheat": {"level": 1, "exp": 3, "value": 1.5},
                "Barley": {"level": 5, "exp": 5, "value": 2.0},
                "Corn": {"level": 15, "exp": 10, "value": 4.0},
                "Rice": {"level": 30, "exp": 18, "value": 7.5},
                "Quinoa": {"level": 50, "exp": 30, "value": 15.0},
                "Ancient Grain": {"level": 70, "exp": 45, "value": 28.0}
            },
            "Fishing": {
                "Small Fish": {"level": 1, "exp": 4, "value": 2.0},
                "Trout": {"level": 12, "exp": 8, "value": 5.5},
                "Salmon": {"level": 28, "exp": 15, "value": 12.0},
                "Tuna": {"level": 45, "exp": 25, "value": 22.0},
                "Rare Fish": {"level": 65, "exp": 40, "value": 40.0},
                "Legendary Fish": {"level": 85, "exp": 65, "value": 75.0}
            },
            "Hunter": {
                "Leather": {"level": 1, "exp": 5, "value": 4.0},
                "Thick Hide": {"level": 15, "exp": 10, "value": 8.0},
                "Beast Pelt": {"level": 30, "exp": 18, "value": 15.0},
                "Dragon Scale": {"level": 50, "exp": 35, "value": 35.0},
                "Rare Hide": {"level": 70, "exp": 50, "value": 65.0},
                "Legendary Pelt": {"level": 90, "exp": 75, "value": 120.0}
            },
            "Animal Keeper": {
                "Feathers": {"level": 1, "exp": 3, "value": 1.5},
                "Fur": {"level": 5, "exp": 5, "value": 2.0},
                "Scales": {"level": 15, "exp": 10, "value": 4.0},
                "Hides": {"level": 30, "exp": 18, "value": 7.5},
                "Rare Materials": {"level": 50, "exp": 30, "value": 15.0},
                "Exotic Materials": {"level": 70, "exp": 45, "value": 28.0}
            }
        }

    def on_profession_change(self, profession_text):
        """Handle profession change"""
        prof_name = profession_text.split()[0]  # Remove emoji
        
        # Map dropdown names to enum names
        profession_mapping = {
            "Mining": "MINING",
            "Lumberjack": "LUMBERJACK", 
            "Harvester": "HARVESTER",
            "Fishing": "FISHING",
            "Hunter": "HUNTER",
            "Animal": "ANIMAL_KEEPER"  # "Animal Keeper" -> first word is "Animal"
        }
        
        enum_name = profession_mapping.get(prof_name, prof_name.upper())
        
        try:
            self.current_profession = GatheringProfession[enum_name]
            logger.info(f"🔄 Changed gathering profession to: {prof_name}")
            self.update_profession_display()
            self.update_location_display()
        except KeyError:
            logger.error(f"❌ Invalid profession: {prof_name}")

    def update_profession_display(self):
        """Update profession-related displays"""
        prof_name = self.current_profession.name.title()
        current_skill = self.player.gathering.get(self.current_profession, 1)
        
        self.skill_level_label.setText(str(current_skill))
        self.skill_slider.setValue(current_skill)
        
        # Update experience progress (simulated)
        exp_progress = (current_skill % 10) * 10
        self.exp_progress.setValue(exp_progress)

    def update_location_display(self):
        """Update location selection based on profession"""
        # Map enum names back to dictionary keys
        enum_to_dict_mapping = {
            "MINING": "Mining",
            "LUMBERJACK": "Lumberjack", 
            "HARVESTER": "Harvester",
            "FISHING": "Fishing",
            "HUNTER": "Hunter",
            "ANIMAL_KEEPER": "Animal Keeper"
        }
        
        prof_name = enum_to_dict_mapping.get(self.current_profession.name, self.current_profession.name.title())
        locations = self.gathering_locations.get(prof_name, [])
        
        self.location_select.clear()
        self.location_select.addItems(locations)
        
        if locations:
            self.current_location = locations[0]
            self.update_resources_display()

    def update_resources_display(self):
        """Update available resources display"""
        # Map enum names back to dictionary keys
        enum_to_dict_mapping = {
            "MINING": "Mining",
            "LUMBERJACK": "Lumberjack", 
            "HARVESTER": "Harvester",
            "FISHING": "Fishing",
            "HUNTER": "Hunter",
            "ANIMAL_KEEPER": "Animal Keeper"
        }
        
        prof_name = enum_to_dict_mapping.get(self.current_profession.name, self.current_profession.name.title())
        resources = self.resource_data.get(prof_name, {})
        current_skill = self.player.gathering.get(self.current_profession, 1)
        
        # Filter resources by skill level
        available_resources = []
        for resource, data in resources.items():
            if data["level"] <= current_skill:
                available_resources.append(f"✅ {resource} (Lv.{data['level']}) - {data['value']}g")
            else:
                available_resources.append(f"🔒 {resource} (Lv.{data['level']}) - Locked")
        
        self.resources_display.setPlainText("\n".join(available_resources))
        
        # Update resource selection dropdown
        self.resource_select.clear()
        unlocked_resources = [name for name, data in resources.items() 
                            if data["level"] <= current_skill]
        self.resource_select.addItems(unlocked_resources)

    def update_tools_display(self):
        """Update tools display"""
        # Calculate efficiency based on tool type and level
        tool_type = self.tool_type_select.currentText()
        tool_level = self.tool_level_spin.value()
        
        base_efficiency = {"Basic": 100, "Advanced": 125, "Improved": 150, "Master": 200}
        efficiency = base_efficiency.get(tool_type, 100) + (tool_level - 1) * 2
        
        self.efficiency_label.setText(f"{efficiency}%")
        
        # Update efficiency color
        if efficiency >= 150:
            color = "#4ade80"  # Green
        elif efficiency >= 120:
            color = "#fbbf24"  # Yellow
        else:
            color = "#f87171"  # Red
        
        self.efficiency_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def update_inventory_display(self):
        """Update inventory status display"""
        # Get gathering-related items from player inventory
        gathering_items = []
        prof_name = self.current_profession.name.title()
        resources = self.resource_data.get(prof_name, {})
        
        for resource in resources.keys():
            count = self.player.get_item_count(resource.lower().replace(" ", "_"), "inventory")
            if count > 0:
                gathering_items.append(f"{resource}: {count}")
        
        if gathering_items:
            self.inventory_display.setPlainText("Current Inventory:\n" + "\n".join(gathering_items))
        else:
            self.inventory_display.setPlainText("No gathering items in inventory.")

    def on_skill_change(self, value):
        """Handle skill level change"""
        self.player.gathering[self.current_profession] = value
        self.player.save()
        self.update_profession_display()
        self.update_resources_display()
        logger.info(f"📈 {self.current_profession.name} skill updated to: {value}")

    def on_location_change(self, location):
        """Handle location change"""
        self.current_location = location
        logger.info(f"📍 Location changed to: {location}")

    def on_tool_change(self):
        """Handle tool type change"""
        self.update_tools_display()

    def on_tool_level_change(self):
        """Handle tool level change"""
        self.update_tools_display()

    def travel_to_location(self):
        """Simulate traveling to selected location"""
        location = self.location_select.currentText()
        self.log_message(f"🚶 Traveled to {location}")
        self.current_location = location

    def start_gathering(self):
        """Start the gathering process"""
        if not self.resource_select.currentText():
            self.log_message("❌ No resource selected!")
            return
        
        self.start_gathering_btn.setEnabled(False)
        self.stop_gathering_btn.setEnabled(True)
        self.gathering_progress.setValue(0)
        
        resource = self.resource_select.currentText()
        quantity = self.quantity_spin.value()
        
        self.log_message(f"🚀 Started gathering {quantity}x {resource}")
        
        # Start gathering timer (simulate gathering over time)
        self.gathering_timer.start(1000)  # Update every second

    def stop_gathering(self):
        """Stop the gathering process"""
        self.gathering_timer.stop()
        self.start_gathering_btn.setEnabled(True)
        self.stop_gathering_btn.setEnabled(False)
        self.gathering_progress.setValue(0)
        
        self.log_message("⏹️ Gathering stopped")

    def simulate_gathering(self):
        """Simulate gathering progress"""
        current_progress = self.gathering_progress.value()
        
        # Calculate gathering speed based on efficiency
        tool_type = self.tool_type_select.currentText()
        base_speed = {"Basic": 2, "Advanced": 3, "Improved": 4, "Master": 6}
        speed = base_speed.get(tool_type, 2)
        
        new_progress = min(100, current_progress + speed)
        self.gathering_progress.setValue(new_progress)
        
        # Complete gathering
        if new_progress >= 100:
            self.complete_gathering()

    def complete_gathering(self):
        """Complete the gathering process"""
        self.gathering_timer.stop()
        
        resource = self.resource_select.currentText()
        quantity = self.quantity_spin.value()
        
        # Add items to inventory
        resource_key = resource.lower().replace(" ", "_")
        current_count = self.player.get_item_count(resource_key, "inventory")
        self.player.set_item_count(resource_key, current_count + quantity, "inventory")
        
        # Add experience (simplified)
        prof_name = self.current_profession.name.title()
        resource_data = self.resource_data.get(prof_name, {}).get(resource, {})
        exp_gained = resource_data.get("exp", 5) * quantity
        
        self.log_message(f"✅ Gathered {quantity}x {resource}! (+{exp_gained} exp)")
        
        # Reset UI
        self.start_gathering_btn.setEnabled(True)
        self.stop_gathering_btn.setEnabled(False)
        self.gathering_progress.setValue(0)
        
        # Update displays
        self.update_inventory_display()

    def bank_gathered_items(self):
        """Move gathered items to bank storage"""
        prof_name = self.current_profession.name.title()
        resources = self.resource_data.get(prof_name, {})
        
        banked_items = []
        for resource in resources.keys():
            resource_key = resource.lower().replace(" ", "_")
            inventory_count = self.player.get_item_count(resource_key, "inventory")
            
            if inventory_count > 0:
                # Move to bank
                bank_count = self.player.get_item_count(resource_key, "storage")
                self.player.set_item_count(resource_key, bank_count + inventory_count, "storage")
                self.player.set_item_count(resource_key, 0, "inventory")
                banked_items.append(f"{resource}: {inventory_count}")
        
        if banked_items:
            self.log_message(f"🏦 Banked items: {', '.join(banked_items)}")
        else:
            self.log_message("🏦 No items to bank")
        
        self.update_inventory_display()

    def sell_gathered_items(self):
        """Sell gathered items for gold"""
        prof_name = self.current_profession.name.title()
        resources = self.resource_data.get(prof_name, {})
        
        total_value = 0
        sold_items = []
        
        for resource, data in resources.items():
            resource_key = resource.lower().replace(" ", "_")
            inventory_count = self.player.get_item_count(resource_key, "inventory")
            
            if inventory_count > 0:
                item_value = data.get("value", 1.0) * inventory_count
                total_value += item_value
                sold_items.append(f"{resource}: {inventory_count}")
                
                # Remove from inventory
                self.player.set_item_count(resource_key, 0, "inventory")
        
        if sold_items:
            self.log_message(f"💰 Sold items for {total_value:.1f}g: {', '.join(sold_items)}")
        else:
            self.log_message("💰 No items to sell")
        
        self.update_inventory_display()

    def log_message(self, message):
        """Add message to gathering log"""
        self.gathering_log.append(f"[{self.get_timestamp()}] {message}")
        
        # Keep log size manageable
        if self.gathering_log.document().blockCount() > 50:
            cursor = self.gathering_log.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.select(cursor.BlockUnderCursor)
            cursor.removeSelectedText()

    def get_timestamp(self):
        """Get current timestamp for logging"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
