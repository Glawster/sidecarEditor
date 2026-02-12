"""
Image preview widget with original/output toggle.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from typing import Optional


class ImagePreview(QWidget):
    """Widget for displaying image preview with original/output toggle."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._originalPath: Optional[str] = None
        self._outputPath: Optional[str] = None
        self._showingOriginal = True

        self._setupUi()

    def _setupUi(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Control bar
        controlBar = QHBoxLayout()

        self._statusLabel = QLabel("No image selected")
        controlBar.addWidget(self._statusLabel)

        controlBar.addStretch()

        self._toggleButton = QPushButton("Show Output")
        self._toggleButton.clicked.connect(self._onToggle)
        self._toggleButton.setEnabled(False)
        controlBar.addWidget(self._toggleButton)

        layout.addLayout(controlBar)

        # Image display
        self._imageLabel = QLabel()
        self._imageLabel.setAlignment(Qt.AlignCenter)
        self._imageLabel.setMinimumSize(400, 400)
        self._imageLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._imageLabel.setScaledContents(False)
        self._imageLabel.setStyleSheet("QLabel { background-color: #2b2b2b; }")
        layout.addWidget(self._imageLabel)

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
            self._toggleButton.setEnabled(True)
            self._toggleButton.setText("Show Output")
        else:
            self._toggleButton.setEnabled(False)
            self._toggleButton.setText("Show Output (Not Available)")

        # Display the original image
        self._displayImage(originalPath)
        self._updateStatus()

    def _displayImage(self, imagePath: str):
        """
        Display an image.

        Args:
            imagePath: Path to the image file
        """
        pixmap = QPixmap(imagePath)

        if pixmap.isNull():
            self._imageLabel.setText(f"Could not load image:\n{imagePath}")
            return

        # Scale to fit widget while maintaining aspect ratio
        scaledPixmap = pixmap.scaled(
            self._imageLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self._imageLabel.setPixmap(scaledPixmap)

    def _onToggle(self):
        """Handle toggle button click."""
        if not self._outputPath:
            return

        self._showingOriginal = not self._showingOriginal

        if self._showingOriginal:
            self._displayImage(self._originalPath)
            self._toggleButton.setText("Show Output")
        else:
            self._displayImage(self._outputPath)
            self._toggleButton.setText("Show Original")

        self._updateStatus()

    def _updateStatus(self):
        """Update the status label."""
        import os

        if self._showingOriginal:
            status = f"Original: {os.path.basename(self._originalPath)}"
        else:
            status = f"Output: {os.path.basename(self._outputPath)}"

        self._statusLabel.setText(status)

    def clear(self):
        """Clear the displayed image."""
        self._originalPath = None
        self._outputPath = None
        self._showingOriginal = True
        self._imageLabel.clear()
        self._imageLabel.setText("No image selected")
        self._statusLabel.setText("No image selected")
        self._toggleButton.setEnabled(False)
        self._toggleButton.setText("Show Output")

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
