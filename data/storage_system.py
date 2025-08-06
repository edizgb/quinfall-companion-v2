#!/usr/bin/env python3
"""
Quinfall Multi-Location Storage System
Supports inventory, storage in different cities, houses, etc.
Prepared for future API integration with real player data.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json
from pathlib import Path
from .quinfall_materials import QuinfallMaterial, QUINFALL_MATERIALS
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class StorageType(Enum):
    """Types of storage locations in Quinfall"""
    INVENTORY = "inventory"           # Player inventory (carried items)
    BANK = "bank"                    # Main bank storage
    CITY_STORAGE = "city_storage"    # City-specific storage
    HOUSE_STORAGE = "house_storage"  # Player house storage
    GUILD_STORAGE = "guild_storage"  # Guild storage
    TEMP_STORAGE = "temp_storage"    # Temporary storage (crafting, etc.)

class StorageLocation(Enum):
    """All storage locations in Quinfall - Based on authentic Fandom Wiki data"""
    # Player inventory
    PLAYER_INVENTORY = "player_inventory"
    
    # === AUTHENTIC QUINFALL CITIES (from Fandom Wiki) ===
    # Major cities with full services (banks, markets, storage)
    MEADOW_BANK = "meadow_bank"
    MEADOW_STORAGE = "meadow_storage"
    
    KINEALLEN_BANK = "kineallen_bank"
    KINEALLEN_STORAGE = "kineallen_storage"
    
    MREAFALL_BANK = "mreafall_bank"
    MREAFALL_STORAGE = "mreafall_storage"
    
    REASYA_BANK = "reasya_bank"
    REASYA_STORAGE = "reasya_storage"
    
    HORUS_BANK = "horus_bank"
    HORUS_STORAGE = "horus_storage"
    
    CALMNAROCK_BANK = "calmnarock_bank"
    CALMNAROCK_STORAGE = "calmnarock_storage"
    
    LARCBOST_BANK = "larcbost_bank"
    LARCBOST_STORAGE = "larcbost_storage"
    
    NEARON_BANK = "nearon_bank"
    NEARON_STORAGE = "nearon_storage"
    
    PABAS_BANK = "pabas_bank"
    PABAS_STORAGE = "pabas_storage"
    
    RUNE_MOUND_BANK = "rune_mound_bank"
    RUNE_MOUND_STORAGE = "rune_mound_storage"
    
    SHADOW_ATOLL_BANK = "shadow_atoll_bank"
    SHADOW_ATOLL_STORAGE = "shadow_atoll_storage"
    
    # === PLAYER HOUSING (Expandable) ===
    STARTER_COTTAGE_STORAGE = "starter_cottage_storage"
    MEDIUM_HOUSE_STORAGE = "medium_house_storage"
    LARGE_MANOR_STORAGE = "large_manor_storage"
    ESTATE_STORAGE = "estate_storage"
    
    # === GUILD STORAGE ===
    GUILD_HALL_STORAGE = "guild_hall_storage"
    GUILD_WAREHOUSE = "guild_warehouse"
    
    # === SPECIAL/TEMPORARY STORAGE ===
    CARAVAN_STORAGE = "caravan_storage"
    SHIP_STORAGE = "ship_storage"
    TEMPORARY_CAMP_STORAGE = "temporary_camp_storage"                # Premium housing
    
    # Guild Locations
    GUILD_TREASURY = "guild_treasury"                            # Guild valuable storage
    
    # Special Locations
    CRAFTING_STATION_TEMP = "crafting_station_temp"              # Temporary crafting storage
    MARKET_TEMP_STORAGE = "market_temp_storage"                  # Market transaction storage
    AUCTION_HOUSE_STORAGE = "auction_house_storage"              # Auction house storage

@dataclass
class StorageContainer:
    """Represents a storage container at a specific location"""
    location: StorageLocation
    storage_type: StorageType
    capacity: int = 200  # Player-configurable storage slots (default 200)
    max_capacity: int = 1000  # Maximum possible slots (upgradeable)
    weight_limit: float = 10000.0  # Maximum weight
    items: Dict[str, int] = field(default_factory=dict)  # material_id -> quantity
    
    # Player configuration
    unlocked_slots: int = 200  # Currently unlocked slots (player can configure)
    
    # API Integration fields (for future use)
    api_container_id: Optional[str] = None
    game_container_id: Optional[int] = None
    last_sync: Optional[str] = None  # ISO timestamp of last API sync
    last_api_sync: Optional[str] = None
    api_sync_hash: Optional[str] = None
    
    def get_item_count(self, material_id: str) -> int:
        """Get quantity of specific material in this container"""
        return self.items.get(material_id, 0)
    
    def set_item_count(self, material_id: str, quantity: int):
        """Set quantity of specific material in this container"""
        if quantity <= 0:
            self.items.pop(material_id, None)
        else:
            self.items[material_id] = quantity
    
    def add_items(self, material_id: str, quantity: int) -> bool:
        """Add items to container. Returns True if successful."""
        if not self.can_add_items(material_id, quantity):
            return False
        
        current = self.items.get(material_id, 0)
        self.items[material_id] = current + quantity
        return True
    
    def remove_items(self, material_id: str, quantity: int) -> bool:
        """Remove items from container. Returns True if successful."""
        current = self.items.get(material_id, 0)
        if current < quantity:
            return False
        
        if current == quantity:
            self.items.pop(material_id, None)
        else:
            self.items[material_id] = current - quantity
        return True
    
    def can_add_items(self, material_id: str, quantity: int) -> bool:
        """Check if items can be added to container"""
        # Check unlocked slots capacity
        total_items = sum(self.items.values()) + quantity
        if total_items > self.unlocked_slots:
            return False
        
        # Check weight limit
        material = QUINFALL_MATERIALS.get(material_id)
        if material:
            current_weight = self.get_total_weight()
            additional_weight = material.weight * quantity
            if current_weight + additional_weight > self.weight_limit:
                return False
        
        return True
    
    def get_total_weight(self) -> float:
        """Calculate total weight of items in container"""
        total_weight = 0.0
        for material_id, quantity in self.items.items():
            material = QUINFALL_MATERIALS.get(material_id)
            if material:
                total_weight += material.weight * quantity
        return total_weight
    
    def get_total_items(self) -> int:
        """Get total number of items in container"""
        return sum(self.items.values())
    
    def is_full(self) -> bool:
        """Check if container is at unlocked capacity"""
        return self.get_total_items() >= self.unlocked_slots
    
    def get_free_space(self) -> int:
        """Get remaining unlocked capacity"""
        return self.unlocked_slots - self.get_total_items()
    
    def can_unlock_slots(self, additional_slots: int) -> bool:
        """Check if additional slots can be unlocked"""
        return (self.unlocked_slots + additional_slots) <= self.max_capacity
    
    def unlock_slots(self, additional_slots: int) -> bool:
        """Unlock additional storage slots"""
        if self.can_unlock_slots(additional_slots):
            self.unlocked_slots += additional_slots
            return True
        return False
    
    def set_unlocked_slots(self, slots: int) -> bool:
        """Set specific number of unlocked slots"""
        if 0 <= slots <= self.max_capacity:
            self.unlocked_slots = slots
            return True
        return False
    
    def get_slot_info(self) -> Dict[str, int]:
        """Get slot information"""
        return {
            "unlocked_slots": self.unlocked_slots,
            "max_capacity": self.max_capacity,
            "used_slots": self.get_total_items(),
            "free_slots": self.get_free_space(),
            "upgradeable_slots": self.max_capacity - self.unlocked_slots
        }

class QuinfallStorageSystem:
    """Complete storage system for Quinfall companion app"""
    
    def __init__(self, player_id: str = "default_player"):
        self.player_id = player_id
        self.containers: Dict[StorageLocation, StorageContainer] = {}
        self.save_path = Path(f"saves/storage_{player_id}.json")
        
        # Initialize default containers
        self._initialize_default_containers()
    
    def _initialize_default_containers(self):
        """Initialize default storage containers with authentic Quinfall cities"""
        # Player inventory (limited, upgradeable)
        self.containers[StorageLocation.PLAYER_INVENTORY] = StorageContainer(
            location=StorageLocation.PLAYER_INVENTORY,
            storage_type=StorageType.INVENTORY,
            capacity=200,  # Default unlocked slots
            max_capacity=500,  # Maximum possible inventory slots
            unlocked_slots=200,
            weight_limit=5000.0
        )
        
        # === AUTHENTIC QUINFALL CITIES (from Fandom Wiki) ===
        # Major cities with banks and storage (where markets exist)
        
        # Meadow - Major city
        self.containers[StorageLocation.MEADOW_BANK] = StorageContainer(
            location=StorageLocation.MEADOW_BANK,
            storage_type=StorageType.BANK,
            capacity=200,
            max_capacity=1000,  # Major city - high capacity
            unlocked_slots=200,
            weight_limit=50000.0
        )
        self.containers[StorageLocation.MEADOW_STORAGE] = StorageContainer(
            location=StorageLocation.MEADOW_STORAGE,
            storage_type=StorageType.CITY_STORAGE,
            capacity=200,
            max_capacity=800,
            unlocked_slots=200,
            weight_limit=40000.0
        )
        
        # Kineallen - Major city
        self.containers[StorageLocation.KINEALLEN_BANK] = StorageContainer(
            location=StorageLocation.KINEALLEN_BANK,
            storage_type=StorageType.BANK,
            capacity=200,
            max_capacity=1000,
            unlocked_slots=200,
            weight_limit=50000.0
        )
        self.containers[StorageLocation.KINEALLEN_STORAGE] = StorageContainer(
            location=StorageLocation.KINEALLEN_STORAGE,
            storage_type=StorageType.CITY_STORAGE,
            capacity=200,
            max_capacity=800,
            unlocked_slots=200,
            weight_limit=40000.0
        )
        
        # Mreafall - Major city
        self.containers[StorageLocation.MREAFALL_BANK] = StorageContainer(
            location=StorageLocation.MREAFALL_BANK,
            storage_type=StorageType.BANK,
            capacity=200,
            max_capacity=1000,
            unlocked_slots=200,
            weight_limit=50000.0
        )
        self.containers[StorageLocation.MREAFALL_STORAGE] = StorageContainer(
            location=StorageLocation.MREAFALL_STORAGE,
            storage_type=StorageType.CITY_STORAGE,
            capacity=200,
            max_capacity=800,
            unlocked_slots=200,
            weight_limit=40000.0
        )
        
        # Reasya - Major city
        self.containers[StorageLocation.REASYA_BANK] = StorageContainer(
            location=StorageLocation.REASYA_BANK,
            storage_type=StorageType.BANK,
            capacity=200,
            max_capacity=900,
            unlocked_slots=200,
            weight_limit=45000.0
        )
        self.containers[StorageLocation.REASYA_STORAGE] = StorageContainer(
            location=StorageLocation.REASYA_STORAGE,
            storage_type=StorageType.CITY_STORAGE,
            capacity=200,
            max_capacity=700,
            unlocked_slots=200,
            weight_limit=35000.0
        )
        
        # Horus - Major city
        self.containers[StorageLocation.HORUS_BANK] = StorageContainer(
            location=StorageLocation.HORUS_BANK,
            storage_type=StorageType.BANK,
            capacity=200,
            max_capacity=900,
            unlocked_slots=200,
            weight_limit=45000.0
        )
        self.containers[StorageLocation.HORUS_STORAGE] = StorageContainer(
            location=StorageLocation.HORUS_STORAGE,
            storage_type=StorageType.CITY_STORAGE,
            capacity=200,
            max_capacity=700,
            unlocked_slots=200,
            weight_limit=35000.0
        )
        
        # Calmnarock - Secondary city
        self.containers[StorageLocation.CALMNAROCK_BANK] = StorageContainer(
            location=StorageLocation.CALMNAROCK_BANK,
            storage_type=StorageType.BANK,
            capacity=200,
            max_capacity=800,
            unlocked_slots=200,
            weight_limit=40000.0
        )
        self.containers[StorageLocation.CALMNAROCK_STORAGE] = StorageContainer(
            location=StorageLocation.CALMNAROCK_STORAGE,
            storage_type=StorageType.CITY_STORAGE,
            capacity=200,
            max_capacity=600,
            unlocked_slots=200,
            weight_limit=30000.0
        )
        
        # Larcbost - Secondary city
        self.containers[StorageLocation.LARCBOST_BANK] = StorageContainer(
            location=StorageLocation.LARCBOST_BANK,
            storage_type=StorageType.BANK,
            capacity=200,
            max_capacity=800,
            unlocked_slots=200,
            weight_limit=40000.0
        )
        self.containers[StorageLocation.LARCBOST_STORAGE] = StorageContainer(
            location=StorageLocation.LARCBOST_STORAGE,
            storage_type=StorageType.CITY_STORAGE,
            capacity=200,
            max_capacity=600,
            unlocked_slots=200,
            weight_limit=30000.0
        )
        
        # Nearon - Secondary city
        self.containers[StorageLocation.NEARON_BANK] = StorageContainer(
            location=StorageLocation.NEARON_BANK,
            storage_type=StorageType.BANK,
            capacity=200,
            max_capacity=700,
            unlocked_slots=200,
            weight_limit=35000.0
        )
        self.containers[StorageLocation.NEARON_STORAGE] = StorageContainer(
            location=StorageLocation.NEARON_STORAGE,
            storage_type=StorageType.CITY_STORAGE,
            capacity=200,
            max_capacity=500,
            unlocked_slots=200,
            weight_limit=25000.0
        )
        
        # Pabas - Secondary city
        self.containers[StorageLocation.PABAS_BANK] = StorageContainer(
            location=StorageLocation.PABAS_BANK,
            storage_type=StorageType.BANK,
            capacity=200,
            max_capacity=700,
            unlocked_slots=200,
            weight_limit=35000.0
        )
        self.containers[StorageLocation.PABAS_STORAGE] = StorageContainer(
            location=StorageLocation.PABAS_STORAGE,
            storage_type=StorageType.CITY_STORAGE,
            capacity=200,
            max_capacity=500,
            unlocked_slots=200,
            weight_limit=25000.0
        )
        
        # Rune Mound - Specialized location
        self.containers[StorageLocation.RUNE_MOUND_BANK] = StorageContainer(
            location=StorageLocation.RUNE_MOUND_BANK,
            storage_type=StorageType.BANK,
            capacity=200,
            max_capacity=600,
            unlocked_slots=200,
            weight_limit=30000.0
        )
        self.containers[StorageLocation.RUNE_MOUND_STORAGE] = StorageContainer(
            location=StorageLocation.RUNE_MOUND_STORAGE,
            storage_type=StorageType.CITY_STORAGE,
            capacity=200,
            max_capacity=400,
            unlocked_slots=200,
            weight_limit=20000.0
        )
        
        # Shadow Atoll - Specialized location
        self.containers[StorageLocation.SHADOW_ATOLL_BANK] = StorageContainer(
            location=StorageLocation.SHADOW_ATOLL_BANK,
            storage_type=StorageType.BANK,
            capacity=200,
            max_capacity=600,
            unlocked_slots=200,
            weight_limit=30000.0
        )
        self.containers[StorageLocation.SHADOW_ATOLL_STORAGE] = StorageContainer(
            location=StorageLocation.SHADOW_ATOLL_STORAGE,
            storage_type=StorageType.CITY_STORAGE,
            capacity=200,
            max_capacity=400,
            unlocked_slots=200,
            weight_limit=20000.0
        )
        
        # === PLAYER HOUSING (Expandable) ===
        self.containers[StorageLocation.STARTER_COTTAGE_STORAGE] = StorageContainer(
            location=StorageLocation.STARTER_COTTAGE_STORAGE,
            storage_type=StorageType.HOUSE_STORAGE,
            capacity=200,
            max_capacity=400,
            unlocked_slots=200,
            weight_limit=15000.0
        )
        
        self.containers[StorageLocation.MEDIUM_HOUSE_STORAGE] = StorageContainer(
            location=StorageLocation.MEDIUM_HOUSE_STORAGE,
            storage_type=StorageType.HOUSE_STORAGE,
            capacity=200,
            max_capacity=600,
            unlocked_slots=200,
            weight_limit=25000.0
        )
        
        self.containers[StorageLocation.LARGE_MANOR_STORAGE] = StorageContainer(
            location=StorageLocation.LARGE_MANOR_STORAGE,
            storage_type=StorageType.HOUSE_STORAGE,
            capacity=200,
            max_capacity=800,
            unlocked_slots=200,
            weight_limit=35000.0
        )
        
        self.containers[StorageLocation.ESTATE_STORAGE] = StorageContainer(
            location=StorageLocation.ESTATE_STORAGE,
            storage_type=StorageType.HOUSE_STORAGE,
            capacity=200,
            max_capacity=1000,
            unlocked_slots=200,
            weight_limit=45000.0
        )
        
        # === GUILD STORAGE ===
        self.containers[StorageLocation.GUILD_HALL_STORAGE] = StorageContainer(
            location=StorageLocation.GUILD_HALL_STORAGE,
            storage_type=StorageType.GUILD_STORAGE,
            capacity=200,
            max_capacity=1200,
            unlocked_slots=200,
            weight_limit=60000.0
        )
        
        self.containers[StorageLocation.GUILD_WAREHOUSE] = StorageContainer(
            location=StorageLocation.GUILD_WAREHOUSE,
            storage_type=StorageType.GUILD_STORAGE,
            capacity=200,
            max_capacity=1500,
            unlocked_slots=200,
            weight_limit=75000.0
        )
    
    def get_container(self, location: StorageLocation) -> Optional[StorageContainer]:
        """Get storage container at specific location"""
        return self.containers.get(location)
    
    def get_item_count(self, material_id: str, location: Optional[StorageLocation] = None) -> int:
        """Get item count at specific location or total across all locations"""
        if location:
            container = self.containers.get(location)
            return container.get_item_count(material_id) if container else 0
        else:
            # Return total across all containers
            total = 0
            for container in self.containers.values():
                total += container.get_item_count(material_id)
            return total
    
    def set_item_count(self, material_id: str, quantity: int, location: StorageLocation):
        """Set item count at specific location"""
        container = self.containers.get(location)
        if container:
            container.set_item_count(material_id, quantity)
    
    def move_items(self, material_id: str, quantity: int, 
                   from_location: StorageLocation, 
                   to_location: StorageLocation) -> bool:
        """Move items between storage locations"""
        from_container = self.containers.get(from_location)
        to_container = self.containers.get(to_location)
        
        if not from_container or not to_container:
            return False
        
        # Check if source has enough items
        if from_container.get_item_count(material_id) < quantity:
            return False
        
        # Check if destination can accept items
        if not to_container.can_add_items(material_id, quantity):
            return False
        
        # Perform the move
        if from_container.remove_items(material_id, quantity):
            if to_container.add_items(material_id, quantity):
                return True
            else:
                # Rollback if destination add failed
                from_container.add_items(material_id, quantity)
        
        return False
    
    def reset_location(self, location: StorageLocation, default_value: int = 0):
        """Reset all items at a location to default value"""
        container = self.containers.get(location)
        if container:
            if default_value == 0:
                container.items.clear()
            else:
                # Set all known materials to default value
                for material_id in QUINFALL_MATERIALS.keys():
                    container.set_item_count(material_id, default_value)
    
    def reset_all_storage(self, inventory_value: int = 0, storage_value: int = 1000):
        """Reset all storage locations to default values"""
        for location, container in self.containers.items():
            if container.storage_type == StorageType.INVENTORY:
                self.reset_location(location, inventory_value)
            else:
                self.reset_location(location, storage_value)
    
    def get_storage_summary(self) -> Dict[str, Any]:
        """Get summary of all storage locations"""
        summary = {}
        for location, container in self.containers.items():
            summary[location.value] = {
                "type": container.storage_type.value,
                "total_items": container.get_total_items(),
                "capacity": container.capacity,
                "total_weight": container.get_total_weight(),
                "weight_limit": container.weight_limit,
                "free_space": container.get_free_space(),
                "unique_materials": len(container.items)
            }
        return summary
    
    def find_material_locations(self, material_id: str) -> Dict[StorageLocation, int]:
        """Find all locations where a material is stored"""
        locations = {}
        for location, container in self.containers.items():
            count = container.get_item_count(material_id)
            if count > 0:
                locations[location] = count
        return locations
    
    def save(self):
        """Save storage data to file"""
        self.save_path.parent.mkdir(exist_ok=True)
        
        data = {
            "player_id": self.player_id,
            "containers": {}
        }
        
        for location, container in self.containers.items():
            data["containers"][location.value] = {
                "storage_type": container.storage_type.value,
                "capacity": container.capacity,
                "weight_limit": container.weight_limit,
                "items": container.items,
                "api_container_id": container.api_container_id,
                "game_container_id": container.game_container_id,
                "last_sync": container.last_sync
            }
        
        with open(self.save_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load storage data from file"""
        if not self.save_path.exists():
            return
        
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
            
            self.player_id = data.get("player_id", "default_player")
            
            # Load containers
            for location_str, container_data in data.get("containers", {}).items():
                try:
                    location = StorageLocation(location_str)
                    storage_type = StorageType(container_data["storage_type"])
                    
                    container = StorageContainer(
                        location=location,
                        storage_type=storage_type,
                        capacity=container_data.get("capacity", 1000),
                        weight_limit=container_data.get("weight_limit", 10000.0),
                        items=container_data.get("items", {}),
                        api_container_id=container_data.get("api_container_id"),
                        game_container_id=container_data.get("game_container_id"),
                        last_sync=container_data.get("last_sync")
                    )
                    
                    self.containers[location] = container
                except ValueError:
                    # Skip unknown locations/types
                    continue
                    
        except Exception as e:
            print(f"Error loading storage data: {e}")
    
    def sync_with_api(self, api_client=None):
        """
        Sync storage data with Quinfall API
        
        Args:
            api_client: QuinfallAPIClient instance (optional, will create if None)
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Import API client
            from utils.quinfall_api import QuinfallAPIClient, create_api_client
            
            # Use provided client or create new one
            if api_client is None:
                api_client = create_api_client()
            
            if not api_client.is_authenticated():
                return False, "❌ API client not authenticated. Please configure API credentials."
            
            logger.info(f"🔄 Starting API sync for player: {self.player_id}")
            
            # Perform the sync
            success, message = api_client.sync_storage_with_game(self)
            
            if success:
                logger.info(f"✅ API sync completed: {message}")
                return True, message
            else:
                logger.error(f"❌ API sync failed: {message}")
                return False, message
                
        except ImportError:
            logger.warning("⚠️ API client not available - running in offline mode")
            return False, "⚠️ API sync not available - running in offline mode"
        except Exception as e:
            logger.error(f"❌ API sync error: {e}")
            return False, f"❌ API sync failed: {str(e)}"
    
    def to_api_format(self) -> Dict[str, Any]:
        """
        Convert storage system to API-compatible format
        
        Returns:
            Dict: Storage data in API format
        """
        api_data = {
            'player_id': self.player_id,
            'containers': {},
            'last_updated': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        for location, container in self.containers.items():
            api_data['containers'][location.value] = {
                'location': location.value,
                'storage_type': container.storage_type.value,
                'capacity': container.capacity,
                'max_capacity': container.max_capacity,
                'weight_limit': container.weight_limit,
                'unlocked_slots': container.unlocked_slots,
                'items': container.items.copy(),
                'last_synced': container.last_api_sync,
                'sync_hash': container.api_sync_hash
            }
        
        return api_data
    
    def from_api_format(self, api_data: Dict[str, Any]) -> bool:
        """
        Update storage system from API data format
        
        Args:
            api_data: Storage data from API
        
        Returns:
            bool: Success status
        """
        try:
            containers_data = api_data.get('containers', {})
            
            for location_name, container_data in containers_data.items():
                try:
                    location = StorageLocation(location_name)
                    container = self.get_container(location)
                    
                    # Update container data
                    container.capacity = container_data.get('capacity', container.capacity)
                    container.max_capacity = container_data.get('max_capacity', container.max_capacity)
                    container.weight_limit = container_data.get('weight_limit', container.weight_limit)
                    container.unlocked_slots = container_data.get('unlocked_slots', container.unlocked_slots)
                    
                    # Update items
                    api_items = container_data.get('items', {})
                    container.items.clear()
                    container.items.update(api_items)
                    
                    # Update sync metadata
                    container.last_api_sync = container_data.get('last_synced')
                    container.api_sync_hash = container_data.get('sync_hash')
                    
                except ValueError:
                    logger.warning(f"⚠️ Unknown storage location in API data: {location_name}")
                    continue
            
            logger.info("✅ Storage system updated from API data")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update from API data: {e}")
            return False
