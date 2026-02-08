"""
Example widget demonstrating Qt Designer .ui file integration.
This serves as a reference implementation for loading .ui files.
"""

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox
from PySide6.QtCore import QFile, Signal
from PySide6.QtUiTools import QUiLoader


class ExampleWidget(QWidget):
    """
    Example widget showing how to load and use a .ui file.
    
    This demonstrates:
    1. Loading a .ui file at runtime
    2. Finding widgets by name
    3. Connecting signals
    4. Implementing business logic
    """
    
    # Custom signal example
    dataSubmitted = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Check if .ui file exists, otherwise fall back to programmatic UI
        ui_file_path = Path(__file__).parent / "exampleWidget.ui"
        if ui_file_path.exists():
            self._load_ui_from_file()
        else:
            self._create_ui_programmatically()
        
        self._connect_signals()
    
    def _load_ui_from_file(self):
        """
        Load UI from .ui file.
        
        This is the recommended approach when you have a .ui file.
        """

        ui_file_path = Path(__file__).parent / "exampleWidget.ui"
        
        # Create QUiLoader
        loader = QUiLoader()
        
        # Open and load the .ui file
        ui_file = QFile(str(ui_file_path))
        ui_file.open(QFile.ReadOnly)
        ui_widget = loader.load(ui_file, self)
        ui_file.close()
        
        # Create layout and add loaded widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(ui_widget)
        
        # Find widgets by their objectName (set in Qt Designer)
        # Note: Widget names should follow naming conventions (btn, lbl, ent, etc.)
        self.lblTitle = ui_widget.findChild(QLabel, "lblTitle")
        self.entName = ui_widget.findChild(QLineEdit, "entName")
        self.btnSubmit = ui_widget.findChild(QPushButton, "btnSubmit")
        self.btnClear = ui_widget.findChild(QPushButton, "btnClear")
        
        # Verify all required widgets were found
        if not all([self.lblTitle, self.entName, self.btnSubmit, self.btnClear]):
            raise RuntimeError("Failed to find all required widgets in UI file")
    
    def _create_ui_programmatically(self):
        """
        Create UI programmatically as fallback.
        
        This is used when .ui file doesn't exist.
        """

        layout = QVBoxLayout(self)
        
        # Title label
        self.lblTitle = QLabel("Example Widget")
        self.lblTitle.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(self.lblTitle)
        
        # Name input
        self.entName = QLineEdit()
        self.entName.setPlaceholderText("Enter your name...")
        layout.addWidget(self.entName)
        
        # Buttons
        self.btnSubmit = QPushButton("Submit")
        layout.addWidget(self.btnSubmit)
        
        self.btnClear = QPushButton("Clear")
        layout.addWidget(self.btnClear)
        
        layout.addStretch()
    
    def _connect_signals(self):
        """
        Connect widget signals to slots.
        
        This should always be done in code, not in Qt Designer,
        for better maintainability and flexibility.
        """
        self.btnSubmit.clicked.connect(self._on_submit)
        self.btnClear.clicked.connect(self._on_clear)
        self.entName.returnPressed.connect(self._on_submit)
    
    def _on_submit(self):
        """Handle submit button click."""

        name = self.entName.text().strip()
        
        if not name:
            QMessageBox.warning(
                self,
                "Input Required",
                "Please enter a name before submitting."
            )
            return
        
        # Emit custom signal
        self.dataSubmitted.emit(name)
        
        # Show confirmation
        QMessageBox.information(
            self,
            "Submitted",
            f"Hello, {name}!"
        )
    
    def _on_clear(self):
        """Handle clear button click."""
        self.entName.clear()
        self.entName.setFocus()


# Example standalone usage (for testing)
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create and show widget
    widget = ExampleWidget()
    widget.setWindowTitle("Example Widget Demo")
    widget.resize(400, 200)
    
    # Connect to custom signal
    widget.dataSubmitted.connect(lambda name: print(f"Data submitted: {name}"))
    
    widget.show()
    sys.exit(app.exec())
