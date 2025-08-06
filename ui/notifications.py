"""
Version change notification system for Quinfall Companion
"""
from PySide6.QtWidgets import QMessageBox

class RecipeUpdateNotifier:
    def __init__(self, parent):
        self.parent = parent
    
    def show_update_alert(self, changes):
        """Show alert for recipe version changes"""
        msg = QMessageBox(self.parent)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Recipe Updated")
        
        # Format change details
        details = []
        if changes.get('materials'):
            details.append("Material changes:")
            for mat, change in changes['materials'].items():
                details.append(f"- {mat}: {change['action']}")
        
        if changes.get('output_stats'):
            details.append("\nStat changes:")
            for stat, change in changes['output_stats'].items():
                details.append(f"- {stat}: {change['action']}")
        
        msg.setText("A recipe you use has been updated")
        msg.setDetailedText("\n".join(details))
        msg.exec_()
