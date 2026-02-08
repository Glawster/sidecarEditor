"""
Entry point for Sidecar Editor.
Run with: python -m sidecarEditor
"""

import sys
from PySide6.QtWidgets import QApplication

# Import from the package
from Qt.mainWindow import MainWindow


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Sidecar Editor")
    app.setOrganizationName("SidecarEditor")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
