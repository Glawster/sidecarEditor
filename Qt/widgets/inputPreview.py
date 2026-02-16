"""
Image preview widget with original/output toggle.
"""

from logging import root
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from typing import Optional
from pathlib import Path

class InputPreview(QWidget):
    """Widget for displaying image preview with original/output toggle."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._originalPath: Optional[str] = None
        self._outputPath: Optional[str] = None
        self._showingOriginal = True

        self._setupUi()

    def _setupUi(self):
        """Set up the user interface by loading from .ui file."""
        uiFilePath = Path(__file__).parent / "inputPreview.ui"

        loader = QUiLoader()
        uiFile = QFile(str(uiFilePath))
        if not uiFile.open(QFile.ReadOnly): # type: ignore
            raise RuntimeError(f"Failed to open UI file: {uiFilePath}")

        root = loader.load(uiFile, None)
        uiFile.close()

        if root is None:
            raise RuntimeError(f"Failed to load UI file: {uiFilePath}")

        self._showOutputButton = root.findChild(QPushButton, "btnShowOutput")
        self._statusLabel = root.findChild(QLabel, "lblStatus")
        self._imageLabel = root.findChild(QLabel, "lblImage")

        missing = [name for name, w in {
            "btnShowOutput": self._showOutputButton,
            "lblStatus": self._statusLabel,
            "lblImage": self._imageLabel,
        }.items() if w is None]
        if missing:
            raise RuntimeError(f"Missing widgets in inputPreview.ui: {', '.join(missing)}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(root)
        
        self.ui = root
    
        # wire events + initial state
        self._showOutputButton.clicked.connect(self._onToggle) # type: ignore
        self._showOutputButton.setEnabled(False) # type: ignore

    def setImages(self, originalPath: str, outputPath: Optional[str] = None):
        """
        Set the images to display.

        Args:
            originalPath: Path to original image
            outputPath: Path to output image (optional)
        """
        self._originalPath = originalPath
        self._outputPath = outputPath
        self._showingOriginal = True

        # Update toggle button state
        if outputPath:
            self._showOutputButton.setEnabled(True) # type: ignore
            self._showOutputButton.setText("Show Output") # type: ignore
        else:
            self._showOutputButton.setEnabled(False) # type: ignore
            self._showOutputButton.setText("Show Output (Not Available)") # type: ignore

        # Display the original image
        self._displayImage(originalPath) # type: ignore
        self._updateStatus() # type: ignore

    def _displayImage(self, imagePath: str):
        """
        Display an image.

        Args:
            imagePath: Path to the image file
        """
        pixmap = QPixmap(imagePath)

        if pixmap.isNull():
            self._imageLabel.setText(f"Could not load image:\n{imagePath}") # type: ignore
            return

        # Scale to fit widget while maintaining aspect ratio
        scaledPixmap = pixmap.scaled(
            self._imageLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation # type: ignore
        )

        self._imageLabel.setPixmap(scaledPixmap) # type: ignore

    def _onToggle(self):
        """Handle toggle button click."""
        if not self._outputPath:
            return

        self._showingOriginal = not self._showingOriginal

        if self._showingOriginal:
            self._displayImage(self._originalPath) # type: ignore
            self._showOutputButton.setText("Show Output")  # type: ignore
        else:
            self._displayImage(self._outputPath) # type: ignore
            self._showOutputButton.setText("Show Original")  # type: ignore

        self._updateStatus()

    def _updateStatus(self):
        """Update the status label."""
        import os

        if self._showingOriginal:
            status = f"Original: {os.path.basename(self._originalPath)}" # type: ignore
        else:
            status = f"Output: {os.path.basename(self._outputPath)}" # type: ignore

        self._statusLabel.setText(status)  # type: ignore

    def clear(self):
        """Clear the displayed image."""
        self._originalPath = None
        self._outputPath = None
        self._showingOriginal = True
        self._imageLabel.clear()  # type: ignore
        self._imageLabel.setText("No image selected")  # type: ignore
        self._statusLabel.setText("No image selected")  # type: ignore
        self._showOutputButton.setEnabled(False)  # type: ignore
        self._showOutputButton.setText("Show Output")  # type: ignore

    def resizeEvent(self, event):
        """Handle resize events to re-scale the image."""
        super().resizeEvent(event)

        # Re-display current image at new size
        if self._originalPath:
            currentPath = (
                self._outputPath
                if not self._showingOriginal and self._outputPath
                else self._originalPath
            )
            self._displayImage(currentPath)
