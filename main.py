import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from src.app import ROMOrganizerApp

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = ROMOrganizerApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()