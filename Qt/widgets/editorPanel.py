"""
Editor panel widget for editing sidecar data.
"""

from __future__ import annotations

import json
import subprocess
import sys
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

import src.sidecarConfig as sidecarConfig
from src.sidecarCore import SidecarData, saveSidecar


class EditorPanel(QWidget):
    """Widget for editing sidecar prompt data."""

    sidecarSaved = Signal(str)   # imagePath
    generateStarted = Signal(str)  # status message

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

        # Buttons
        self._saveButton: QPushButton = self.ui.findChild(QPushButton, "btnSave")  # type: ignore
        self._revertButton: QPushButton = self.ui.findChild(QPushButton, "btnRevert")  # type: ignore
        self._generateButton: Optional[QPushButton] = self.ui.findChild(QPushButton, "btnGenerate")  # type: ignore

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
                "btnSave": self._saveButton,
                "btnRevert": self._revertButton,
            }.items()
            if w is None
        ]
        if missing:
            raise RuntimeError(f"Missing widgets in editorPanel.ui: {', '.join(missing)}")

        # Signals
        for w in (
            self._subjectPrompt, self._subjectRaw,
            self._posePrompt, self._poseRaw,
            self._clothingPrompt, self._clothingRaw,
            self._lingeriePrompt, self._lingerieRaw,
            self._settingPrompt, self._settingRaw,
            self._compositionPrompt, self._compositionRaw,
            self._negPromptEdit, self._negStyleEdit,
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
            inputSidecarPath = self._findInputSidecarPath(getattr(sidecar, "imagePath", ""))
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
        rawSubject = self._get(inputData, "positive.description") or ""
        rawPose = self._get(inputData, "positive.pose.raw") or ""
        rawClothing = self._get(inputData, "positive.clothing.raw") or ""
        rawLingerie = self._get(inputData, "positive.lingerie.raw") or ""
        rawSetting = self._get(inputData, "positive.location.raw") or ""
        rawComposition = self._get(inputData, "positive.camera.raw") or ""

        # Block signals while populating
        self._blockAll(True)

        # Raw fields (this is what you asked for)
        self._subjectRaw.setPlainText(rawSubject)
        self._poseRaw.setPlainText(rawPose)
        self._clothingRaw.setPlainText(rawClothing)
        self._lingerieRaw.setPlainText(rawLingerie)
        self._settingRaw.setPlainText(rawSetting)
        self._compositionRaw.setPlainText(rawComposition)

        # Prompt fields: leave as-is (blank by default); later we’ll bind these to prompt json.
        # Negative/status/notes: also leave as-is for now.

        self._blockAll(False)

        self._saveButton.setEnabled(True)  # type: ignore
        self._revertButton.setEnabled(False)  # type: ignore

    def clear(self):
        """Clear the editor."""
        self._currentSidecar = None

        self._blockAll(True)

        for w in (
            self._subjectPrompt, self._subjectRaw,
            self._posePrompt, self._poseRaw,
            self._clothingPrompt, self._clothingRaw,
            self._lingeriePrompt, self._lingerieRaw,
            self._settingPrompt, self._settingRaw,
            self._compositionPrompt, self._compositionRaw,
            self._negPromptEdit, self._negStyleEdit,
            self._txtNotes,
        ):
            w.clear()

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
            saveSidecar(self._currentSidecar, createBackup=True)
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

        scriptPath = sidecarConfig.getTxt2ImgScriptPath()
        if not scriptPath:
            QMessageBox.information(
                self,
                "Generate",
                "txt2imgComfy.py is not configured.\n\n"
                "Set 'txt2ImgScriptPath' in your kohyaConfig.json to the path of\n"
                "txt2imgComfy.py from the linuxMigration repository.\n\n"
                "Also set your RunPod Pod ID via the 'Set RunPod ID' button in the\n"
                "top bar (the preferred way to connect to ComfyUI).",
            )
            return

        if not Path(scriptPath).exists():
            QMessageBox.warning(
                self,
                "Generate",
                f"Script not found:\n{scriptPath}\n\n"
                "Check 'txt2ImgScriptPath' in your kohyaConfig.json.",
            )
            return

        # RunPod is the preferred remote target; fall back to a local URL if set.
        runpodPodId = sidecarConfig.getRunpodPodId()
        comfyUrl = sidecarConfig.getComfyUrl()
        cmd = [sys.executable, scriptPath]
        if runpodPodId:
            cmd += ["--remote", runpodPodId]
        elif comfyUrl:
            cmd += ["--local", comfyUrl]
        else:
            reply = QMessageBox.question(
                self,
                "Generate",
                "No RunPod Pod ID or ComfyUI URL is configured.\n\n"
                "Set a RunPod Pod ID via the 'Set RunPod ID' button in the top bar,\n"
                "or add 'comfyUrl' to your kohyaConfig.json.\n\n"
                "Proceed anyway (using the script's own config)?",
                QMessageBox.Yes | QMessageBox.No,  # type: ignore
                QMessageBox.No,  # type: ignore
            )
            if reply != QMessageBox.Yes:  # type: ignore
                return

        try:
            subprocess.Popen(cmd, shell=False)  # non-blocking: script runs in background
            self.generateStarted.emit(f"Generation started: {Path(scriptPath).name}")
        except OSError as e:
            QMessageBox.critical(self, "Generate Error", f"Failed to start generation:\n{e}")

    def _onSave(self):
        self.saveCurrentSidecar()

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
            self._subjectPrompt, self._subjectRaw,
            self._posePrompt, self._poseRaw,
            self._clothingPrompt, self._clothingRaw,
            self._lingeriePrompt, self._lingerieRaw,
            self._settingPrompt, self._settingRaw,
            self._compositionPrompt, self._compositionRaw,
            self._negPromptEdit, self._negStyleEdit,
            self._txtNotes,
        ):
            w.blockSignals(blocked)  # type: ignore
        self._chkLocked.blockSignals(blocked)  # type: ignore
        self._chkReviewed.blockSignals(blocked)  # type: ignore

    def _findInputSidecarPath(self, imagePath: str) -> Optional[Path]:
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
