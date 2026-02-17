"""
Generic image preview widget.
"""

import os

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)
from PySide6.QtCore import Qt, QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from typing import Optional
from pathlib import Path


class ImagePreview(QWidget):
    """Widget for displaying a single image."""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)

        self._imagePath: Optional[str] = None
        self._title = title
        self._setupUi()

    def _setupUi(self):
        uiFilePath = Path(__file__).parent / "imagePreview.ui"
        # reuse same ui file (no toggle button required)

        loader = QUiLoader()
        uiFile = QFile(str(uiFilePath))
        if not uiFile.open(QFile.ReadOnly):  # type: ignore
            raise RuntimeError(f"Failed to open UI file: {uiFilePath}")

        root = loader.load(uiFile, None)
        uiFile.close()

        if root is None:
            raise RuntimeError(f"Failed to load UI file: {uiFilePath}")

        self._statusLabel = root.findChild(QLabel, "lblStatus")
        self._imageLabel = root.findChild(QLabel, "lblImage")

        missing = [name for name, w in {
            "lblStatus": self._statusLabel,
            "lblImage": self._imageLabel,
        }.items() if w is None]

        if missing:
            raise RuntimeError(f"Missing widgets in imagePreview.ui: {', '.join(missing)}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(root)

        self.ui = root

    # ----------------------------------------------------

    def setImage(self, imagePath: Optional[str]):
        """Display a single image."""
        self._imagePath = imagePath

        if not imagePath:
            self.clear()
            return

        pixmap = QPixmap(imagePath)

        if pixmap.isNull():
            self._imageLabel.setText(f"Could not load image:\n{imagePath}") # type: ignore
            return

        scaledPixmap = pixmap.scaled(
            self._imageLabel.size(), # type: ignore
            Qt.KeepAspectRatio, # type: ignore
            Qt.SmoothTransformation, # type: ignore
        )

        self._imageLabel.setPixmap(scaledPixmap) # type: ignore
        self._updateStatus()

    # ----------------------------------------------------

    def _updateStatus(self):
            if not self._statusLabel:
                return

            if not self._imagePath:
                self._statusLabel.setText("No image selected")
                return
            # filename should be two last two path components 
            # (e.g. "input/image.png" or "output/image.png") plus the actual filename, 
            # to help distinguish between input and output images in the status label
            parts = Path(self._imagePath).parts
            # how do i os.join parts -3, -2, -1? if parts is long enough, otherwise just use the filename
            if len(parts) >= 3:
                filename = os.path.join(parts[-3], parts[-2], parts[-1])
            elif len(parts) == 2:
                filename = os.path.join(parts[-2], parts[-1])
            else:
                filename = os.path.basename(self._imagePath)

            if self._title:
                self._statusLabel.setText(f"{self._title}: {filename}")
            else:
                self._statusLabel.setText(filename)

    # ----------------------------------------------------

    def clear(self):
        self._imagePath = None
        self._imageLabel.clear() # type: ignore
        self._imageLabel.setText("No image selected") # type: ignore
        self._statusLabel.setText("No image selected") # type: ignore

    # ----------------------------------------------------

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if self._imagePath:
            self.setImage(self._imagePath)
