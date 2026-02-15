"""
Main window for Sidecar Editor.
QMainWindow with split panes for image browsing and editing.
Loads UI from Qt Designer .ui file.
"""

import os
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QSplitter,
    QFileDialog,
    QMessageBox,
    QLineEdit,
    QPushButton,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer, QFile
from PySide6.QtGui import QAction
from PySide6.QtUiTools import QUiLoader

import src.sidecarConfig as sidecarConfig
from src.sidecarCore import scanImages, loadSidecar
from src.outputResolver import OutputResolver

from Qt.widgets.thumbnailList import ThumbnailList
from Qt.widgets.imagePreview import ImagePreview
from Qt.widgets.editorPanel import EditorPanel
from Qt.widgets.outputPreview import OutputPreview
from Qt.widgets.buttonBar import ButtonBar


class MainWindow(QMainWindow):
    """Main window for the Sidecar Editor application."""

    def __init__(self):
        super().__init__()

        # Initialize components
        self._outputResolver = OutputResolver()
        self._currentImages = []
        self._inputRoot: Optional[str] = None
        self._outputRoot: Optional[str] = None

        self._setupUi()
        self._connectSignals()
        self._restoreState()

        # Show welcome message after window is shown
        QTimer.singleShot(10, self._showWelcome)

    def _setupUi(self):
        """Set up the user interface by loading from .ui file."""
        uiFilePath = Path(__file__).parent / "mainwindow.ui"

        loader = QUiLoader()
        uiFile = QFile(str(uiFilePath))
        if not uiFile.open(QFile.ReadOnly):  # type: ignore
            raise RuntimeError(f"Failed to open UI file: {uiFilePath}")

        # Load the UI - this creates a QMainWindow with all its properties
        # Keep a reference to prevent garbage collection of actions
        self._loadedWindow = loader.load(uiFile, None)
        uiFile.close()

        # Copy window properties from loaded window
        self.setWindowTitle(self._loadedWindow.windowTitle())  # type: ignore
        self.setGeometry(self._loadedWindow.geometry())  # type: ignore

        loadedCentral = self._loadedWindow.centralWidget()  # type: ignore
        if not loadedCentral:
            raise RuntimeError("Loaded UI has no central widget")
        loadedCentral.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore

        # Extract UI elements from the loaded central widget
        self._inputLabel = loadedCentral.findChild(QLineEdit, "txtInputFolder")  # type: ignore
        self._outputLabel = loadedCentral.findChild(QLineEdit, "txtOutputFolder")  # type: ignore
        btnSetInput = loadedCentral.findChild(QPushButton, "btnSetInput")  # type: ignore
        btnSetOutput = loadedCentral.findChild(QPushButton, "btnSetOutput")  # type: ignore

        # Placeholder widget where we inject our regions
        mainContentWidget = loadedCentral.findChild(QWidget, "wgtMainContent")  # type: ignore
        mainContentWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore

        missing = [
            name
            for name, w in {
                "txtInputFolder": self._inputLabel,
                "txtOutputFolder": self._outputLabel,
                "btnSetInput": btnSetInput,
                "btnSetOutput": btnSetOutput,
                "wgtMainContent": mainContentWidget,
            }.items()
            if w is None
        ]
        if missing:
            raise RuntimeError(
                f"Failed to find required widgets in UI file: {', '.join(missing)}"
            )

        # Store button references for signal connections
        self._btnSetInput = btnSetInput
        self._btnSetOutput = btnSetOutput

        # ------------------------------------------------------------
        # MAIN CONTENT LAYOUT (inside wgtMainContent)
        # ------------------------------------------------------------
        contentLayout = QVBoxLayout(mainContentWidget)
        contentLayout.setContentsMargins(0, 0, 0, 0)

        # ------------------------------------------------------------
        # SIDECAR REGIONS
        # Left: thumbnails
        # Right: preview/editor/output preview
        # ------------------------------------------------------------
        self._sidecarRegion = QSplitter(Qt.Horizontal)  # type: ignore
        self._sidecarRegion.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore

        self._buttonBar = ButtonBar(mainContentWidget)
        self._buttonBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # type: ignore

        # Left region: thumbnails
        self._thumbnailList = ThumbnailList()
        self._thumbnailList.setMinimumWidth(380)
        self._thumbnailList.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore
        self._sidecarRegion.addWidget(self._thumbnailList)

        # Editor region: three columns (preview | editor | output preview)
        self._editorRegion = QSplitter(Qt.Horizontal)  # type: ignore
        self._editorRegion.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore

        # Preview (input)
        self._imagePreview = ImagePreview()
        self._imagePreview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore
        self._editorRegion.addWidget(self._imagePreview)

        # Editor
        self._editorPanel = EditorPanel()
        self._editorPanel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore
        self._editorRegion.addWidget(self._editorPanel)

        # Output preview (same file resolved in output tree)
        self._outputPreview = OutputPreview()
        self._outputPreview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore
        self._editorRegion.addWidget(self._outputPreview)

        # Stretch behaviour (editor gets more horizontal space)
        self._editorRegion.setStretchFactor(0, 1)  # input preview
        self._editorRegion.setStretchFactor(1, 2)  # editor
        self._editorRegion.setStretchFactor(2, 1)  # output preview

        self._sidecarRegion.addWidget(self._editorRegion)

        # Default region sizing (applied again after geometry restore)
        self._sidecarRegion.setSizes([400, 1000])
        self._editorRegion.setSizes([350, 300, 350])

        contentLayout.addWidget(self._sidecarRegion, 1)
        contentLayout.addWidget(self._buttonBar, 0)

        # Set the loaded central widget as our central widget
        self.setCentralWidget(loadedCentral)
        self.setMenuBar(self._loadedWindow.menuBar())  # type: ignore
        self.setStatusBar(self._loadedWindow.statusBar())  # type: ignore

        # Menu actions from loaded window
        self._actionSetInput = self._loadedWindow.findChild(QAction, "actionSetInput")  # type: ignore
        self._actionSetOutput = self._loadedWindow.findChild(QAction, "actionSetOutput")  # type: ignore
        self._actionRefresh = self._loadedWindow.findChild(QAction, "actionRefresh")  # type: ignore
        self._actionAbout = self._loadedWindow.findChild(QAction, "actionAbout")  # type: ignore
        self._actionExit = self._loadedWindow.findChild(QAction, "actionExit")  # type: ignore

        # button bar
        self._buttonBar.cancelRequested.connect(self.close)
        self._buttonBar.okRequested.connect(self._onOk)

        self.statusBar().showMessage("Ready")

    def _connectSignals(self):
        """Connect UI signals to slots."""
        # Buttons
        self._btnSetInput.clicked.connect(self._onSetInputFolder)  # type: ignore
        self._btnSetOutput.clicked.connect(self._onSetOutputFolder)  # type: ignore

        # Menu actions
        self._actionSetInput.triggered.connect(self._onSetInputFolder)  # type: ignore
        self._actionSetOutput.triggered.connect(self._onSetOutputFolder)  # type: ignore
        self._actionRefresh.triggered.connect(self._onRefresh)  # type: ignore
        self._actionAbout.triggered.connect(self._onAbout)  # type: ignore

        # Menu exit
        self._actionExit.triggered.connect(self.close)  # type: ignore

        # Button Bar Actions
        self._buttonBar.cancelRequested.connect(self.close)
        self._buttonBar.okRequested.connect(self._onOk)

        # Widget signals
        self._thumbnailList.imageSelected.connect(self._onImageSelected)
        self._thumbnailList.thumbnailsLoaded.connect(self._onThumbnailsLoaded)
        self._editorPanel.sidecarSaved.connect(self._onSidecarSaved)

    def _onOk(self):
        if self._editorPanel.hasUnsavedChanges():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before exiting?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,  # type: ignore
                QMessageBox.Yes,  # type: ignore
            )
            if reply == QMessageBox.Cancel:  # type: ignore
                return
            elif reply == QMessageBox.Yes:  # type: ignore
                self._editorPanel.saveCurrentSidecar()
        self.close()

    def _restoreState(self):
        """Restore window state and paths from config."""
        geometry = sidecarConfig.getWindowGeometry()
        if geometry:
            self.setGeometry(
                geometry["x"], geometry["y"], geometry["width"], geometry["height"]
            )

        inputRoot = sidecarConfig.getInputRoot()
        if inputRoot:
            self._setInputRoot(inputRoot)
            QTimer.singleShot(100, self._scanImages)

        outputRoot = sidecarConfig.getOutputRoot()
        if outputRoot:
            self._setOutputRoot(outputRoot)

        # Apply default region sizing AFTER geometry restore (prevents "ignored" sizing)
        QTimer.singleShot(0, self._applyRegionDefaults)

    def _applyRegionDefaults(self):
        """Apply default region sizing after layouts have settled."""
        if hasattr(self, "_sidecarRegion"):
            self._sidecarRegion.setSizes([400, 1000])

        if hasattr(self, "_editorRegion"):
            self._editorRegion.setSizes([350, 300, 350])

    def _saveState(self):
        """Save window state and paths to config."""
        geometry = self.geometry()
        sidecarConfig.setWindowGeometry(
            geometry.x(), geometry.y(), geometry.width(), geometry.height()
        )

    def _showWelcome(self):
        """Show welcome message on first run or when no folders are set."""
        if not self._inputRoot:
            self.statusBar().showMessage(
                "Welcome! Please set an input folder to get started (File > Set Input Folder)"
            )
        else:
            self.statusBar().showMessage("Loading thumbnails...")

    def _onSetInputFolder(self):
        """Handle set input folder action."""
        initialDir = self._inputRoot or ""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Input Folder", initialDir
        )
        if folder:
            self._setInputRoot(folder)
            self._scanImages()

    def _onSetOutputFolder(self):
        """Handle set output folder action."""
        initialDir = self._outputRoot or ""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Folder", initialDir
        )
        if folder:
            self._setOutputRoot(folder)

    def _setInputRoot(self, path: str):
        """Set the input root folder."""
        self._inputRoot = path
        self._inputLabel.setText(path)  # type: ignore
        self._inputLabel.setStyleSheet("")  # type: ignore
        sidecarConfig.setInputRoot(path)

    def _setOutputRoot(self, path: str):
        """Set the output root folder."""
        self._outputRoot = path
        self._outputLabel.setText(path)  # type: ignore
        self._outputLabel.setStyleSheet("")  # type: ignore
        self._outputResolver.setOutputRoot(path)
        sidecarConfig.setOutputRoot(path)

    def _scanImages(self):
        """Scan the input folder for images."""
        if not self._inputRoot:
            return

        self.statusBar().showMessage("Scanning for images...")

        try:
            images = scanImages(self._inputRoot)
            self._currentImages = images

            if images:
                self.statusBar().showMessage(
                    f"Loading thumbnails for {len(images)} images..."
                )

            self._thumbnailList.loadImages(images, self._inputRoot)

            lastImage = sidecarConfig.getLastSelectedImage()
            if lastImage and lastImage in images:
                self._thumbnailList.selectImage(lastImage)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to scan images:\n{str(e)}")
            self.statusBar().showMessage("Error scanning images")

    def _onThumbnailsLoaded(self, imageCount: int):
        """Handle thumbnails loaded event."""
        self.statusBar().showMessage(f"Loaded {imageCount} images")

    def _onRefresh(self):
        """Handle refresh action."""
        self._scanImages()

    def _onImageSelected(self, imagePath: str):
        """Handle image selection."""
        sidecarConfig.setLastSelectedImage(imagePath)

        # Load sidecar into editor
        try:
            sidecar = loadSidecar(imagePath)
            self._editorPanel.loadSidecar(sidecar)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load sidecar:\n{str(e)}")

        # Resolve output image path (same relative file under output root)
        outputPath = None
        if self._outputRoot and self._inputRoot:
            outputPath = self._outputResolver.resolveOutput(imagePath, self._inputRoot)

        # Update previews:
        # - left preview: input only
        # - right preview: output only (if not found, show input again as a fallback)
        self._imagePreview.setImages(imagePath, None)

        if outputPath:
            self._outputPreview.setImages(outputPath, None)
        else:
            self._outputPreview.setImages(imagePath, None)

        # Status
        status = f"Loaded: {os.path.basename(imagePath)}"
        if outputPath:
            status += f" (output: {os.path.basename(outputPath)})"
        else:
            status += " (no output image found)"
        self.statusBar().showMessage(status)

    def _onSidecarSaved(self, imagePath: str):
        """Handle sidecar saved event."""
        self.statusBar().showMessage(f"Saved sidecar for {os.path.basename(imagePath)}")

    def _onAbout(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Sidecar Editor",
            "<h3>Sidecar Editor</h3>"
            "<p>A Qt-based desktop tool for reviewing and refining "
            "image prompt sidecar files.</p>"
            "<p>Version 0.1.0 (MVP)</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Browse images in a folder</li>"
            "<li>Edit .prompt.json sidecar files</li>"
            "<li>Preview original and generated images</li>"
            "<li>Persist UI state and paths</li>"
            "</ul>",
        )

    def closeEvent(self, event):
        """Handle window close event."""
        if self._editorPanel.hasUnsavedChanges():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to exit anyway?",
                QMessageBox.Yes | QMessageBox.No,  # type: ignore
                QMessageBox.No,  # type: ignore
            )
            if reply == QMessageBox.No:  # type: ignore
                event.ignore()
                return

        self._saveState()
        event.accept()
