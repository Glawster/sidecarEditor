"""
Thumbnail list widget for displaying images.
"""

from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QIcon
from typing import List, Optional


class ThumbnailList(QListWidget):
    """List widget that displays image thumbnails."""
    
    # Signal emitted when an image is selected
    imageSelected = Signal(str)  # image_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up the list widget
        self.setIconSize(Qt.QSize(100, 100))
        self.setViewMode(QListWidget.IconMode)
        self.setResizeMode(QListWidget.Adjust)
        self.setSpacing(10)
        self.setMovement(QListWidget.Static)
        
        # Connect selection signal
        self.currentItemChanged.connect(self._on_selection_changed)
        
        # Store image paths
        self._image_paths = []
    
    def load_images(self, image_paths: List[str]):
        """
        Load images into the thumbnail list.
        
        Args:
            image_paths: List of image file paths
        """
        self.clear()
        self._image_paths = image_paths
        
        for img_path in image_paths:
            self._add_thumbnail(img_path)
    
    def _add_thumbnail(self, image_path: str):
        """
        Add a single thumbnail to the list.
        
        Args:
            image_path: Path to the image file
        """
        import os
        
        # Create thumbnail
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            # If image can't be loaded, use a placeholder
            pixmap = QPixmap(100, 100)
            pixmap.fill(Qt.gray)
        
        # Scale to thumbnail size
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Create list item
        item = QListWidgetItem(QIcon(pixmap), os.path.basename(image_path))
        item.setData(Qt.UserRole, image_path)  # Store full path
        self.addItem(item)
    
    def _on_selection_changed(self, current: Optional[QListWidgetItem], previous: Optional[QListWidgetItem]):
        """
        Handle selection change.
        
        Args:
            current: Currently selected item
            previous: Previously selected item
        """
        if current:
            image_path = current.data(Qt.UserRole)
            if image_path:
                self.imageSelected.emit(image_path)
    
    def get_selected_image(self) -> Optional[str]:
        """
        Get the currently selected image path.
        
        Returns:
            Selected image path or None
        """
        current = self.currentItem()
        if current:
            return current.data(Qt.UserRole)
        return None
    
    def select_image(self, image_path: str):
        """
        Select an image by path.
        
        Args:
            image_path: Path to the image to select
        """
        for i in range(self.count()):
            item = self.item(i)
            if item.data(Qt.UserRole) == image_path:
                self.setCurrentItem(item)
                break
