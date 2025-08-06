#!/usr/bin/env python3
"""
API Settings Dialog for Quinfall Companion
Allows users to configure API credentials and sync settings
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QLineEdit, QPushButton, QLabel, QCheckBox, 
                               QSpinBox, QGroupBox, QTextEdit, QTabWidget,
                               QWidget, QMessageBox, QProgressBar)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class APITestThread(QThread):
    """Thread for testing API connection without blocking UI"""
    
    test_completed = Signal(bool, str)  # success, message
    
    def __init__(self, username=None, password=None, api_key=None):
        super().__init__()
        self.username = username
        self.password = password
        self.api_key = api_key
    
    def run(self):
        try:
            from utils.quinfall_api import QuinfallAPIClient
            
            client = QuinfallAPIClient()
            
            if self.api_key:
                success = client.authenticate(api_key=self.api_key)
                if success:
                    self.test_completed.emit(True, "✅ API key authentication successful!")
                else:
                    self.test_completed.emit(False, "❌ API key authentication failed")
            elif self.username and self.password:
                success = client.authenticate(self.username, self.password)
                if success:
                    self.test_completed.emit(True, "✅ Username/password authentication successful!")
                else:
                    self.test_completed.emit(False, "❌ Username/password authentication failed")
            else:
                self.test_completed.emit(False, "❌ No credentials provided")
                
        except Exception as e:
            self.test_completed.emit(False, f"❌ Connection test failed: {str(e)}")

class APISyncThread(QThread):
    """Thread for performing API sync without blocking UI"""
    
    sync_completed = Signal(bool, str)  # success, message
    sync_progress = Signal(str)  # progress message
    
    def __init__(self, storage_system):
        super().__init__()
        self.storage_system = storage_system
    
    def run(self):
        try:
            self.sync_progress.emit("🔄 Connecting to Quinfall API...")
            
            success, message = self.storage_system.sync_with_api()
            
            if success:
                self.sync_completed.emit(True, message)
            else:
                self.sync_completed.emit(False, message)
                
        except Exception as e:
            self.sync_completed.emit(False, f"❌ Sync failed: {str(e)}")

class APISettingsDialog(QDialog):
    """Dialog for configuring Quinfall API settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quinfall API Settings")
        self.setFixedSize(500, 600)
        self.setModal(True)
        
        # Load current settings
        self.settings = self._load_settings()
        
        self.init_ui()
        self.load_current_settings()
        
        # Test thread
        self.test_thread = None
        self.sync_thread = None
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Authentication tab
        auth_tab = self._create_auth_tab()
        tab_widget.addTab(auth_tab, "🔐 Authentication")
        
        # Sync settings tab
        sync_tab = self._create_sync_tab()
        tab_widget.addTab(sync_tab, "⚙️ Sync Settings")
        
        # Status tab
        status_tab = self._create_status_tab()
        tab_widget.addTab(status_tab, "📊 Status")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.test_button = QPushButton("🧪 Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        
        self.save_button = QPushButton("💾 Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        
        self.cancel_button = QPushButton("❌ Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.test_button)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _create_auth_tab(self):
        """Create authentication settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # API Key authentication
        api_key_group = QGroupBox("🔑 API Key Authentication (Recommended)")
        api_key_layout = QFormLayout(api_key_group)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter your Quinfall API key...")
        api_key_layout.addRow("API Key:", self.api_key_input)
        
        api_key_info = QLabel("Get your API key from: https://thequinfall.com/api-keys")
        api_key_info.setStyleSheet("color: #666; font-size: 11px;")
        api_key_info.setWordWrap(True)
        api_key_layout.addRow("", api_key_info)
        
        layout.addWidget(api_key_group)
        
        # Username/Password authentication
        user_pass_group = QGroupBox("👤 Username/Password Authentication")
        user_pass_layout = QFormLayout(user_pass_group)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Your Quinfall username...")
        user_pass_layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Your Quinfall password...")
        user_pass_layout.addRow("Password:", self.password_input)
        
        user_pass_info = QLabel("⚠️ API key authentication is more secure and recommended")
        user_pass_info.setStyleSheet("color: #ff6b35; font-size: 11px;")
        user_pass_info.setWordWrap(True)
        user_pass_layout.addRow("", user_pass_info)
        
        layout.addWidget(user_pass_group)
        
        # Server settings
        server_group = QGroupBox("🌐 Server Settings")
        server_layout = QFormLayout(server_group)
        
        self.server_url_input = QLineEdit()
        self.server_url_input.setText("https://api.thequinfall.com/v1")
        self.server_url_input.setPlaceholderText("API server URL...")
        server_layout.addRow("Server URL:", self.server_url_input)
        
        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(5, 120)
        self.timeout_input.setValue(30)
        self.timeout_input.setSuffix(" seconds")
        server_layout.addRow("Timeout:", self.timeout_input)
        
        layout.addWidget(server_group)
        
        layout.addStretch()
        return widget
    
    def _create_sync_tab(self):
        """Create sync settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Auto-sync settings
        auto_sync_group = QGroupBox("🔄 Automatic Sync")
        auto_sync_layout = QFormLayout(auto_sync_group)
        
        self.auto_sync_enabled = QCheckBox("Enable automatic sync")
        auto_sync_layout.addRow("", self.auto_sync_enabled)
        
        self.sync_interval = QSpinBox()
        self.sync_interval.setRange(1, 60)
        self.sync_interval.setValue(5)
        self.sync_interval.setSuffix(" minutes")
        auto_sync_layout.addRow("Sync interval:", self.sync_interval)
        
        self.sync_on_startup = QCheckBox("Sync on application startup")
        auto_sync_layout.addRow("", self.sync_on_startup)
        
        self.sync_on_shutdown = QCheckBox("Sync on application shutdown")
        auto_sync_layout.addRow("", self.sync_on_shutdown)
        
        layout.addWidget(auto_sync_group)
        
        # Conflict resolution
        conflict_group = QGroupBox("⚖️ Conflict Resolution")
        conflict_layout = QFormLayout(conflict_group)
        
        conflict_info = QLabel("When local and server data differ:")
        conflict_layout.addRow("", conflict_info)
        
        self.prefer_server = QCheckBox("Prefer server data (recommended)")
        self.prefer_server.setChecked(True)
        conflict_layout.addRow("", self.prefer_server)
        
        self.prefer_local = QCheckBox("Prefer local data")
        conflict_layout.addRow("", self.prefer_local)
        
        # Make checkboxes mutually exclusive
        self.prefer_server.toggled.connect(lambda checked: self.prefer_local.setChecked(not checked) if checked else None)
        self.prefer_local.toggled.connect(lambda checked: self.prefer_server.setChecked(not checked) if checked else None)
        
        layout.addWidget(conflict_group)
        
        # Cache settings
        cache_group = QGroupBox("💾 Cache Settings")
        cache_layout = QFormLayout(cache_group)
        
        self.enable_cache = QCheckBox("Enable response caching")
        self.enable_cache.setChecked(True)
        cache_layout.addRow("", self.enable_cache)
        
        self.cache_duration = QSpinBox()
        self.cache_duration.setRange(30, 600)
        self.cache_duration.setValue(60)
        self.cache_duration.setSuffix(" seconds")
        cache_layout.addRow("Cache duration:", self.cache_duration)
        
        layout.addWidget(cache_group)
        
        layout.addStretch()
        return widget
    
    def _create_status_tab(self):
        """Create status and testing tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Connection status
        status_group = QGroupBox("📡 Connection Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("❓ Not tested")
        self.status_label.setStyleSheet("font-weight: bold; padding: 10px;")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(status_group)
        
        # Test results
        results_group = QGroupBox("📋 Test Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(150)
        self.results_text.setPlaceholderText("Connection test results will appear here...")
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(results_group)
        
        # Manual sync
        sync_group = QGroupBox("🔄 Manual Sync")
        sync_layout = QVBoxLayout(sync_group)
        
        sync_info = QLabel("Test storage synchronization with the server:")
        sync_layout.addWidget(sync_info)
        
        self.manual_sync_button = QPushButton("🔄 Sync Storage Now")
        self.manual_sync_button.clicked.connect(self.manual_sync)
        sync_layout.addWidget(self.manual_sync_button)
        
        self.sync_results = QTextEdit()
        self.sync_results.setMaximumHeight(100)
        self.sync_results.setPlaceholderText("Sync results will appear here...")
        sync_layout.addWidget(self.sync_results)
        
        layout.addWidget(sync_group)
        
        layout.addStretch()
        return widget
    
    def _load_settings(self):
        """Load API settings from file"""
        try:
            settings_file = Path("saves/api_settings.json")
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load API settings: {e}")
        
        # Default settings
        return {
            'server_url': 'https://api.thequinfall.com/v1',
            'timeout': 30,
            'auto_sync_enabled': True,
            'sync_interval': 5,
            'sync_on_startup': True,
            'sync_on_shutdown': True,
            'prefer_server': True,
            'enable_cache': True,
            'cache_duration': 60
        }
    
    def load_current_settings(self):
        """Load current settings into UI"""
        self.server_url_input.setText(self.settings.get('server_url', ''))
        self.timeout_input.setValue(self.settings.get('timeout', 30))
        self.auto_sync_enabled.setChecked(self.settings.get('auto_sync_enabled', True))
        self.sync_interval.setValue(self.settings.get('sync_interval', 5))
        self.sync_on_startup.setChecked(self.settings.get('sync_on_startup', True))
        self.sync_on_shutdown.setChecked(self.settings.get('sync_on_shutdown', True))
        self.prefer_server.setChecked(self.settings.get('prefer_server', True))
        self.prefer_local.setChecked(not self.settings.get('prefer_server', True))
        self.enable_cache.setChecked(self.settings.get('enable_cache', True))
        self.cache_duration.setValue(self.settings.get('cache_duration', 60))
    
    def test_connection(self):
        """Test API connection"""
        if self.test_thread and self.test_thread.isRunning():
            return
        
        # Get credentials
        api_key = self.api_key_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not api_key and not (username and password):
            QMessageBox.warning(self, "No Credentials", 
                              "Please enter either an API key or username/password.")
            return
        
        # Update UI
        self.status_label.setText("🔄 Testing connection...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.test_button.setEnabled(False)
        
        # Start test thread
        self.test_thread = APITestThread(username, password, api_key)
        self.test_thread.test_completed.connect(self._on_test_completed)
        self.test_thread.start()
    
    def _on_test_completed(self, success, message):
        """Handle test completion"""
        self.progress_bar.setVisible(False)
        self.test_button.setEnabled(True)
        
        if success:
            self.status_label.setText("✅ Connected")
            self.status_label.setStyleSheet("color: green; font-weight: bold; padding: 10px;")
        else:
            self.status_label.setText("❌ Connection failed")
            self.status_label.setStyleSheet("color: red; font-weight: bold; padding: 10px;")
        
        self.results_text.append(f"{message}\n")
    
    def manual_sync(self):
        """Perform manual storage sync"""
        if not hasattr(self.parent(), 'player') or not self.parent().player:
            QMessageBox.warning(self, "No Player Data", 
                              "Player data not available for sync.")
            return
        
        if self.sync_thread and self.sync_thread.isRunning():
            return
        
        # Update UI
        self.manual_sync_button.setEnabled(False)
        self.sync_results.append("🔄 Starting manual sync...\n")
        
        # Start sync thread
        storage_system = self.parent().player.storage_system
        self.sync_thread = APISyncThread(storage_system)
        self.sync_thread.sync_progress.connect(lambda msg: self.sync_results.append(f"{msg}\n"))
        self.sync_thread.sync_completed.connect(self._on_sync_completed)
        self.sync_thread.start()
    
    def _on_sync_completed(self, success, message):
        """Handle sync completion"""
        self.manual_sync_button.setEnabled(True)
        self.sync_results.append(f"{message}\n")
        
        if success:
            QMessageBox.information(self, "Sync Complete", message)
        else:
            QMessageBox.warning(self, "Sync Failed", message)
    
    def save_settings(self):
        """Save API settings"""
        try:
            # Collect settings
            settings = {
                'server_url': self.server_url_input.text().strip(),
                'timeout': self.timeout_input.value(),
                'auto_sync_enabled': self.auto_sync_enabled.isChecked(),
                'sync_interval': self.sync_interval.value(),
                'sync_on_startup': self.sync_on_startup.isChecked(),
                'sync_on_shutdown': self.sync_on_shutdown.isChecked(),
                'prefer_server': self.prefer_server.isChecked(),
                'enable_cache': self.enable_cache.isChecked(),
                'cache_duration': self.cache_duration.value()
            }
            
            # Save to file
            settings_file = Path("saves/api_settings.json")
            settings_file.parent.mkdir(exist_ok=True)
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            # Save credentials separately (more secure)
            api_key = self.api_key_input.text().strip()
            username = self.username_input.text().strip()
            password = self.password_input.text().strip()
            
            if api_key or (username and password):
                creds = {}
                if api_key:
                    creds['api_key'] = api_key
                if username:
                    creds['username'] = username
                if password:
                    creds['password'] = password
                
                creds_file = Path("saves/api_credentials.json")
                with open(creds_file, 'w') as f:
                    json.dump(creds, f, indent=2)
            
            QMessageBox.information(self, "Settings Saved", 
                                  "API settings saved successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", 
                               f"Failed to save settings: {str(e)}")
