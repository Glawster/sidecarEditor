"""
Editor panel widget for editing sidecar data.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QGroupBox,
    QMessageBox,
)
from PySide6.QtCore import Signal
from typing import Optional
from ...src.sidecarCore import SidecarData, saveSidecar


class EditorPanel(QWidget):
    """Widget for editing sidecar prompt data."""

    # Signal emitted when sidecar is saved
    sidecarSaved = Signal(str)  # imagePath

    def __init__(self, parent=None):
        super().__init__(parent)

        self._currentSidecar: Optional[SidecarData] = None
        self._setupUi()

    def _setupUi(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Prompt section
        promptGroup = QGroupBox("Prompt")
        promptLayout = QVBoxLayout(promptGroup)

        self._promptEdit = QTextEdit()
        self._promptEdit.setPlaceholderText("Enter the image generation prompt...")
        self._promptEdit.setMinimumHeight(150)
        promptLayout.addWidget(self._promptEdit)

        layout.addWidget(promptGroup)

        # Negative prompt section
        negPromptGroup = QGroupBox("Negative Prompt")
        negPromptLayout = QVBoxLayout(negPromptGroup)

        self._negPromptEdit = QTextEdit()
        self._negPromptEdit.setPlaceholderText("Enter negative prompt (optional)...")
        self._negPromptEdit.setMinimumHeight(100)
        negPromptLayout.addWidget(self._negPromptEdit)

        layout.addWidget(negPromptGroup)

        # Tags section (future enhancement - for now, just a label)
        # TODO: Add proper tag editing widget
        tagsLabel = QLabel("Tags: (Tag editing will be added in future version)")
        tagsLabel.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(tagsLabel)

        layout.addStretch()

        # Button bar
        buttonBar = QHBoxLayout()
        buttonBar.addStretch()

        self._saveButton = QPushButton("Save Sidecar")
        self._saveButton.clicked.connect(self._onSave)
        self._saveButton.setEnabled(False)
        buttonBar.addWidget(self._saveButton)

        self._revertButton = QPushButton("Revert Changes")
        self._revertButton.clicked.connect(self._onRevert)
        self._revertButton.setEnabled(False)
        buttonBar.addWidget(self._revertButton)

        layout.addLayout(buttonBar)

        # Connect change signals
        self._promptEdit.textChanged.connect(self._onContentChanged)
        self._negPromptEdit.textChanged.connect(self._onContentChanged)

    def loadSidecar(self, sidecar: SidecarData):
        """
        Load sidecar data into the editor.

        Args:
            sidecar: SidecarData to edit
        """
        self._currentSidecar = sidecar

        # Block signals while loading to avoid triggering change detection
        self._promptEdit.blockSignals(True)
        self._negPromptEdit.blockSignals(True)

        self._promptEdit.setPlainText(sidecar.prompt)
        self._negPromptEdit.setPlainText(sidecar.negativePrompt)

        self._promptEdit.blockSignals(False)
        self._negPromptEdit.blockSignals(False)

        self._saveButton.setEnabled(True)
        self._revertButton.setEnabled(False)

    def clear(self):
        """Clear the editor."""
        self._currentSidecar = None
        self._promptEdit.clear()
        self._negPromptEdit.clear()
        self._saveButton.setEnabled(False)
        self._revertButton.setEnabled(False)

    def _onContentChanged(self):
        """Handle content changes."""
        if self._currentSidecar:
            self._revertButton.setEnabled(True)

    def _onSave(self):
        """Handle save button click."""
        if not self._currentSidecar:
            return

        # Update sidecar with current values
        self._currentSidecar.prompt = self._promptEdit.toPlainText()
        self._currentSidecar.negativePrompt = self._negPromptEdit.toPlainText()

        try:
            saveSidecar(self._currentSidecar, createBackup=True)
            self._revertButton.setEnabled(False)
            self.sidecarSaved.emit(self._currentSidecar.imagePath)

            # Show success message
            QMessageBox.information(
                self,
                "Saved",
                f"Sidecar saved successfully.\nBackup created as .prompt.json.bak",
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Save Error", f"Failed to save sidecar:\n{str(e)}"
            )

    def _onRevert(self):
        """Handle revert button click."""
        if not self._currentSidecar:
            return

        reply = QMessageBox.question(
            self,
            "Revert Changes",
            "Discard all unsaved changes?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Reload the original data
            self.loadSidecar(self._currentSidecar)

    def hasUnsavedChanges(self) -> bool:
        """
        Check if there are unsaved changes.

        Returns:
            True if there are unsaved changes
        """
        return self._revertButton.isEnabled()
