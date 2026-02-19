"""
Editor panel widget for editing sidecar data.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
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
from src.sidecarConfig import getNegativePrompt, setNegativePrompt


class EditorPanel(QWidget):
    """Widget for editing sidecar prompt data."""

    # note we also use "description" as a key but it is not part of FIELD_NAMES
    FIELD_NAMES = [
        "subject",
        "pose",
        "clothing",
        "lingerie",
        "setting",
        "composition",
    ]

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

        self._promptText: Dict[str, QTextEdit] = {}
        self._rawText = {name: "" for name in self.FIELD_NAMES}

        # Positive prompt fields
        self._promptText["description"]: QTextEdit = self.ui.findChild(QTextEdit, "txtDescriptionPrompt")  # type: ignore
        self._promptText["subject"]: QTextEdit = self.ui.findChild(QTextEdit, "txtSubjectPrompt")  # type: ignore
        self._promptText["pose"]: QTextEdit = self.ui.findChild(QTextEdit, "txtPosePrompt")  # type: ignore
        self._promptText["clothing"]: QTextEdit = self.ui.findChild(QTextEdit, "txtClothingPrompt")  # type: ignore
        self._promptText["lingerie"]: QTextEdit = self.ui.findChild(QTextEdit, "txtLingeriePrompt")  # type: ignore
        self._promptText["setting"]: QTextEdit = self.ui.findChild(QTextEdit, "txtSettingPrompt")  # type: ignore
        self._promptText["composition"]: QTextEdit = self.ui.findChild(QTextEdit, "txtCompositionPrompt")  # type: ignore

        # Negative
        self._negGeneralText: QTextEdit = self.ui.findChild(QTextEdit, "txtNegativePrompt")  # type: ignore
        self._negStyleText: QTextEdit = self.ui.findChild(QTextEdit, "txtNegativeStyle")  # type: ignore

        # Status
        self._chkLocked: QCheckBox = self.ui.findChild(QCheckBox, "chkLocked")  # type: ignore
        self._chkReviewed: QCheckBox = self.ui.findChild(QCheckBox, "chkReviewed")  # type: ignore
        self._txtNotes: QTextEdit = self.ui.findChild(QTextEdit, "txtNotes")  # type: ignore

        # Buttons
        self._saveButton: QPushButton = self.ui.findChild(QPushButton, "btnSave")  # type: ignore
        self._revertButton: QPushButton = self.ui.findChild(QPushButton, "btnRevert")  # type: ignore
        self._generateButton: Optional[QPushButton] = self.ui.findChild(QPushButton, "btnGenerate")  # type: ignore
        self._updateRawButton: Optional[QPushButton] = self.ui.findChild(QPushButton, "btnUpdateRaw")  # type: ignore
        self._sendToLingerieButton: Optional[QPushButton] = self.ui.findChild(QPushButton, "btnSendToLingerie")  # type: ignore

        missing = [
            name
            for name, w in {
                "txtDescriptionPrompt": self._promptText["description"],
                "txtSubjectPrompt": self._promptText["subject"],
                "txtPosePrompt": self._promptText["pose"],
                "txtClothingPrompt": self._promptText["clothing"],
                "txtLingeriePrompt": self._promptText["lingerie"],
                "txtSettingPrompt": self._promptText["setting"],
                "txtCompositionPrompt": self._promptText["composition"],
                "txtNegativePrompt": self._negGeneralText,
                "txtNegativeStyle": self._negStyleText,
                "chkLocked": self._chkLocked,
                "chkReviewed": self._chkReviewed,
                "txtNotes": self._txtNotes,
                "btnSave": self._saveButton,
                "btnRevert": self._revertButton,
                "btnSendToLingerie": self._sendToLingerieButton,
            }.items()
            if w is None
        ]
        if missing:
            raise RuntimeError(
                f"Missing widgets in editorPanel.ui: {', '.join(missing)}"
            )

        # Signals
        for w in (
            self._promptText["description"],
            self._promptText["subject"],
            self._promptText["pose"],
            self._promptText["clothing"],
            self._promptText["lingerie"],
            self._promptText["setting"],
            self._promptText["composition"],
            self._negGeneralText,
            self._negStyleText,
            self._txtNotes,
        ):
            w.textChanged.connect(self._onContentChanged)  # type: ignore

        self._chkLocked.stateChanged.connect(self._onContentChanged)  # type: ignore
        self._chkReviewed.stateChanged.connect(self._onContentChanged)  # type: ignore

        self._saveButton.clicked.connect(self._onSave)  # type: ignore
        self._revertButton.clicked.connect(self._onRevert)  # type: ignore

        if self._generateButton is not None:
            self._generateButton.clicked.connect(self._onGenerate)  # type: ignore

        if self._updateRawButton is not None:
            self._updateRawButton.clicked.connect(self._onUpdateRaw)  # type: ignore

        if self._sendToLingerieButton is not None:
            self._sendToLingerieButton.clicked.connect(self._onSendToLingerie)  # type: ignore

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

        self._blockAll(True)

        # for each field get the prompt and raw text; if prompt is missing, fallback to
        # raw for the prompt field (so at least something shows up in the UI)
        # subject is a bit special since it doesn't have a dedicated raw field, so we just use the description as raw too
        positive = inputData.get("positive", {})
        promptText = positive.get("description", "") or ""
        self._promptText["description"].setPlainText(promptText)  # type: ignore

        for field in self.FIELD_NAMES:
            node = positive.get(field, {}) or {}
            rawText = node.get("raw", "") or ""
            promptText = node.get("prompt", "") or ""
            if not promptText.strip():
                promptText = rawText
            self._rawText[field] = rawText
            self._promptText[field].setPlainText(promptText)  # type: ignore

        # read the negative general prompt from the config file
        #  comfyText2ImgBaseNegative
        thisNegative = getNegativePrompt()

        # read the negative prompt stuff too
        negative = inputData.get("negative", {})
        negGeneralPrompt = negative.get("general", "") or thisNegative or ""
        negStylePrompt = negative.get("style", "") or ""
        self._negGeneralText.setPlainText(negGeneralPrompt)
        self._negStyleText.setPlainText(negStylePrompt)

        self._blockAll(False)

        self._saveButton.setEnabled(False)  # type: ignore
        self._revertButton.setEnabled(False)  # type: ignore

    def clear(self):
        """Clear the editor."""
        self._currentSidecar = None

        self._blockAll(True)

        for w in (
            self._promptText["description"],
            self._promptText["subject"],
            self._promptText["pose"],
            self._promptText["clothing"],
            self._promptText["lingerie"],
            self._promptText["setting"],
            self._promptText["composition"],
            self._negGeneralText,
            self._negStyleText,
            self._txtNotes,
        ):
            w.clear()  # type: ignore

        for field in self.FIELD_NAMES:
            self._rawText[field] = ""

        self._chkLocked.setChecked(False)
        self._chkReviewed.setChecked(False)

        self._saveButton.setEnabled(False)  # type: ignore
        self._revertButton.setEnabled(False)  # type: ignore

        self._blockAll(False)

    # ------------------------------------------------------------
    # Save / revert (kept minimal for now)
    # ------------------------------------------------------------

    def loadFromImage(self, imagePath: str) -> None:
        """
        Single entry point from MainWindow.
        Resolves the prompt sidecar path, loads it if present, else creates default,
        then populates UI via existing loadSidecar(SidecarData).
        """
        sidecarPath = self._findSidecarPath(imagePath)

        data = {}
        if sidecarPath and sidecarPath.exists():
            data = self._readJson(sidecarPath)

        sidecar = SidecarData.fromDict(imagePath, data)
        self.loadSidecar(sidecar)

    def hasUnsavedChanges(self) -> bool:
        return self._revertButton.isEnabled()  # type: ignore

    def saveCurrentSidecar(self) -> bool:
        """Save the currently loaded sidecar. Returns True if saved."""
        success = True
        if self._currentSidecar:
            try:
                # persist baseline + per-field prompts in metadata so it survives reload
                payload = self._currentSidecar.toDict() or {}
                payload["generator"] = {
                    "image source": getattr(self._currentSidecar, "imagePath", ""),
                    "tool": "Sidecar Editor",
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                }
                payload["positive"] = {
                    "description": self._promptText["description"].toPlainText().strip(),  # type: ignore
                    "subject": {"raw": self._rawText["subject"], "prompt": self._promptText["subject"].toPlainText().strip()},  # type: ignore
                    "pose": {"raw": self._rawText["pose"], "prompt": self._promptText["pose"].toPlainText().strip()},  # type: ignore
                    "clothing": {"raw": self._rawText["clothing"], "prompt": self._promptText["clothing"].toPlainText().strip()},  # type: ignore
                    "lingerie": {"raw": self._rawText["lingerie"], "prompt": self._promptText["lingerie"].toPlainText().strip()},  # type: ignore
                    "setting": {"raw": self._rawText["setting"], "prompt": self._promptText["setting"].toPlainText().strip()},  # type: ignore
                    "composition": {"raw": self._rawText["composition"], "prompt": self._promptText["composition"].toPlainText().strip()},  # type: ignore
                }
                payload["negative"] = {
                    "general": self._negGeneralText.toPlainText().strip(),  # type: ignore
                    "style": self._negStyleText.toPlainText().strip(),  # type: ignore
                }
                payload["assembled"] = {
                    "positive": self._assemblePositivePrompt(),
                    "negative": self._assembleNegativePrompt(),
                }
                payload["status"] = {
                    "locked": bool(self._chkLocked.isChecked()),
                    "reviewed": bool(self._chkReviewed.isChecked()),
                    "notes": self._txtNotes.toPlainText().strip(),
                }
                self._currentSidecar.data = payload

                # save to disk
                self._saveSidecar(self._currentSidecar, createBackup=True)

                self._revertButton.setEnabled(False)  # type: ignore
                self._saveButton.setEnabled(False)  # type: ignore
                self.sidecarSaved.emit(getattr(self._currentSidecar, "imagePath", ""))

            except Exception as e:
                QMessageBox.critical(
                    self, "Save Error", f"Failed to save sidecar:\n{e}"
                )
                success = False
        return success

    # ------------------------------------------------------------
    # Events
    # ------------------------------------------------------------

    def _onContentChanged(self):
        if self._currentSidecar:
            self._saveButton.setEnabled(True)  # type: ignore
            self._revertButton.setEnabled(True)  # type: ignore

    def _onGenerate(self):
        QMessageBox.information(self, "Generate", "Generate is not wired yet.")

    def _onSave(self):
        self.saveCurrentSidecar()

    def _onSendToLingerie(self):
        if self._currentSidecar:
            # copy current positive prompt to lingerie prompt
            self._promptText["lingerie"].setPlainText(self._promptText["clothing"].toPlainText())  # type: ignore
            self._promptText["clothing"].clear()  # type: ignore

            self._rawText["lingerie"] = self._rawText["clothing"]  # type: ignore
            self._rawText["clothing"] = ""  # type: ignore
            self._onContentChanged()  # mark as changed so user can save if they want

    def _onRevert(self):
        if self._currentSidecar:
            self._blockAll(True)
            self._promptText["subject"].setPlainText(self._rawText["subject"] or "")  # type: ignore
            self._promptText["pose"].setPlainText(self._rawText["pose"] or "")  # type: ignore
            self._promptText["clothing"].setPlainText(self._rawText["clothing"] or "")  # type: ignore
            self._promptText["lingerie"].setPlainText(self._rawText["lingerie"] or "")  # type: ignore
            self._promptText["setting"].setPlainText(self._rawText["setting"] or "")  # type: ignore
            self._promptText["composition"].setPlainText(self._rawText["composition"] or "")  # type: ignore
            self._revertButton.setEnabled(False)  # type: ignore
            self._saveButton.setEnabled(True)  # type: ignore - user can still save after revert if they want
            self._blockAll(False)

    def _onUpdateRaw(self):
        """
        Commit current prompt fields as the new baseline (raw).
        This does NOT save to disk by itself — it just updates the baseline
        so you can continue editing and use Revert meaningfully.
        """
        if self._currentSidecar:

            reply = QMessageBox.question(
                self,
                "Update Raw",
                "Set the current prompt fields as the new baseline?",
                QMessageBox.Yes | QMessageBox.No,  # type: ignore
                QMessageBox.No,  # type: ignore
            )
            if reply == QMessageBox.Yes:  # type: ignore
                for field in self.FIELD_NAMES:
                    self._rawText[field] = self._promptText[field].toPlainText().strip()  # type: ignore

                # baseline updated, so there are no longer "unsaved changes" relative to baseline
                self._revertButton.setEnabled(False)  # type: ignore
                self._saveButton.setEnabled(True)  # type: ignore - user can still save after updating raw if they want

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------

    def _assembleNegativePrompt(self) -> str:
        # Simple comma-join of negative prompt and style (you can tune ordering later)
        parts = [
            self._negGeneralText.toPlainText().strip(),
            self._negStyleText.toPlainText().strip(),
        ]
        parts = [p for p in parts if p]
        return ", ".join(parts)

    def _assemblePositivePrompt(self) -> str:
        # Simple comma-join of non-empty fields (you can tune ordering later)
        assembledPrompt = ""
        for field in self.FIELD_NAMES:
            assembledPrompt = ", ".join([self._promptText.get(field).toPlainText().strip(),]).strip()  # type: ignore
        return assembledPrompt

    def _backupFile(self, path: Path) -> None:
        if path.exists():
            bak = Path(str(path) + ".bak")
            bak.write_bytes(path.read_bytes())

    def _blockAll(self, blocked: bool):
        for w in (
            self._promptText.get("description"),
            self._promptText.get("subject"),
            self._promptText.get("pose"),
            self._promptText.get("clothing"),
            self._promptText.get("lingerie"),
            self._promptText.get("setting"),
            self._promptText.get("composition"),
            self._negGeneralText,
            self._negStyleText,
            self._txtNotes,
        ):
            w.blockSignals(blocked)  # type: ignore

        self._chkLocked.blockSignals(blocked)  # type: ignore
        self._chkReviewed.blockSignals(blocked)  # type: ignore

    def _findSidecarPath(self, imagePath: str) -> Optional[Path]:
        """
        Try a few common patterns:
        - alongside image: <stem>.prompt.json (we want this one to be the default if it exists, since it's the most explicit and specific to the image)
        - alongside image: <filename>.prompt.json (e.g. clothed-142.prompt.json)
        """
        if not imagePath:
            return None

        p = Path(imagePath)
        candidates = [
            p.with_suffix(".prompt.json"),
            Path(str(p) + ".prompt.json"),
        ]
        filename = p.with_suffix(".prompt.json")  # fallback to standard alongside path
        for c in candidates:
            if c.exists() and c.is_file():
                filename = c
                break

        return filename

    def _readJson(self, path: Path) -> Dict[str, Any]:
        try:
            txt = path.read_text(encoding="utf-8")
            obj = json.loads(txt)
            return obj if isinstance(obj, dict) else {}
        except Exception:
            return {}

    def _saveSidecar(self, sidecar: SidecarData, createBackup: bool = True):
        """
        Save sidecar data to disk.

        Args:
            sidecar: SidecarData to save
            createBackup: If True, create .bak backup before saving
        """
        sidecarPath = self._findSidecarPath(sidecar.imagePath)

        # Create backup if file exists
        if createBackup and sidecarPath.exists():  # type: ignore
            backupPath = Path(str(sidecarPath) + ".bak")
            try:
                backupPath.write_bytes(sidecarPath.read_bytes())  # type: ignore
            except IOError as e:
                print(f"Warning: Could not create backup {backupPath}: {e}")

        # Save the sidecar
        try:
            with open(sidecarPath, "w", encoding="utf-8") as f:  # type: ignore
                json.dump(sidecar.toDict(), f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error: Could not save sidecar {sidecarPath}: {e}")
            raise
