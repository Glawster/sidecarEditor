"""
Example widget demonstrating Qt Designer .ui file integration.
This serves as a reference implementation for loading .ui files.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
)
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
        self._uiFilePath = Path(__file__).parent / "exampleWidget.ui"
        if self._uiFilePath.exists():
            self._loadUiFromFile()
        else:
            self._createUiProgrammatically()

        self._connectSignals()

    def _loadUiFromFile(self):
        """
        Load UI from .ui file.

        This is the recommended approach when you have a .ui file.
        """

        # Create QUiLoader
        loader = QUiLoader()

        # Open and load the .ui file
        uiFile = QFile(str(self._uiFilePath))
        uiFile.open(QFile.ReadOnly)
        uiWidget = loader.load(uiFile, self)
        uiFile.close()

        # Create layout and add loaded widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(uiWidget)

        # Find widgets by their objectName (set in Qt Designer)
        # Note: Widget names should follow naming conventions (btn, lbl, ent, etc.)
        self.lblTitle = uiWidget.findChild(QLabel, "lblTitle")
        self.entName = uiWidget.findChild(QLineEdit, "entName")
        self.btnSubmit = uiWidget.findChild(QPushButton, "btnSubmit")
        self.btnClear = uiWidget.findChild(QPushButton, "btnClear")

        # Verify all required widgets were found
        if not all([self.lblTitle, self.entName, self.btnSubmit, self.btnClear]):
            raise RuntimeError("Failed to find all required widgets in UI file")

    def _createUiProgrammatically(self):
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

    def _connectSignals(self):
        """
        Connect widget signals to slots.

        This should always be done in code, not in Qt Designer,
        for better maintainability and flexibility.
        """
        self.btnSubmit.clicked.connect(self._onSubmit)
        self.btnClear.clicked.connect(self._onClear)
        self.entName.returnPressed.connect(self._onSubmit)

    def _onSubmit(self):
        """Handle submit button click."""

        name = self.entName.text().strip()

        if not name:
            QMessageBox.warning(
                self, "Input Required", "Please enter a name before submitting."
            )
            return

        # Emit custom signal
        self.dataSubmitted.emit(name)

        # Show confirmation
        QMessageBox.information(self, "Submitted", f"Hello, {name}!")

    def _onClear(self):
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
