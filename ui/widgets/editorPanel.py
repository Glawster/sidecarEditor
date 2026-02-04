"""
Editor panel widget for editing sidecar data.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QGroupBox, QMessageBox
)
from PySide6.QtCore import Signal
from typing import Optional
from ...src.sidecarCore import SidecarData, save_sidecar


class EditorPanel(QWidget):
    """Widget for editing sidecar prompt data."""
    
    # Signal emitted when sidecar is saved
    sidecarSaved = Signal(str)  # image_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._current_sidecar: Optional[SidecarData] = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Prompt section
        prompt_group = QGroupBox("Prompt")
        prompt_layout = QVBoxLayout(prompt_group)
        
        self._prompt_edit = QTextEdit()
        self._prompt_edit.setPlaceholderText("Enter the image generation prompt...")
        self._prompt_edit.setMinimumHeight(150)
        prompt_layout.addWidget(self._prompt_edit)
        
        layout.addWidget(prompt_group)
        
        # Negative prompt section
        neg_prompt_group = QGroupBox("Negative Prompt")
        neg_prompt_layout = QVBoxLayout(neg_prompt_group)
        
        self._neg_prompt_edit = QTextEdit()
        self._neg_prompt_edit.setPlaceholderText("Enter negative prompt (optional)...")
        self._neg_prompt_edit.setMinimumHeight(100)
        neg_prompt_layout.addWidget(self._neg_prompt_edit)
        
        layout.addWidget(neg_prompt_group)
        
        # Tags section (future enhancement - for now, just a label)
        # TODO: Add proper tag editing widget
        tags_label = QLabel("Tags: (Tag editing will be added in future version)")
        tags_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(tags_label)
        
        layout.addStretch()
        
        # Button bar
        button_bar = QHBoxLayout()
        button_bar.addStretch()
        
        self._save_button = QPushButton("Save Sidecar")
        self._save_button.clicked.connect(self._on_save)
        self._save_button.setEnabled(False)
        button_bar.addWidget(self._save_button)
        
        self._revert_button = QPushButton("Revert Changes")
        self._revert_button.clicked.connect(self._on_revert)
        self._revert_button.setEnabled(False)
        button_bar.addWidget(self._revert_button)
        
        layout.addLayout(button_bar)
        
        # Connect change signals
        self._prompt_edit.textChanged.connect(self._on_content_changed)
        self._neg_prompt_edit.textChanged.connect(self._on_content_changed)
    
    def load_sidecar(self, sidecar: SidecarData):
        """
        Load sidecar data into the editor.
        
        Args:
            sidecar: SidecarData to edit
        """
        self._current_sidecar = sidecar
        
        # Block signals while loading to avoid triggering change detection
        self._prompt_edit.blockSignals(True)
        self._neg_prompt_edit.blockSignals(True)
        
        self._prompt_edit.setPlainText(sidecar.prompt)
        self._neg_prompt_edit.setPlainText(sidecar.negative_prompt)
        
        self._prompt_edit.blockSignals(False)
        self._neg_prompt_edit.blockSignals(False)
        
        self._save_button.setEnabled(True)
        self._revert_button.setEnabled(False)
    
    def clear(self):
        """Clear the editor."""
        self._current_sidecar = None
        self._prompt_edit.clear()
        self._neg_prompt_edit.clear()
        self._save_button.setEnabled(False)
        self._revert_button.setEnabled(False)
    
    def _on_content_changed(self):
        """Handle content changes."""
        if self._current_sidecar:
            self._revert_button.setEnabled(True)
    
    def _on_save(self):
        """Handle save button click."""
        if not self._current_sidecar:
            return
        
        # Update sidecar with current values
        self._current_sidecar.prompt = self._prompt_edit.toPlainText()
        self._current_sidecar.negative_prompt = self._neg_prompt_edit.toPlainText()
        
        try:
            save_sidecar(self._current_sidecar, create_backup=True)
            self._revert_button.setEnabled(False)
            self.sidecarSaved.emit(self._current_sidecar.image_path)
            
            # Show success message
            QMessageBox.information(
                self,
                "Saved",
                f"Sidecar saved successfully.\nBackup created as .prompt.json.bak"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save sidecar:\n{str(e)}"
            )
    
    def _on_revert(self):
        """Handle revert button click."""
        if not self._current_sidecar:
            return
        
        reply = QMessageBox.question(
            self,
            "Revert Changes",
            "Discard all unsaved changes?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reload the original data
            self.load_sidecar(self._current_sidecar)
    
    def has_unsaved_changes(self) -> bool:
        """
        Check if there are unsaved changes.
        
        Returns:
            True if there are unsaved changes
        """
        return self._revert_button.isEnabled()
