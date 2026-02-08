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
    imageSelected = Signal(str)  # image_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up the list widget
        self.setIconSize(QSize(100, 100))
        self.setViewMode(QListWidget.IconMode)
        self.setResizeMode(QListWidget.Adjust)
        self.setSpacing(10)
        self.setMovement(QListWidget.Static)
        
        # Connect selection signal
        self.currentItemChanged.connect(self._on_selection_changed)
        
        # Store image paths
        self._image_paths = []
    
    def load_images(self, image_paths: List[str], input_root: Optional[str] = None):
        """
        Load images into the thumbnail list.
        
        Args:
            image_paths: List of image file paths
            input_root: Root input folder path (for subfolder separators)
        """
        self.clear()
        self._image_paths = image_paths
        
        # Group images by subfolder if input_root is provided
        if input_root:
            groups = {}
            
            for img_path in image_paths:
                # Get relative path from input_root
                try:
                    rel_path = Path(img_path).relative_to(Path(input_root))
                    subfolder = str(rel_path.parent) if rel_path.parent != Path('.') else ''
                except ValueError:
                    # If image is not under input_root, use empty subfolder
                    subfolder = ''
                
                if subfolder not in groups:
                    groups[subfolder] = []
                groups[subfolder].append(img_path)
            
            # Add images with separators between subfolders
            for subfolder in sorted(groups.keys()):
                # Add separator if it's not the first group or if subfolder is not empty
                if subfolder:
                    self._add_separator(subfolder)
                
                # Add thumbnails for this subfolder
                for img_path in groups[subfolder]:
                    self._add_thumbnail(img_path)
        else:
            # No input_root, just add all images
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
    
    def _add_separator(self, subfolder: str):
        """
        Add a separator item with subfolder name.
        
        Args:
            subfolder: Name of the subfolder
        """
        # Create a separator item
        separator = QListWidgetItem(f"📁 {subfolder}")
        separator.setData(Qt.UserRole, None)  # Mark as separator (no image path)
        separator.setFlags(Qt.ItemIsEnabled)  # Make it non-selectable
        
        # Style the separator
        font = QFont()
        font.setBold(True)
        separator.setFont(font)
        
        self.addItem(separator)
    
    def _on_selection_changed(self, current: Optional[QListWidgetItem], previous: Optional[QListWidgetItem]):
        """
        Handle selection change.
        
        Args:
            current: Currently selected item
            previous: Previously selected item
        """
        if current:
            image_path = current.data(Qt.UserRole)
            # Only emit signal if it's an actual image (not a separator)
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
