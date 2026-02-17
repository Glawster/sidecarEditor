"""
Editor panel widget for editing sidecar data.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QCheckBox,
)
from PySide6.QtCore import QFile, Signal
from PySide6.QtUiTools import QUiLoader

from typing import Optional
from pathlib import Path

from src.sidecarCore import SidecarData, saveSidecar


class EditorPanel(QWidget):
    """Widget for editing sidecar prompt data."""

    # Signal emitted when sidecar is saved
    sidecarSaved = Signal(str)  # imagePath

    def __init__(self, parent=None):
        super().__init__(parent)

        self._currentSidecar: Optional[SidecarData] = None
        self._setupUi()

    def _setupUi(self):
        """Set up the user interface by loading from .ui file."""
        uiFilePath = Path(__file__).parent / "editorPanel.ui"

        loader = QUiLoader()
        uiFile = QFile(str(uiFilePath))
        if not uiFile.open(QFile.ReadOnly):  # type: ignore
            raise RuntimeError(f"Failed to open UI file: {uiFilePath}")

        self.ui = loader.load(uiFile, self)
        uiFile.close()

        if self.ui is None:
            raise RuntimeError(f"Failed to load UI file: {uiFilePath}")

        # Embed the loaded UI into this widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        # Grab widgets by objectName (must match Qt Designer objectName)
        self._subjectPrompt: QTextEdit = self.ui.findChild(QTextEdit, "txtSubjectPrompt")  # type: ignore
        self._subjectRaw: QTextEdit = self.ui.findChild(QTextEdit, "txtSubjectRaw")  # type: ignore
        self._posePrompt: QTextEdit = self.ui.findChild(QTextEdit, "txtPosePrompt")  # type: ignore
        self._poseRaw: QTextEdit = self.ui.findChild(QTextEdit, "txtPoseRaw")  # type: ignore
        self._clothingPrompt: QTextEdit = self.ui.findChild(QTextEdit, "txtClothingPrompt")  # type: ignore
        self._clothingRaw: QTextEdit = self.ui.findChild(QTextEdit, "txtClothingRaw")  # type: ignore
        self._lingeriePrompt: QTextEdit = self.ui.findChild(QTextEdit, "txtLingeriePrompt")  # type: ignore
        self._lingerieRaw: QTextEdit = self.ui.findChild(QTextEdit, "txtLingerieRaw")  # type: ignore
        self._settingPrompt: QTextEdit = self.ui.findChild(QTextEdit, "txtSettingPrompt")  # type: ignore
        self._settingRaw: QTextEdit = self.ui.findChild(QTextEdit, "txtSettingRaw")  # type: ignore
        self._compositionPrompt: QTextEdit = self.ui.findChild(QTextEdit, "txtCompositionPrompt")  # type: ignore
        self._compositionRaw: QTextEdit = self.ui.findChild(QTextEdit, "txtCompositionRaw")  # type: ignore

        # Negative
        self._negPromptEdit: QTextEdit = self.ui.findChild(QTextEdit, "txtNegativePrompt")  # type: ignore
        self._negStyleEdit: QTextEdit = self.ui.findChild(QTextEdit, "txtNegativeStyle")  # type: ignore

        # Status
        self._chkLocked: QCheckBox = self.ui.findChild(QCheckBox, "chkLocked")  # type: ignore
        self._chkReviewed: QCheckBox = self.ui.findChild(QCheckBox, "chkReviewed")  # type: ignore
        self._txtNotes: QTextEdit = self.ui.findChild(QTextEdit, "txtNotes")  # type: ignore

        self._generateButton: QPushButton = self.ui.findChild(QPushButton, "btnGenerate")  # type: ignore
        self._saveButton: QPushButton = self.ui.findChild(QPushButton, "btnSave")  # type: ignore
        self._revertButton: QPushButton = self.ui.findChild(QPushButton, "btnRevert")  # type: ignore

        missing = [
            name
            for name, w in {
                "txtSubjectPrompt": self._subjectPrompt,
                "txtSubjectRaw": self._subjectRaw,
                "txtPosePrompt": self._posePrompt,
                "txtPoseRaw": self._poseRaw,
                "txtClothingPrompt": self._clothingPrompt,
                "txtClothingRaw": self._clothingRaw,
                "txtLingeriePrompt": self._lingeriePrompt,
                "txtLingerieRaw": self._lingerieRaw,
                "txtSettingPrompt": self._settingPrompt,
                "txtSettingRaw": self._settingRaw,
                "txtCompositionPrompt": self._compositionPrompt,
                "txtCompositionRaw": self._compositionRaw,
                "txtNegativePrompt": self._negPromptEdit,
                "txtNegativeStyle": self._negStyleEdit,
                "chkLocked": self._chkLocked,
                "chkReviewed": self._chkReviewed,
                "txtNotes": self._txtNotes,
                "btnGenerate": self._generateButton,
                "btnSave": self._saveButton,
                "btnRevert": self._revertButton,
            }.items()
            if w is None
        ]
        if missing:
            raise RuntimeError(
                f"Missing widgets in editorPanel.ui: {', '.join(missing)}"
            )

        # Wire signals (same behaviour as before)
        self._subjectPrompt.textChanged.connect(self._onContentChanged)  # type: ignore
        self._subjectRaw.textChanged.connect(self._onContentChanged)  # type: ignore
        self._posePrompt.textChanged.connect(self._onContentChanged)  # type: ignore
        self._poseRaw.textChanged.connect(self._onContentChanged)  # type: ignore
        self._clothingPrompt.textChanged.connect(self._onContentChanged)  # type: ignore
        self._clothingRaw.textChanged.connect(self._onContentChanged)  # type: ignore
        self._lingeriePrompt.textChanged.connect(self._onContentChanged)  # type: ignore
        self._lingerieRaw.textChanged.connect(self._onContentChanged)  # type: ignore
        self._settingPrompt.textChanged.connect(self._onContentChanged)  # type: ignore
        self._settingRaw.textChanged.connect(self._onContentChanged)  # type: ignore
        self._compositionPrompt.textChanged.connect(self._onContentChanged)  # type: ignore
        self._compositionRaw.textChanged.connect(self._onContentChanged) # type: ignore
        self._chkLocked.stateChanged.connect(self._onContentChanged)  # type: ignore
        self._chkReviewed.stateChanged.connect(self._onContentChanged)  # type: ignore
        self._txtNotes.textChanged.connect(self._onContentChanged)  # type: ignore
        self._saveButton.clicked.connect(self._onSave)  # type: ignore
        self._revertButton.clicked.connect(self._onRevert)  # type: ignore
        self._generateButton.clicked.connect(self._onGenerate)  # type: ignore

    def loadSidecar(self, sidecar: SidecarData):
        """
        Load sidecar data into the editor.

        Args:
            sidecar: SidecarData to edit
        """
        self._currentSidecar = sidecar

        # Block signals while loading to avoid triggering change detection
        self._saveButton.setEnabled(True)  # type: ignore
        self._revertButton.setEnabled(False)  # type: ignore

    def clear(self):
        """Clear the editor."""
        self._currentSidecar = None
        self._promptEdit.clear()  # type: ignore
        self._negPromptEdit.clear()  # type: ignore
        self._saveButton.setEnabled(False)  # type: ignore
        self._revertButton.setEnabled(False)  # type: ignore

    def saveCurrentSidecar(self) -> bool:
        """Save the currently loaded sidecar. Returns True if saved."""
        if not self._currentSidecar:
            return False

        # Whatever your current “collect values from UI” logic is:
        self._currentSidecar.prompt = self._promptEdit.toPlainText()  # type: ignore
        self._currentSidecar.negativePrompt = self._negPromptEdit.toPlainText()  # type: ignore

        try:
            saveSidecar(self._currentSidecar, createBackup=True)
            self._revertButton.setEnabled(False)  # type: ignore
            self.sidecarSaved.emit(self._currentSidecar.imagePath)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save sidecar:\n{e}")
            return False

    def hasUnsavedChanges(self) -> bool:
        """
        Check if there are unsaved changes.

        Returns:
            True if there are unsaved changes
        """
        return self._revertButton.isEnabled()  # type: ignore

    def _onContentChanged(self):
        """Handle content changes."""
        if self._currentSidecar:
            self._revertButton.setEnabled(True)
    
    def _onGenerate(self):
        """Handle generate button click."""
        QMessageBox.information(self, "Generate", "This would trigger image generation based on prompt text entered here.")

    def _onSave(self):
        """Handle save button click."""
        self.saveCurrentSidecar()

    def _onRevert(self):
        """Handle revert button click."""
        if not self._currentSidecar:
            return

        reply = QMessageBox.question(
            self,
            "Revert Changes",
            "Discard all unsaved changes?",
            QMessageBox.Yes | QMessageBox.No, # type: ignore
            QMessageBox.No, # type: ignore
        )

        if reply == QMessageBox.Yes: # type: ignore
            # Reload the original data
            self.loadSidecar(self._currentSidecar) # type: ignore
