from enum import Enum, auto

class Profession(Enum):
    # CRAFTING PROFESSIONS (July 2025 Quinfall System)
    ALCHEMY = auto()
    COOKING = auto()  # Chef in Quinfall
    WEAPONSMITH = auto()  # Split from Blacksmithing
    ARMORSMITH = auto()   # Split from Blacksmithing
    WOODWORKING = auto()  # Carpenter/Woodworker
    TAILORING = auto()    # Clothing and fabric crafting
    JEWELCRAFTING = auto()
    ENCHANTING = auto()
    INSCRIPTION = auto()
    
    # GATHERING PROFESSIONS (July 2025 Quinfall System) - These DON'T have crafting recipes
    MINING = auto()
    LUMBERJACK = auto()  # Tree cutting (gathering only)
    HARVESTER = auto()   # Plant gathering
    FISHING = auto()
    HUNTER = auto()      # Animal hunting
    ANIMAL_KEEPER = auto()  # New Quinfall profession
    BEEKEEPER = auto()      # New July 2025 profession
    
    # SPECIALIZATION PROFESSIONS (July 2025 Quinfall System)
    TRADING = auto()
    SHIPBUILDING = auto()
    TREASURE_HUNTER = auto()  # New Quinfall profession
    WORKER = auto()           # New Quinfall profession
    TRAVELER = auto()         # New Quinfall profession

class ProfessionCategory(Enum):
    CRAFTING = auto()
    GATHERING = auto() 
    SPECIALIZATION = auto()

class ProfessionTier(Enum):
    APPRENTICE = 1
    JOURNEYMAN = 10
    MASTER = 20

class ToolType(Enum):
    # Crafting Tools
    FORGE = "Forge"                    # For Weaponsmith
    ANVIL = "Anvil"                    # For Armorsmith  
    ALCHEMY_TABLE = "Alchemy Table"    # For Alchemy
    COOKING_STATION = "Cooking Station" # For Cooking/Chef
    WORKBENCH = "Workbench"            # For Woodworking
    JEWELING_TABLE = "Jeweling Table"  # For Jewelcrafting
    ENCHANTING_TABLE = "Enchanting Table" # For Enchanting
    SHIPYARD = "Shipyard"              # For Shipbuilding
    DOCK = "Dock"                      # Alternative shipbuilding location
    LOOM = "Loom"                      # For Tailoring
    # Gathering Tools
    PICKAXE = "Pickaxe"                # For Mining
    AXE = "Axe"                        # For Lumberjack
    SICKLE = "Sickle"                  # For Harvester
    FISHING_ROD = "Fishing Rod"        # For Fishing
    HUNTING_BOW = "Hunting Bow"        # For Hunter
    ANIMAL_TOOLS = "Animal Tools"      # For Animal Keeper
    BEEKEEPING_TOOLS = "Beekeeping Tools"  # For Beekeeper
    # Specialization Tools
    TRADING_CART = "Trading Cart"      # For Trading
    TREASURE_MAP = "Treasure Map"      # For Treasure Hunter
    WORK_TOOLS = "Work Tools"          # For Worker
    TRAVEL_GEAR = "Travel Gear"        # For Traveler

class GatheringProfession(Enum):
    MINING = auto()
    LUMBERJACK = auto()  # Renamed from LOGGING
    HARVESTER = auto()   # Renamed from HERBALISM  
    FISHING = auto()
    HUNTER = auto()      # Renamed from HUNTING
    ANIMAL_KEEPER = auto()  # New Quinfall profession
    BEEKEEPER = auto()      # New July 2025 profession

class Specialization(Enum):
    TRADING = auto()
    SHIPBUILDING = auto()
    ARCHITECTURE = auto()
    ENGINEERING = auto()
    TAILORING = auto()

class Recipe:
    def __init__(self, name: str, profession: Profession, tier: ProfessionTier, 
                 materials: dict, tool: ToolType, tool_level: int, skill_level: int):
        self.name = name
        self.profession = profession
        self.tier = tier
        self.materials = materials
        self.required_tool = tool
        self.tool_level = tool_level
        self.skill_level = skill_level
