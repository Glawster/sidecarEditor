"""
Thumbnail list widget for displaying images.
"""

from pathlib import Path
from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon, QFont
from typing import List, Optional


class ThumbnailList(QListWidget):
    """List widget that displays image thumbnails."""

    # Signal emitted when an image is selected
    imageSelected = Signal(str)  # imagePath

    # Signal emitted when thumbnails have finished loading
    thumbnailsLoaded = Signal(int)  # number of images loaded

    def __init__(self, parent=None):

        super().__init__(parent)

        # Set up the list widget
        self.setIconSize(QSize(100, 100))
        self.setViewMode(QListWidget.IconMode)
        self.setResizeMode(QListWidget.Adjust)
        self.setSpacing(10)
        self.setMovement(QListWidget.Static)

        # Connect selection signal
        self.currentItemChanged.connect(self._onSelectionChanged)

        # Store image paths
        self._imagePaths = []

    def loadImages(self, imagePaths: List[str], inputRoot: Optional[str] = None):
        """
        Load images into the thumbnail list.

        Args:
            imagePaths: List of image file paths
            inputRoot: Root input folder path (for subfolder separators)
        """
        self.clear()
        self._imagePaths = imagePaths

        # Group images by subfolder if input_root is provided
        if inputRoot:
            groups = {}

            for imgPath in imagePaths:
                # Get relative path from inputRoot
                try:
                    relPath = Path(imgPath).relative_to(Path(inputRoot))
                    subfolder = (
                        str(relPath.parent) if relPath.parent != Path(".") else ""
                    )
                except ValueError:
                    # If image is not under inputRoot, use empty subfolder
                    subfolder = ""

                if subfolder not in groups:
                    groups[subfolder] = []
                groups[subfolder].append(img_path)

            # Add images with separators between subfolders
            for subfolder in sorted(groups.keys()):
                # Add separator if it's not the first group or if subfolder is not empty
                if subfolder:
                    self._add_separator(subfolder)

                # Add thumbnails for this subfolder
                for imgPath in groups[subfolder]:
                    self._addThumbnail(imgPath)
        else:
            # No inputRoot, just add all images
            for imgPath in imagePaths:
                self._addThumbnail(imgPath)

        # Emit signal when loading is complete
        self.thumbnailsLoaded.emit(len(imagePaths))

    def _addThumbnail(self, imagePath: str):
        """
        Add a single thumbnail to the list.

        Args:
            imagePath: Path to the image file
        """
        import os

        # Create thumbnail
        pixmap = QPixmap(imagePath)
        if pixmap.isNull():
            # If image can't be loaded, use a placeholder
            pixmap = QPixmap(100, 100)
            pixmap.fill(Qt.gray)

        # Scale to thumbnail size
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Create list item
        item = QListWidgetItem(QIcon(pixmap), os.path.basename(imagePath))
        item.setData(Qt.UserRole, imagePath)  # Store full path
        self.addItem(item)

    def _addSeparator(self, subfolder: str):
        """
        Add a separator item with subfolder name.

        Args:
            subfolder: Name of the subfolder
        """
        # Create a separator item with special styling to span full width
        separator = QListWidgetItem(f"📁 {subfolder}")
        separator.setData(Qt.UserRole, None)  # Mark as separator (no image path)
        separator.setFlags(Qt.ItemIsEnabled)  # Make it non-selectable

        # Style the separator
        font = QFont()
        font.setBold(True)
        separator.setFont(font)

        # Make separator take full width by setting size hint
        # Use a large width to force it to span the entire row
        separator.setSizeHint(QSize(10000, 30))

        self.addItem(separator)

    def _onSelectionChanged(
        self, current: Optional[QListWidgetItem], previous: Optional[QListWidgetItem]
    ):
        """
        Handle selection change.

        Args:
            current: Currently selected item
            previous: Previously selected item
        """
        if current:
            imagePath = current.data(Qt.UserRole)
            # Only emit signal if it's an actual image (not a separator)
            if imagePath:
                self.imageSelected.emit(imagePath)

    def getSelectedImage(self) -> Optional[str]:
        """
        Get the currently selected image path.

        Returns:
            Selected image path or None
        """
        current = self.currentItem()
        if current:
            return current.data(Qt.UserRole)
        return None

    def selectImage(self, imagePath: str):
        """
        Select an image by path.

        Args:
            imagePath: Path to the image to select
        """
        for i in range(self.count()):
            item = self.item(i)
            if item.data(Qt.UserRole) == imagePath:
                self.setCurrentItem(item)
                break
