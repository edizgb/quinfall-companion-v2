from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider, 
                             QPushButton, QTextEdit, QSpinBox, QGroupBox, QGridLayout,
                             QProgressBar, QTabWidget, QWidget, QTableWidget, QTableWidgetItem)
from PySide6.QtCore import Qt, QTimer
from ui.base_tab import BaseTab
from data.enums import Specialization
from data.player import Player
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SpecializationTab(BaseTab):
    def __init__(self):
        super().__init__("Specializations")
        self.player = Player()
        self.player.load()
        
        # Specialization data
        self.trading_routes = self.load_trading_routes()
        self.shipbuilding_projects = self.load_shipbuilding_projects()
        
        # UI state
        self.active_trades = []
        self.active_projects = []
        
        self.setup_ui()
        logger.info(" Specialization tab initialized")

    def setup_ui(self):
        """Setup the complete specialization UI"""
        main_layout = QVBoxLayout()
        
        # Header
        header = QLabel(" Quinfall Specialization System")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #8b5cf6; margin: 10px;")
        main_layout.addWidget(header)
        
        # Create tab widget for different specializations
        self.spec_tabs = QTabWidget()
        
        # Trading Tab
        trading_tab = self.create_trading_tab()
        self.spec_tabs.addTab(trading_tab, " Trading")
        
        # Shipbuilding Tab
        shipbuilding_tab = self.create_shipbuilding_tab()
        self.spec_tabs.addTab(shipbuilding_tab, " Shipbuilding")
        
        main_layout.addWidget(self.spec_tabs)
        self.setLayout(main_layout)
        
        # Initialize displays
        self.update_trading_display()
        self.update_shipbuilding_display()

    def create_trading_tab(self):
        """Create trading specialization tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Trading Skills Section
        skills_group = QGroupBox(" Trading Skills & Reputation")
        skills_layout = QGridLayout()
        
        # Trading level
        skills_layout.addWidget(QLabel("Trading Level:"), 0, 0)
        self.trading_level_label = QLabel("1")
        self.trading_level_label.setStyleSheet("font-weight: bold; color: #fbbf24;")
        skills_layout.addWidget(self.trading_level_label, 0, 1)
        
        # Trading skill adjustment
        skills_layout.addWidget(QLabel("Adjust Level:"), 1, 0)
        self.trading_skill_slider = QSlider(Qt.Horizontal)
        self.trading_skill_slider.setRange(1, 100)
        self.trading_skill_slider.valueChanged.connect(self.on_trading_skill_change)
        skills_layout.addWidget(self.trading_skill_slider, 1, 1)
        
        # Reputation with different cities
        skills_layout.addWidget(QLabel("Quinfall City Rep:"), 2, 0)
        self.quinfall_rep_progress = QProgressBar()
        self.quinfall_rep_progress.setRange(0, 100)
        self.quinfall_rep_progress.setValue(50)
        skills_layout.addWidget(self.quinfall_rep_progress, 2, 1)
        
        skills_group.setLayout(skills_layout)
        layout.addWidget(skills_group)
        
        # Trading Routes Section
        routes_group = QGroupBox(" Trading Routes")
        routes_layout = QVBoxLayout()
        
        # Route selection
        route_controls = QHBoxLayout()
        route_controls.addWidget(QLabel("Select Route:"))
        self.route_select = QComboBox()
        route_controls.addWidget(self.route_select)
        
        self.start_trade_btn = QPushButton(" Start Trade Run")
        self.start_trade_btn.clicked.connect(self.start_trade_run)
        self.start_trade_btn.setStyleSheet("background-color: #059669; color: white; font-weight: bold;")
        route_controls.addWidget(self.start_trade_btn)
        
        routes_layout.addLayout(route_controls)
        
        # Trade goods selection
        goods_layout = QHBoxLayout()
        goods_layout.addWidget(QLabel("Trade Goods:"))
        self.goods_select = QComboBox()
        goods_layout.addWidget(self.goods_select)
        
        goods_layout.addWidget(QLabel("Quantity:"))
        self.trade_quantity_spin = QSpinBox()
        self.trade_quantity_spin.setRange(1, 1000)
        self.trade_quantity_spin.setValue(10)
        goods_layout.addWidget(self.trade_quantity_spin)
        
        routes_layout.addLayout(goods_layout)
        
        # Profit calculation display
        self.profit_display = QTextEdit()
        self.profit_display.setMaximumHeight(120)
        self.profit_display.setReadOnly(True)
        self.profit_display.setStyleSheet("background-color: #1e293b; color: #e2e8f0; border: 1px solid #475569;")
        routes_layout.addWidget(QLabel("Profit Analysis:"))
        routes_layout.addWidget(self.profit_display)
        
        routes_group.setLayout(routes_layout)
        layout.addWidget(routes_group)
        
        widget.setLayout(layout)
        return widget

    def create_shipbuilding_tab(self):
        """Create shipbuilding specialization tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Shipbuilding Skills Section
        skills_group = QGroupBox(" Shipbuilding Skills")
        skills_layout = QGridLayout()
        
        # Shipbuilding level
        skills_layout.addWidget(QLabel("Shipbuilding Level:"), 0, 0)
        self.shipbuilding_level_label = QLabel("1")
        self.shipbuilding_level_label.setStyleSheet("font-weight: bold; color: #06b6d4;")
        skills_layout.addWidget(self.shipbuilding_level_label, 0, 1)
        
        # Shipbuilding skill adjustment
        skills_layout.addWidget(QLabel("Adjust Level:"), 1, 0)
        self.shipbuilding_skill_slider = QSlider(Qt.Horizontal)
        self.shipbuilding_skill_slider.setRange(1, 100)
        self.shipbuilding_skill_slider.valueChanged.connect(self.on_shipbuilding_skill_change)
        skills_layout.addWidget(self.shipbuilding_skill_slider, 1, 1)
        
        skills_group.setLayout(skills_layout)
        layout.addWidget(skills_group)
        
        # Ship Projects Section
        projects_group = QGroupBox(" Ship Construction Projects")
        projects_layout = QVBoxLayout()
        
        # Project selection
        project_controls = QHBoxLayout()
        project_controls.addWidget(QLabel("Ship Type:"))
        self.ship_type_select = QComboBox()
        project_controls.addWidget(self.ship_type_select)
        
        self.start_project_btn = QPushButton(" Start Construction")
        self.start_project_btn.clicked.connect(self.start_ship_project)
        self.start_project_btn.setStyleSheet("background-color: #0369a1; color: white; font-weight: bold;")
        project_controls.addWidget(self.start_project_btn)
        
        projects_layout.addLayout(project_controls)
        
        # Materials required display
        self.materials_display = QTextEdit()
        self.materials_display.setMaximumHeight(120)
        self.materials_display.setReadOnly(True)
        self.materials_display.setStyleSheet("background-color: #1e293b; color: #e2e8f0; border: 1px solid #475569;")
        projects_layout.addWidget(QLabel("Required Materials:"))
        projects_layout.addWidget(self.materials_display)
        
        projects_group.setLayout(projects_layout)
        layout.addWidget(projects_group)
        
        widget.setLayout(layout)
        return widget

    def load_trading_routes(self):
        """Load trading routes data"""
        return {
            "Quinfall → Calmnarock": {
                "distance": 50,
                "travel_time": 120,  # minutes
                "goods": {
                    "Iron Ingots": {"buy": 15.0, "sell": 22.0},
                    "Wheat": {"buy": 2.0, "sell": 3.5},
                    "Leather": {"buy": 8.0, "sell": 12.0}
                },
                "reputation_req": 0,
                "risk": "Low"
            },
            "Calmnarock → Distant Port": {
                "distance": 120,
                "travel_time": 300,
                "goods": {
                    "Exotic Spices": {"buy": 45.0, "sell": 75.0},
                    "Rare Gems": {"buy": 100.0, "sell": 180.0}
                },
                "reputation_req": 25,
                "risk": "Medium"
            }
        }

    def load_shipbuilding_projects(self):
        """Load shipbuilding projects data"""
        return {
            "Fishing Boat": {
                "level_req": 1,
                "materials": {"Oak Wood": 50, "Iron Nails": 25, "Rope": 10},
                "build_time": 180,  # minutes
                "cost": 500
            },
            "Merchant Vessel": {
                "level_req": 25,
                "materials": {"Hardwood": 200, "Iron Reinforcement": 100, "Canvas": 50},
                "build_time": 720,
                "cost": 2500
            },
            "War Galley": {
                "level_req": 50,
                "materials": {"Ebony Wood": 300, "Steel Plating": 150},
                "build_time": 1440,
                "cost": 8000
            }
        }

    def update_trading_display(self):
        """Update trading-related displays"""
        trading_level = self.player.specializations.get(Specialization.TRADING, 1)
        self.trading_level_label.setText(str(trading_level))
        self.trading_skill_slider.setValue(trading_level)
        
        # Update route selection
        self.route_select.clear()
        available_routes = []
        for route, data in self.trading_routes.items():
            if trading_level >= data["reputation_req"]:
                available_routes.append(f"{route} ({data['risk']} Risk)")
            else:
                available_routes.append(f" {route} (Req: Lv.{data['reputation_req']})")
        
        self.route_select.addItems(available_routes)
        
        # Update goods selection
        if available_routes:
            first_route = list(self.trading_routes.keys())[0]
            goods = list(self.trading_routes[first_route]["goods"].keys())
            self.goods_select.clear()
            self.goods_select.addItems(goods)
        
        self.update_profit_calculation()

    def update_shipbuilding_display(self):
        """Update shipbuilding-related displays"""
        shipbuilding_level = self.player.specializations.get(Specialization.SHIPBUILDING, 1)
        self.shipbuilding_level_label.setText(str(shipbuilding_level))
        self.shipbuilding_skill_slider.setValue(shipbuilding_level)
        
        # Update ship type selection
        self.ship_type_select.clear()
        available_ships = []
        for ship, data in self.shipbuilding_projects.items():
            if shipbuilding_level >= data["level_req"]:
                available_ships.append(f"{ship} (Lv.{data['level_req']})")
            else:
                available_ships.append(f" {ship} (Req: Lv.{data['level_req']})")
        
        self.ship_type_select.addItems(available_ships)
        self.update_materials_display()

    def update_profit_calculation(self):
        """Update profit calculation display"""
        if not self.route_select.currentText() or " " in self.route_select.currentText():
            self.profit_display.setPlainText("Select an available route to see profit analysis.")
            return
        
        route_name = self.route_select.currentText().split(" (")[0]
        route_data = self.trading_routes.get(route_name, {})
        
        if not route_data or not self.goods_select.currentText():
            return
        
        goods_name = self.goods_select.currentText()
        goods_data = route_data["goods"].get(goods_name, {})
        quantity = self.trade_quantity_spin.value()
        
        if goods_data:
            buy_price = goods_data["buy"]
            sell_price = goods_data["sell"]
            profit_per_item = sell_price - buy_price
            total_profit = profit_per_item * quantity
            profit_margin = (profit_per_item / buy_price) * 100
            
            analysis = f"""Route: {route_name}
Goods: {goods_name} x{quantity}
Buy Price: {buy_price:.1f}g each
Sell Price: {sell_price:.1f}g each
Profit: {profit_per_item:.1f}g per item ({profit_margin:.1f}%)
Total Profit: {total_profit:.1f}g
Travel Time: {route_data['travel_time']} minutes
Risk Level: {route_data['risk']}"""
            
            self.profit_display.setPlainText(analysis)

    def update_materials_display(self):
        """Update materials required display"""
        if not self.ship_type_select.currentText() or " " in self.ship_type_select.currentText():
            self.materials_display.setPlainText("Select an available ship type to see materials.")
            return
        
        ship_name = self.ship_type_select.currentText().split(" (")[0]
        ship_data = self.shipbuilding_projects.get(ship_name, {})
        
        if ship_data:
            materials_text = f"Materials required for {ship_name}:\n"
            for material, quantity in ship_data["materials"].items():
                have = self.player.get_item_count(material.lower().replace(" ", "_"), "both")
                status = "" if have >= quantity else ""
                materials_text += f"{status} {material}: {have}/{quantity}\n"
            
            materials_text += f"\nBuild Time: {ship_data['build_time']} minutes"
            materials_text += f"\nCost: {ship_data['cost']}g"
            
            self.materials_display.setPlainText(materials_text)

    def on_trading_skill_change(self, value):
        """Handle trading skill change"""
        self.player.specializations[Specialization.TRADING] = value
        self.player.save()
        self.update_trading_display()
        logger.info(f" Trading skill updated to: {value}")

    def on_shipbuilding_skill_change(self, value):
        """Handle shipbuilding skill change"""
        self.player.specializations[Specialization.SHIPBUILDING] = value
        self.player.save()
        self.update_shipbuilding_display()
        logger.info(f" Shipbuilding skill updated to: {value}")

    def start_trade_run(self):
        """Start a trading run"""
        if " " in self.route_select.currentText():
            logger.warning(" Route not available at current level")
            return
        
        route_name = self.route_select.currentText().split(" (")[0]
        goods_name = self.goods_select.currentText()
        quantity = self.trade_quantity_spin.value()
        
        logger.info(f" Started trade run: {goods_name} x{quantity} on {route_name}")

    def start_ship_project(self):
        """Start a shipbuilding project"""
        if " " in self.ship_type_select.currentText():
            logger.warning(" Ship type not available at current level")
            return
        
        ship_name = self.ship_type_select.currentText().split(" (")[0]
        logger.info(f" Started shipbuilding project: {ship_name}")
