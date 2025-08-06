from PySide6.QtWidgets import QWidget

class BaseTab(QWidget):
    def __init__(self, title: str):
        super().__init__()
        self.title = title
