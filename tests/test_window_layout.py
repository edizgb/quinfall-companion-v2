import unittest
from PySide6.QtWidgets import QApplication, QScrollArea
from main import CompanionApp

app = QApplication([])

class TestWindowLayout(unittest.TestCase):
    def test_minimum_size(self):
        window = CompanionApp()
        self.assertGreaterEqual(window.minimumWidth(), 800)
        self.assertGreaterEqual(window.minimumHeight(), 600)

    def test_scroll_area(self):
        window = CompanionApp()
        self.assertIsNotNone(window.findChild(QScrollArea))
