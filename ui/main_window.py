from PySide6.QtWidgets import QTabWidget
from ui.crafting_tab_improved import ImprovedCraftingTab
from ui.gathering_tab import GatheringTab
from ui.specialization_tab import SpecializationTab

class MainTabs(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setMovable(True)
        self.addTab(ImprovedCraftingTab(), "Crafting")
        self.addTab(GatheringTab(), "Gathering")
        self.addTab(SpecializationTab(), "Specializations")
