from PySide6.QtWidgets import (QMainWindow, QApplication, QWidget, QScrollArea, 
                               QVBoxLayout, QMenuBar, QMenu, QStatusBar, QMessageBox,
                               QSystemTrayIcon, QLabel, QHBoxLayout, QPushButton)
from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QAction, QIcon
from ui.main_window import MainTabs
from ui.api_settings_dialog import APISettingsDialog
from data.player import Player
import logging
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompanionApp(QMainWindow):
    """
    Main Quinfall Companion Application
    Enhanced with API sync functionality and proper menu system
    """
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1000, 700)  # Increased for better API integration UI
        self.setWindowTitle("Quinfall Companion - Enhanced with API Sync")
        
        # Initialize player data
        self.player = Player()
        self.player.load()
        
        # API sync timer
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.auto_sync)
        
        # Initialize UI
        self.init_ui()
        self.init_menu_bar()
        self.init_status_bar()
        
        # Load API settings and start auto-sync if enabled
        self.load_api_settings()
        
        logger.info("🚀 Quinfall Companion started with API sync support")
    
    def init_ui(self):
        """Initialize the main user interface"""
        # Central widget with layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        central_widget.setLayout(QVBoxLayout())
        central_widget.layout().addWidget(scroll)
        
        # Content container
        content = QWidget()
        scroll.setWidget(content)
        self.main_layout = QVBoxLayout(content)
        
        # API status bar at top
        self.api_status_widget = self.create_api_status_widget()
        self.main_layout.addWidget(self.api_status_widget)
        
        # Main tabs with player data
        self.tabs = MainTabs()
        # Pass player data to tabs that need it
        if hasattr(self.tabs, 'set_player'):
            self.tabs.set_player(self.player)
        
        self.main_layout.addWidget(self.tabs)
        self.show()
    
    def create_api_status_widget(self):
        """Create API status widget for the top of the application"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # API status label
        self.api_status_label = QLabel("🔌 API: Not connected")
        self.api_status_label.setStyleSheet("color: #666; font-weight: bold;")
        layout.addWidget(self.api_status_label)
        
        layout.addStretch()
        
        # Quick sync button
        self.quick_sync_button = QPushButton("🔄 Quick Sync")
        self.quick_sync_button.setMaximumWidth(120)
        self.quick_sync_button.clicked.connect(self.quick_sync)
        self.quick_sync_button.setEnabled(False)  # Disabled until API is configured
        layout.addWidget(self.quick_sync_button)
        
        # API settings button
        api_settings_button = QPushButton("⚙️ API Settings")
        api_settings_button.setMaximumWidth(120)
        api_settings_button.clicked.connect(self.open_api_settings)
        layout.addWidget(api_settings_button)
        
        widget.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-bottom: 1px solid #ccc;
            }
            QPushButton {
                padding: 5px 10px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #f5f5f5;
                color: #999;
            }
        """)
        
        return widget
    
    def init_menu_bar(self):
        """Initialize the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("📁 File")
        
        save_action = QAction("💾 Save Player Data", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_player_data)
        file_menu.addAction(save_action)
        
        load_action = QAction("📂 Load Player Data", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_player_data)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # API menu
        api_menu = menubar.addMenu("🌐 API Sync")
        
        api_settings_action = QAction("⚙️ API Settings", self)
        api_settings_action.triggered.connect(self.open_api_settings)
        api_menu.addAction(api_settings_action)
        
        api_menu.addSeparator()
        
        sync_now_action = QAction("🔄 Sync Now", self)
        sync_now_action.setShortcut("F5")
        sync_now_action.triggered.connect(self.quick_sync)
        api_menu.addAction(sync_now_action)
        
        toggle_auto_sync_action = QAction("⏰ Toggle Auto-Sync", self)
        toggle_auto_sync_action.setCheckable(True)
        toggle_auto_sync_action.triggered.connect(self.toggle_auto_sync)
        api_menu.addAction(toggle_auto_sync_action)
        self.auto_sync_action = toggle_auto_sync_action
        
        api_menu.addSeparator()
        
        connection_status_action = QAction("📊 Connection Status", self)
        connection_status_action.triggered.connect(self.show_connection_status)
        api_menu.addAction(connection_status_action)
        
        # Help menu
        help_menu = menubar.addMenu("❓ Help")
        
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        api_help_action = QAction("🔗 API Documentation", self)
        api_help_action.triggered.connect(self.show_api_help)
        help_menu.addAction(api_help_action)
    
    def init_status_bar(self):
        """Initialize the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status labels
        self.status_bar.addWidget(QLabel("Ready"))
        self.status_bar.addPermanentWidget(QLabel("Player: " + self.player.storage_system.player_id))
    
    def load_api_settings(self):
        """Load API settings and configure auto-sync"""
        try:
            settings_file = Path("saves/api_settings.json")
            if settings_file.exists():
                import json
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                
                # Configure auto-sync
                if settings.get('auto_sync_enabled', False):
                    interval = settings.get('sync_interval', 5) * 60000  # Convert to milliseconds
                    self.sync_timer.start(interval)
                    self.auto_sync_action.setChecked(True)
                    self.api_status_label.setText("🔄 API: Auto-sync enabled")
                    self.quick_sync_button.setEnabled(True)
                    
                    # Sync on startup if enabled
                    if settings.get('sync_on_startup', False):
                        QTimer.singleShot(2000, self.quick_sync)  # Delay 2 seconds after startup
                
        except Exception as e:
            logger.warning(f"Could not load API settings: {e}")
    
    def save_player_data(self):
        """Save player data"""
        try:
            self.player.save()
            self.status_bar.showMessage("Player data saved successfully", 3000)
            logger.info("💾 Player data saved")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save player data: {str(e)}")
            logger.error(f"Failed to save player data: {e}")
    
    def load_player_data(self):
        """Load player data"""
        try:
            self.player.load()
            self.status_bar.showMessage("Player data loaded successfully", 3000)
            logger.info("📂 Player data loaded")
            
            # Refresh UI if needed
            if hasattr(self.tabs, 'refresh_data'):
                self.tabs.refresh_data()
                
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load player data: {str(e)}")
            logger.error(f"Failed to load player data: {e}")
    
    def open_api_settings(self):
        """Open API settings dialog"""
        dialog = APISettingsDialog(self)
        dialog.exec()
        
        # Reload settings after dialog closes
        self.load_api_settings()
    
    def quick_sync(self):
        """Perform quick storage sync"""
        try:
            self.quick_sync_button.setEnabled(False)
            self.api_status_label.setText("🔄 API: Syncing...")
            self.status_bar.showMessage("Syncing with Quinfall API...")
            
            # Perform sync
            success, message = self.player.storage_system.sync_with_api()
            
            if success:
                self.api_status_label.setText("✅ API: Sync successful")
                self.status_bar.showMessage("Sync completed successfully", 5000)
                logger.info(f"✅ Quick sync successful: {message}")
            else:
                self.api_status_label.setText("❌ API: Sync failed")
                self.status_bar.showMessage("Sync failed", 5000)
                logger.error(f"❌ Quick sync failed: {message}")
                QMessageBox.warning(self, "Sync Failed", message)
            
        except Exception as e:
            self.api_status_label.setText("❌ API: Error")
            logger.error(f"Quick sync error: {e}")
            QMessageBox.critical(self, "Sync Error", f"Sync failed: {str(e)}")
        finally:
            self.quick_sync_button.setEnabled(True)
    
    def auto_sync(self):
        """Perform automatic background sync"""
        try:
            logger.info("🔄 Performing automatic sync...")
            success, message = self.player.storage_system.sync_with_api()
            
            if success:
                self.api_status_label.setText("✅ API: Auto-sync active")
                logger.info(f"✅ Auto-sync successful: {message}")
            else:
                self.api_status_label.setText("⚠️ API: Auto-sync warning")
                logger.warning(f"⚠️ Auto-sync failed: {message}")
                
        except Exception as e:
            logger.error(f"Auto-sync error: {e}")
            self.api_status_label.setText("❌ API: Auto-sync error")
    
    def toggle_auto_sync(self, checked):
        """Toggle automatic sync on/off"""
        if checked:
            # Load settings to get interval
            try:
                settings_file = Path("saves/api_settings.json")
                if settings_file.exists():
                    import json
                    with open(settings_file, 'r') as f:
                        settings = json.load(f)
                    interval = settings.get('sync_interval', 5) * 60000
                else:
                    interval = 300000  # Default 5 minutes
                
                self.sync_timer.start(interval)
                self.api_status_label.setText("🔄 API: Auto-sync enabled")
                self.quick_sync_button.setEnabled(True)
                logger.info("🔄 Auto-sync enabled")
                
            except Exception as e:
                logger.error(f"Failed to enable auto-sync: {e}")
                self.auto_sync_action.setChecked(False)
        else:
            self.sync_timer.stop()
            self.api_status_label.setText("🔌 API: Auto-sync disabled")
            logger.info("⏸️ Auto-sync disabled")
    
    def show_connection_status(self):
        """Show API connection status"""
        try:
            from utils.quinfall_api import test_api_connection
            
            if test_api_connection():
                QMessageBox.information(self, "Connection Status", 
                                      "✅ API server is reachable!\n\nYou can configure your credentials in API Settings.")
            else:
                QMessageBox.warning(self, "Connection Status", 
                                  "❌ Cannot reach API server.\n\nPlease check your internet connection and API settings.")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to test connection: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>🎮 Quinfall Companion</h2>
        <p><b>Version:</b> 2.0 - Enhanced with API Sync</p>
        <p><b>Description:</b> Advanced companion app for The Quinfall MMORPG</p>
        
        <h3>✨ Features:</h3>
        <ul>
            <li>🔨 Interactive Recipe Selection & Crafting</li>
            <li>📦 Multi-Location Storage Management</li>
            <li>🌐 Real-time API Synchronization</li>
            <li>📊 Market Price Integration</li>
            <li>⚙️ Advanced Player Management</li>
        </ul>
        
        <p><b>Developer:</b> Quinfall Community</p>
        <p><b>Game:</b> The Quinfall MMORPG</p>
        """
        QMessageBox.about(self, "About Quinfall Companion", about_text)
    
    def show_api_help(self):
        """Show API help information"""
        help_text = """
        <h2>🔗 Quinfall API Integration</h2>
        
        <h3>🔑 Getting Started:</h3>
        <ol>
            <li>Visit <a href="https://thequinfall.com/api-keys">thequinfall.com/api-keys</a></li>
            <li>Generate your personal API key</li>
            <li>Open API Settings in this app</li>
            <li>Enter your API key and test the connection</li>
            <li>Enable auto-sync for real-time synchronization</li>
        </ol>
        
        <h3>⚙️ Features:</h3>
        <ul>
            <li><b>Storage Sync:</b> Keep your inventory and storage in sync across devices</li>
            <li><b>Market Prices:</b> Get real-time market data for crafting calculations</li>
            <li><b>Auto-Sync:</b> Automatic background synchronization</li>
            <li><b>Conflict Resolution:</b> Smart merging of local and server data</li>
        </ul>
        
        <h3>🔒 Security:</h3>
        <p>Your API credentials are stored locally and encrypted. Never share your API key with others.</p>
        """
        QMessageBox.information(self, "API Help", help_text)
    
    def closeEvent(self, event):
        """Handle application close event"""
        try:
            # Sync on shutdown if enabled
            settings_file = Path("saves/api_settings.json")
            if settings_file.exists():
                import json
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                
                if settings.get('sync_on_shutdown', False):
                    logger.info("🔄 Performing shutdown sync...")
                    self.player.storage_system.sync_with_api()
            
            # Save player data
            self.player.save()
            logger.info("💾 Player data saved on shutdown")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Quinfall Companion")
    app.setApplicationVersion("2.0")
    
    # Set application icon if available
    icon_path = Path("assets/icon.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    window = CompanionApp()
    
    # Handle system exit
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
