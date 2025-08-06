from PySide6.QtWidgets import QTabWidget
from ui.crafting_tab import CraftingTab
from ui.crafting_tab_improved import ImprovedCraftingTab
from ui.gathering_tab import GatheringTab
from ui.specialization_tab import SpecializationTab

class MainTabs(QTabWidget):
    def __init__(self, player=None):
        super().__init__()
        self.setMovable(True)
        self.player = player
        self.addTab(ImprovedCraftingTab(player), "Crafting")
        self.addTab(GatheringTab(), "Gathering")
        self.addTab(SpecializationTab(), "Specializations")
    
    def refresh_data(self):
        """Refresh data in all tabs that support it"""
        for i in range(self.count()):
            tab = self.widget(i)
            if hasattr(tab, 'load_profession_levels'):
                tab.load_profession_levels()
            elif hasattr(tab, 'load_profession_skill'):
                tab.load_profession_skill()
            elif hasattr(tab, 'update_display'):
                tab.update_display()
