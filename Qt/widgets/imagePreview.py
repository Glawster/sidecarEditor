"""
Image preview widget with original/output toggle.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from typing import Optional


class ImagePreview(QWidget):
    """Widget for displaying image preview with original/output toggle."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._original_path: Optional[str] = None
        self._output_path: Optional[str] = None
        self._showing_original = True
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Control bar
        control_bar = QHBoxLayout()
        
        self._status_label = QLabel("No image selected")
        control_bar.addWidget(self._status_label)
        
        control_bar.addStretch()
        
        self._toggle_button = QPushButton("Show Output")
        self._toggle_button.clicked.connect(self._on_toggle)
        self._toggle_button.setEnabled(False)
        control_bar.addWidget(self._toggle_button)
        
        layout.addLayout(control_bar)
        
        # Image display
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignCenter)
        self._image_label.setMinimumSize(400, 400)
        self._image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._image_label.setScaledContents(False)
        self._image_label.setStyleSheet("QLabel { background-color: #2b2b2b; }")
        layout.addWidget(self._image_label)
    
    def set_images(self, original_path: str, output_path: Optional[str] = None):
        """
        Set the images to display.
        
        Args:
            original_path: Path to original image
            output_path: Path to output image (optional)
        """
        self._original_path = original_path
        self._output_path = output_path
        self._showing_original = True
        
        # Update toggle button state
        if output_path:
            self._toggle_button.setEnabled(True)
            self._toggle_button.setText("Show Output")
        else:
            self._toggle_button.setEnabled(False)
            self._toggle_button.setText("Show Output (Not Available)")
        
        # Display the original image
        self._display_image(original_path)
        self._update_status()
    
    def _display_image(self, image_path: str):
        """
        Display an image.
        
        Args:
            image_path: Path to the image file
        """
        pixmap = QPixmap(image_path)
        
        if pixmap.isNull():
            self._image_label.setText(f"Could not load image:\n{image_path}")
            return
        
        # Scale to fit widget while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            self._image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        self._image_label.setPixmap(scaled_pixmap)
    
    def _on_toggle(self):
        """Handle toggle button click."""
        if not self._output_path:
            return
        
        self._showing_original = not self._showing_original
        
        if self._showing_original:
            self._display_image(self._original_path)
            self._toggle_button.setText("Show Output")
        else:
            self._display_image(self._output_path)
            self._toggle_button.setText("Show Original")
        
        self._update_status()
    
    def _update_status(self):
        """Update the status label."""
        import os
        
        if self._showing_original:
            status = f"Original: {os.path.basename(self._original_path)}"
        else:
            status = f"Output: {os.path.basename(self._output_path)}"
        
        self._status_label.setText(status)
    
    def clear(self):
        """Clear the displayed image."""
        self._original_path = None
        self._output_path = None
        self._showing_original = True
        self._image_label.clear()
        self._image_label.setText("No image selected")
        self._status_label.setText("No image selected")
        self._toggle_button.setEnabled(False)
        self._toggle_button.setText("Show Output")
    
    def resizeEvent(self, event):
        """Handle resize events to re-scale the image."""
        super().resizeEvent(event)
        
        # Re-display current image at new size
        if self._original_path:
            current_path = self._output_path if not self._showing_original and self._output_path else self._original_path
            self._display_image(current_path)
