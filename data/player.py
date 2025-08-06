from data.enums import Profession, ToolType, GatheringProfession, Specialization
from data.storage_system import QuinfallStorageSystem, StorageLocation
from data.quinfall_materials import QUINFALL_MATERIALS, get_all_material_names
import json
from pathlib import Path

class Player:
    def __init__(self):
        self.skills = {prof: 1 for prof in Profession}
        self.tools = {tool: 1 for tool in ToolType}
        self.gathering = {g: 1 for g in GatheringProfession}
        self.specializations = {s: 1 for s in Specialization}
        self.tool_types = {prof: "Basic" for prof in Profession}  # Tool type per profession
        self.profession_tool_levels = {prof: 1 for prof in Profession}  # Tool level per profession
        
        # Quinfall Storage System (multi-location support)
        self.storage_system = QuinfallStorageSystem(player_id="default_player")
        
        self.save_path = Path("saves/player.json")
        
    def get_item_count(self, item_name, source="both"):
        """Get item count from inventory, storage, or both"""
        if source == "inventory":
            return self.storage_system.get_item_count(item_name, StorageLocation.PLAYER_INVENTORY)
        elif source == "storage":
            # Get from main storage locations (excluding inventory)
            total = 0
            for location in [StorageLocation.MEADOW_BANK, 
                           StorageLocation.MEADOW_STORAGE,
                           StorageLocation.STARTER_COTTAGE_STORAGE]:
                total += self.storage_system.get_item_count(item_name, location)
            return total
        else:  # both
            return self.storage_system.get_item_count(item_name)  # Total across all locations
    
    def set_item_count(self, item_name, count, location="storage"):
        """Set item count in inventory or storage"""
        if location == "inventory":
            self.storage_system.set_item_count(item_name, count, StorageLocation.PLAYER_INVENTORY)
        elif location == "storage":
            # Set in main bank storage
            self.storage_system.set_item_count(item_name, count, StorageLocation.MEADOW_BANK)
    
    def reset_inventory(self, value=0):
        """Reset all inventory items to specified value (default 0)"""
        self.storage_system.reset_location(StorageLocation.PLAYER_INVENTORY, value)
    
    def reset_storage(self, value=1000):
        """Reset all storage items to specified value (default 1000)"""
        # Reset main storage locations
        for location in [StorageLocation.MEADOW_BANK, 
                        StorageLocation.MEADOW_STORAGE,
                        StorageLocation.STARTER_COTTAGE_STORAGE]:
            self.storage_system.reset_location(location, value)
    
    def can_craft(self, recipe):
        """Check if player has enough materials to craft recipe"""
        for material, needed in recipe.materials.items():
            available = self.get_item_count(material, "both")
            if available < needed:
                return False, f"Not enough {material}: need {needed}, have {available}"
        return True, "Can craft"
    
    def craft_item(self, recipe, quantity=1):
        """Craft item and deduct materials from inventory/storage"""
        # Check if can craft
        can_craft, message = self.can_craft(recipe)
        if not can_craft:
            return False, message
        
        # Check if can craft the requested quantity
        for material, needed_per_craft in recipe.materials.items():
            total_needed = needed_per_craft * quantity
            available = self.get_item_count(material, "both")
            if available < total_needed:
                return False, f"Not enough {material}: need {total_needed}, have {available}"
        
        # Deduct materials (prioritize inventory first, then storage locations)
        for material, needed_per_craft in recipe.materials.items():
            total_needed = needed_per_craft * quantity
            
            # Deduct from inventory first
            inventory_count = self.storage_system.get_item_count(material, StorageLocation.PLAYER_INVENTORY)
            if inventory_count > 0:
                deduct_from_inventory = min(inventory_count, total_needed)
                new_inventory_count = inventory_count - deduct_from_inventory
                self.storage_system.set_item_count(material, new_inventory_count, StorageLocation.PLAYER_INVENTORY)
                total_needed -= deduct_from_inventory
            
            # Deduct remaining from storage locations
            storage_locations = [StorageLocation.MEADOW_BANK, 
                               StorageLocation.MEADOW_STORAGE,
                               StorageLocation.STARTER_COTTAGE_STORAGE]
            
            for location in storage_locations:
                if total_needed <= 0:
                    break
                    
                storage_count = self.storage_system.get_item_count(material, location)
                if storage_count > 0:
                    deduct_from_storage = min(storage_count, total_needed)
                    new_storage_count = storage_count - deduct_from_storage
                    self.storage_system.set_item_count(material, new_storage_count, location)
                    total_needed -= deduct_from_storage
        
        # Add crafted items to storage (prioritize inventory first, then storage)
        crafted_item_name = recipe.name
        current_inventory = self.storage_system.get_item_count(crafted_item_name, StorageLocation.PLAYER_INVENTORY)
        new_inventory_count = current_inventory + quantity
        self.storage_system.set_item_count(crafted_item_name, new_inventory_count, StorageLocation.PLAYER_INVENTORY)
        
        return True, f"Successfully crafted {quantity}x {recipe.name}"
    
    def save(self):
        self.save_path.parent.mkdir(exist_ok=True)
        data = {
            "skills": {p.name: lvl for p, lvl in self.skills.items()},
            "tools": {t.name: lvl for t, lvl in self.tools.items()},
            "tool_types": {p.name: tool_type for p, tool_type in self.tool_types.items()},
            "profession_tool_levels": {p.name: lvl for p, lvl in self.profession_tool_levels.items()}
        }
        self.save_path.write_text(json.dumps(data, indent=2))
        
        # Save storage system separately
        self.storage_system.save()
        
    def load(self):
        if self.save_path.exists():
            data = json.loads(self.save_path.read_text())
            
            # Migrate old profession data
            migrated_skills = {}
            for p, lvl in data["skills"].items():
                if p == "BLACKSMITHING":
                    # Split old BLACKSMITHING into WEAPONSMITH and ARMORSMITH
                    migrated_skills["WEAPONSMITH"] = lvl
                    migrated_skills["ARMORSMITH"] = lvl
                    print(f"Debug: Migrated BLACKSMITHING level {lvl} to both WEAPONSMITH and ARMORSMITH")
                else:
                    migrated_skills[p] = lvl
            
            # Load skills with migration
            self.skills = {}
            for p, lvl in migrated_skills.items():
                try:
                    self.skills[Profession[p]] = lvl
                except KeyError:
                    print(f"Warning: Unknown profession '{p}' in save data, skipping")
            
            # Ensure all current professions have a skill level
            for prof in Profession:
                if prof not in self.skills:
                    self.skills[prof] = 1
            
            # Migrate tool data similarly
            migrated_tools = {}
            for t, lvl in data["tools"].items():
                if t == "BASIC":  # Handle old tool type names if needed
                    continue  # Skip old basic tool type
                migrated_tools[t] = lvl
            
            self.tools = {}
            for t, lvl in migrated_tools.items():
                try:
                    self.tools[ToolType[t]] = lvl
                except KeyError:
                    print(f"Warning: Unknown tool type '{t}' in save data, skipping")
            
            # Ensure all current tools have a level
            for tool in ToolType:
                if tool not in self.tools:
                    self.tools[tool] = 1
            
            # Load tool types if available
            if "tool_types" in data:
                migrated_tool_types = {}
                for p, tool_type in data["tool_types"].items():
                    if p == "BLACKSMITHING":
                        migrated_tool_types["WEAPONSMITH"] = tool_type
                        migrated_tool_types["ARMORSMITH"] = tool_type
                    else:
                        migrated_tool_types[p] = tool_type
                
                self.tool_types = {}
                for p, tool_type in migrated_tool_types.items():
                    try:
                        self.tool_types[Profession[p]] = tool_type
                    except KeyError:
                        print(f"Warning: Unknown profession '{p}' in tool_types, skipping")
            else:
                self.tool_types = {prof: "Basic" for prof in Profession}
            
            # Ensure all current professions have a tool type
            for prof in Profession:
                if prof not in self.tool_types:
                    self.tool_types[prof] = "Basic"
            
            # Load profession tool levels if available
            if "profession_tool_levels" in data:
                migrated_prof_tool_levels = {}
                for p, lvl in data["profession_tool_levels"].items():
                    if p == "BLACKSMITHING":
                        migrated_prof_tool_levels["WEAPONSMITH"] = lvl
                        migrated_prof_tool_levels["ARMORSMITH"] = lvl
                    else:
                        migrated_prof_tool_levels[p] = lvl
                
                self.profession_tool_levels = {}
                for p, lvl in migrated_prof_tool_levels.items():
                    try:
                        self.profession_tool_levels[Profession[p]] = lvl
                    except KeyError:
                        print(f"Warning: Unknown profession '{p}' in profession_tool_levels, skipping")
            else:
                self.profession_tool_levels = {prof: 1 for prof in Profession}
            
            # Ensure all current professions have a tool level
            for prof in Profession:
                if prof not in self.profession_tool_levels:
                    self.profession_tool_levels[prof] = 1
        else:
            # Initialize defaults for new player
            self.reset_inventory(0)
            self.reset_storage(1000)
        
        # Load storage system
        self.storage_system.load()
