"""
Editor panel widget for editing sidecar data.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional, Dict

from PySide6.QtCore import QFile, Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QMessageBox,
    QCheckBox,
    QPushButton,
)

from src.sidecarCore import SidecarData


class EditorPanel(QWidget):
    """Widget for editing sidecar prompt data."""

    sidecarSaved = Signal(str)  # imagePath

    def __init__(self, parent=None):
        super().__init__(parent)

        self._currentSidecar: Optional[SidecarData] = None
        self._setupUi()

    # ------------------------------------------------------------
    # UI setup
    # ------------------------------------------------------------

    def _setupUi(self):
        uiFilePath = Path(__file__).parent / "editorPanel.ui"

        loader = QUiLoader()
        uiFile = QFile(str(uiFilePath))
        if not uiFile.open(QFile.ReadOnly):  # type: ignore
            raise RuntimeError(f"Failed to open UI file: {uiFilePath}")

        self.ui = loader.load(uiFile, self)
        uiFile.close()

        if self.ui is None:
            raise RuntimeError(f"Failed to load UI file: {uiFilePath}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        # Positive prompt fields
        self._subjectPrompt: QTextEdit = self.ui.findChild(QTextEdit, "txtSubjectPrompt")  # type: ignore
        self._subjectRaw = ""
        self._posePrompt: QTextEdit = self.ui.findChild(QTextEdit, "txtPosePrompt")  # type: ignore
        self._poseRaw = ""
        self._clothingPrompt: QTextEdit = self.ui.findChild(QTextEdit, "txtClothingPrompt")  # type: ignore
        self._clothingRaw = ""
        self._lingeriePrompt: QTextEdit = self.ui.findChild(QTextEdit, "txtLingeriePrompt")  # type: ignore
        self._lingerieRaw = ""
        self._settingPrompt: QTextEdit = self.ui.findChild(QTextEdit, "txtSettingPrompt")  # type: ignore
        self._settingRaw = ""
        self._compositionPrompt: QTextEdit = self.ui.findChild(QTextEdit, "txtCompositionPrompt")  # type: ignore
        self._compositionRaw = ""

        # Negative
        self._negPromptEdit: QTextEdit = self.ui.findChild(QTextEdit, "txtNegativePrompt")  # type: ignore
        self._negStyleEdit: QTextEdit = self.ui.findChild(QTextEdit, "txtNegativeStyle")  # type: ignore

        # Status
        self._chkLocked: QCheckBox = self.ui.findChild(QCheckBox, "chkLocked")  # type: ignore
        self._chkReviewed: QCheckBox = self.ui.findChild(QCheckBox, "chkReviewed")  # type: ignore
        self._txtNotes: QTextEdit = self.ui.findChild(QTextEdit, "txtNotes")  # type: ignore

        # Buttons
        self._saveButton: QPushButton = self.ui.findChild(QPushButton, "btnSave")  # type: ignore
        self._revertButton: QPushButton = self.ui.findChild(QPushButton, "btnRevert")  # type: ignore
        self._generateButton: Optional[QPushButton] = self.ui.findChild(QPushButton, "btnGenerate")  # type: ignore

        missing = [
            name
            for name, w in {
                "txtSubjectPrompt": self._subjectPrompt,
                "txtPosePrompt": self._posePrompt,
                "txtClothingPrompt": self._clothingPrompt,
                "txtLingeriePrompt": self._lingeriePrompt,
                "txtSettingPrompt": self._settingPrompt,
                "txtCompositionPrompt": self._compositionPrompt,
                "txtNegativePrompt": self._negPromptEdit,
                "txtNegativeStyle": self._negStyleEdit,
                "chkLocked": self._chkLocked,
                "chkReviewed": self._chkReviewed,
                "txtNotes": self._txtNotes,
                "btnSave": self._saveButton,
                "btnRevert": self._revertButton,
            }.items()
            if w is None
        ]
        if missing:
            raise RuntimeError(f"Missing widgets in editorPanel.ui: {', '.join(missing)}")

        # Signals
        for w in (
            self._subjectPrompt, 
            self._posePrompt, 
            self._clothingPrompt, 
            self._lingeriePrompt, 
            self._settingPrompt, 
            self._compositionPrompt, 
            self._negPromptEdit, 
            self._negStyleEdit,
            self._txtNotes,
        ):
            w.textChanged.connect(self._onContentChanged)  # type: ignore

        self._chkLocked.stateChanged.connect(self._onContentChanged)  # type: ignore
        self._chkReviewed.stateChanged.connect(self._onContentChanged)  # type: ignore

        self._saveButton.clicked.connect(self._onSave)  # type: ignore
        self._revertButton.clicked.connect(self._onRevert)  # type: ignore

        if self._generateButton is not None:
            self._generateButton.clicked.connect(self._onGenerate)  # type: ignore

        self._saveButton.setEnabled(False)  # type: ignore
        self._revertButton.setEnabled(False)  # type: ignore

    # ------------------------------------------------------------
    # Sidecar load / clear
    # ------------------------------------------------------------

    def loadSidecar(self, sidecar: SidecarData):
        """
        Load sidecar data into the editor.
        Additionally reads the input-sidecar json and fills RAW fields.
        """
        self._currentSidecar = sidecar

        # Try to find & read the input-sidecar json
        inputData: Dict[str, Any] = {}
        try:
            inputSidecarPath = self._findSidecarPath(getattr(sidecar, "imagePath", ""))
            if inputSidecarPath:
                inputData = self._readJson(inputSidecarPath)
        except Exception:
            inputData = {}

        # Fill RAW fields from input-sidecar
        # - Subject raw: prefer positive.description
        # - Pose raw: positive.pose.raw
        # - Clothing raw: positive.clothing.raw
        # - Lingerie raw: positive.lingerie.raw
        # - Setting raw: positive.location.raw
        # - Composition raw: positive.camera.raw

        self._blockAll(True)

        # for each field get the prompt and raw text; if prompt is missing, fallback to 
        # raw for the prompt field (so at least something shows up in the UI)
        # subject is a bit special since it doesn't have a dedicated raw field, so we just use the description as raw too
        promptText = self._get(inputData, "positive.description") or ""
        self._subjectPrompt.setPlainText(promptText)
        self._subjectRaw = promptText  # no separate raw, so just mirror the prompt

        rawText = self._get(inputData, "positive.pose.raw") or ""
        promptText = self._get(inputData, "positive.pose.prompt") or ""
        if not promptText.strip():
             promptText = rawText  # fallback to raw if prompt is missing
        self._posePrompt.setPlainText(promptText)
        self._poseRaw = rawText

        rawText = self._get(inputData, "positive.clothing.raw") or ""
        promptText = self._get(inputData, "positive.clothing.prompt") or ""
        if not promptText.strip():
             promptText = rawText  # fallback to raw if prompt is missing
        self._clothingPrompt.setPlainText(promptText)
        self._clothingRaw = rawText

        rawText = self._get(inputData, "positive.lingerie.raw") or ""
        promptText = self._get(inputData, "positive.lingerie.prompt") or ""
        if not promptText.strip():
             promptText = rawText  # fallback to raw if prompt is missing
        self._lingeriePrompt.setPlainText(promptText)
        self._lingerieRaw = rawText

        rawText = self._get(inputData, "positive.location.raw") or ""
        promptText = self._get(inputData, "positive.location.prompt") or ""
        if not promptText.strip():
             promptText = rawText  # fallback to raw if prompt is missing
        self._settingPrompt.setPlainText(promptText)
        self._settingRaw = rawText

        rawText = self._get(inputData, "positive.camera.raw") or ""
        promptText = self._get(inputData, "positive.camera.prompt") or ""
        if not promptText.strip():
             promptText = rawText  # fallback to raw if prompt is missing
        self._compositionPrompt.setPlainText(promptText)
        self._compositionRaw = rawText

        self._blockAll(False)

        self._saveButton.setEnabled(True)  # type: ignore
        self._revertButton.setEnabled(False)  # type: ignore

    def clear(self):
        """Clear the editor."""
        self._currentSidecar = None

        self._blockAll(True)

        for w in (
            self._subjectPrompt, 
            self._posePrompt, 
            self._clothingPrompt, 
            self._lingeriePrompt, 
            self._settingPrompt, 
            self._compositionPrompt, 
            self._negPromptEdit, 
            self._negStyleEdit,
            self._txtNotes,
        ):
            w.clear()
        for w in (
            self._subjectRaw,
            self._poseRaw,
            self._clothingRaw,
            self._lingerieRaw,
            self._settingRaw,
            self._compositionRaw
        ):
            w = ""

        self._chkLocked.setChecked(False)
        self._chkReviewed.setChecked(False)

        self._blockAll(False)

        self._saveButton.setEnabled(False)  # type: ignore
        self._revertButton.setEnabled(False)  # type: ignore

    # ------------------------------------------------------------
    # Save / revert (kept minimal for now)
    # ------------------------------------------------------------

    def saveCurrentSidecar(self) -> bool:
        """Save the currently loaded sidecar. Returns True if saved."""
        if not self._currentSidecar:
            return False

        try:
            # For now we are NOT writing raw fields into the prompt-sidecar object yet.
            # Next step will map UI -> SidecarData structured fields.
            self._saveSidecar(self._currentSidecar, createBackup=True)
            self._revertButton.setEnabled(False)  # type: ignore
            self.sidecarSaved.emit(getattr(self._currentSidecar, "imagePath", ""))
            return True
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save sidecar:\n{e}")
            return False

    def hasUnsavedChanges(self) -> bool:
        return self._revertButton.isEnabled()  # type: ignore

    # ------------------------------------------------------------
    # Events
    # ------------------------------------------------------------

    def _onContentChanged(self):
        if self._currentSidecar:
            self._revertButton.setEnabled(True)  # type: ignore

    def _onGenerate(self):
        QMessageBox.information(self, "Generate", "Generate is not wired yet.")

    def _onSave(self):
        self.saveCurrentSidecar()

    def _saveSidecar(self, sidecar: SidecarData, createBackup: bool = True):
        """
        Save sidecar data to disk.

        Args:
            sidecar: SidecarData to save
            createBackup: If True, create .bak backup before saving
        """
        sidecarPath = self._findSidecarPath(sidecar.imagePath)

        # Create backup if file exists
        if createBackup and sidecarPath.exists():
            backupPath = Path(str(sidecarPath) + ".bak")
            try:
                backupPath.write_bytes(sidecarPath.read_bytes())
            except IOError as e:
                print(f"Warning: Could not create backup {backupPath}: {e}")

        # Save the sidecar
        try:
            with open(sidecarPath, "w", encoding="utf-8") as f:
                json.dump(sidecar.toDict(), f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error: Could not save sidecar {sidecarPath}: {e}")
            raise

    def _onRevert(self):
        if not self._currentSidecar:
            return

        reply = QMessageBox.question(
            self,
            "Revert Changes",
            "Discard all unsaved changes?",
            QMessageBox.Yes | QMessageBox.No,  # type: ignore
            QMessageBox.No,  # type: ignore
        )
        if reply == QMessageBox.Yes:  # type: ignore
            self.loadSidecar(self._currentSidecar)

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------

    def _blockAll(self, blocked: bool):
        for w in (
            self._subjectPrompt, 
            self._posePrompt, 
            self._clothingPrompt, 
            self._lingeriePrompt, 
            self._settingPrompt, 
            self._compositionPrompt, 
            self._negPromptEdit, 
            self._negStyleEdit,
            self._txtNotes,
        ):
            w.blockSignals(blocked)  # type: ignore

        self._chkLocked.blockSignals(blocked)  # type: ignore
        self._chkReviewed.blockSignals(blocked)  # type: ignore

    def _findSidecarPath(self, imagePath: str) -> Optional[Path]:
        """
        Try a few common patterns:
        - same folder: input.prompt.json
        - alongside image: <stem>.prompt.json
        - alongside image: <filename>.prompt.json (e.g. clothed-142.png.prompt.json)
        """
        if not imagePath:
            return None

        p = Path(imagePath)
        candidates = [
            p.parent / "input.prompt.json",
            p.with_suffix(".prompt.json"),
            Path(str(p) + ".prompt.json"),
        ]
        for c in candidates:
            if c.exists() and c.is_file():
                return c
        return None

    def _readJson(self, path: Path) -> Dict[str, Any]:
        try:
            txt = path.read_text(encoding="utf-8")
            obj = json.loads(txt)
            return obj if isinstance(obj, dict) else {}
        except Exception:
            return {}

    def _get(self, obj: Dict[str, Any], dottedPath: str) -> Any:
        """
        Safe dotted getter for dicts.
        Example: _get(data, "positive.pose.raw")
        """
        cur: Any = obj
        for part in dottedPath.split("."):
            if not isinstance(cur, dict):
                return None
            cur = cur.get(part)
        return cur

    def _backupFile(self, path: Path) -> None:
        if path.exists():
            bak = Path(str(path) + ".bak")
            bak.write_bytes(path.read_bytes())

    def _assemblePositivePrompt(self) -> str:
        # Simple comma-join of non-empty fields (you can tune ordering later)
        parts = [
            self._subjectPrompt.toPlainText().strip(),
            self._posePrompt.toPlainText().strip(),
            self._clothingPrompt.toPlainText().strip(),
            self._lingeriePrompt.toPlainText().strip(),
            self._settingPrompt.toPlainText().strip(),
            self._compositionPrompt.toPlainText().strip(),
        ]
        parts = [p for p in parts if p]
        return ", ".join(parts)

    def _assembleNegativePrompt(self) -> str:
        # Simple comma-join of negative prompt and style (you can tune ordering later)
        parts = [
            self._negPromptEdit.toPlainText().strip(),
            self._negStyleEdit.toPlainText().strip(),
        ]
        parts = [p for p in parts if p]
        return ", ".join(parts)