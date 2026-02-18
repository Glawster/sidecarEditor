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
    QHBoxLayout,
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
from src.sidecarCore import scanImages
from src.outputResolver import OutputResolver

from Qt.widgets.thumbnailList import ThumbnailList
from Qt.widgets.imagePreview import ImagePreview
from Qt.widgets.editorPanel import EditorPanel
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
        """Set up the user interface by loading from .ui file, then inject dynamic panels."""
        uiFilePath = Path(__file__).parent / "mainwindow.ui"

        loader = QUiLoader()
        uiFile = QFile(str(uiFilePath))
        if not uiFile.open(QFile.ReadOnly):  # type: ignore
            raise RuntimeError(f"Failed to open UI file: {uiFilePath}")

        self._loadedWindow = loader.load(uiFile, None)
        uiFile.close()

        if self._loadedWindow is None:
            raise RuntimeError(f"Failed to load UI file: {uiFilePath}")

        loadedCentral = self._loadedWindow.centralWidget()  # type: ignore
        if loadedCentral is None:
            raise RuntimeError("Loaded UI has no central widget")

        # window basics
        self.setWindowTitle(self._loadedWindow.windowTitle())
        self.setGeometry(self._loadedWindow.geometry())

        # reuse UI menubar/statusbar (prevents double menubar)
        loadedMenuBar = self._loadedWindow.menuBar()  # type: ignore
        if loadedMenuBar is not None:
            loadedMenuBar.setParent(self)
            self.setMenuBar(loadedMenuBar)

        loadedStatusBar = self._loadedWindow.statusBar()  # type: ignore
        if loadedStatusBar is not None:
            loadedStatusBar.setParent(self)
            self.setStatusBar(loadedStatusBar)

        self.setCentralWidget(loadedCentral)

        # placeholders from UI
        self._topBarWidget = loadedCentral.findChild(QWidget, "wgtTopBar")
        self._mainContentWidget = loadedCentral.findChild(QWidget, "wgtMainContent")
        if self._topBarWidget is None:
            raise RuntimeError("Missing widget in mainwindow.ui: wgtTopBar")
        if self._mainContentWidget is None:
            raise RuntimeError("Missing widget in mainwindow.ui: wgtMainContent")

        centralLayout = loadedCentral.layout()
        if centralLayout is None:
            centralLayout = QVBoxLayout(loadedCentral)
            centralLayout.setContentsMargins(0, 0, 0, 0)
            centralLayout.setSpacing(6)
            centralLayout.addWidget(self._topBarWidget)
            centralLayout.addWidget(self._mainContentWidget)

        centralLayout.setStretch(0, 0)  # top bar
        centralLayout.setStretch(1, 1)  # main content fills

        # top bar controls
        self._btnSetInput = loadedCentral.findChild(QPushButton, "btnSetInput")
        self._btnSetOutput = loadedCentral.findChild(QPushButton, "btnSetOutput")
        if self._btnSetInput is None:
            raise RuntimeError("Missing widget in mainwindow.ui: btnSetInput")
        if self._btnSetOutput is None:
            raise RuntimeError("Missing widget in mainwindow.ui: btnSetOutput")

        self._txtInputFolder = loadedCentral.findChild(QLineEdit, "txtInputFolder")
        self._txtOutputFolder = loadedCentral.findChild(QLineEdit, "txtOutputFolder")
        if self._txtInputFolder is None:
            raise RuntimeError("Missing widget in mainwindow.ui: txtInputFolder")
        if self._txtOutputFolder is None:
            raise RuntimeError("Missing widget in mainwindow.ui: txtOutputFolder")

        # actions
        self._actionSetInput = self._loadedWindow.findChild(QAction, "actionSetInput")
        self._actionSetOutput = self._loadedWindow.findChild(QAction, "actionSetOutput")
        self._actionRefresh = self._loadedWindow.findChild(QAction, "actionRefresh")
        self._actionExit = self._loadedWindow.findChild(QAction, "actionExit")
        self._actionAbout = self._loadedWindow.findChild(QAction, "actionAbout")

        # main layout inside wgtMainContent
        mainLayout = self._mainContentWidget.layout()
        if mainLayout is None:
            mainLayout = QVBoxLayout(self._mainContentWidget)

        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(6)

        # --- splitters ---
        # mainContentWidget is split horizontally the bottom half becomes the sidecar frame
        self._sidecarFrame = QSplitter(Qt.Horizontal, self._mainContentWidget) # type: ignore
        self._sidecarFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # type: ignore

        # create the thumbnail widget and add to sidecar frame
        self._thumbnailList = ThumbnailList()
        self._thumbnailList.setMinimumWidth(380)
        self._thumbnailList.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # type: ignore
        self._sidecarFrame.addWidget(self._thumbnailList)

        # split the sidecar frame: right side becomes the editor region
        # layout: [EditorPanel | (InputPreview above OutputPreview)]
        self._editorFrame = QSplitter(Qt.Horizontal, self._sidecarFrame)  # type: ignore
        self._editorFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore

        # left: editor panel (now long, so give it the main width)
        self._editorPanel = EditorPanel()
        self._editorPanel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore
        self._editorFrame.addWidget(self._editorPanel)

        # right: previews stacked vertically
        self._previewFrame = QSplitter(Qt.Vertical, self._editorFrame)  # type: ignore
        self._previewFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore

        self._inputPreview = ImagePreview()
        self._inputPreview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore
        self._previewFrame.addWidget(self._inputPreview)

        self._outputPreview = ImagePreview()
        self._outputPreview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore
        self._previewFrame.addWidget(self._outputPreview)

        # add the preview frame to the horizontal editor frame
        self._editorFrame.addWidget(self._previewFrame)

        # stretch: editor panel wider than preview column
        self._editorFrame.setStretchFactor(0, 3)
        self._editorFrame.setStretchFactor(1, 1)

        # stretch: preview stack roughly equal heights
        self._previewFrame.setStretchFactor(0, 1)
        self._previewFrame.setStretchFactor(1, 1)

        # add the editor frame to the sidecar frame (right side)
        self._sidecarFrame.addWidget(self._editorFrame)
        #self._sidecarFrame.setSizes([400, 1000])
        #self._editorFrame.setSizes([350, 600, 350])

        # add the sidecar frame to the main content layout
        mainLayout.addWidget(self._sidecarFrame, 1)

        # --- bottom-right button bar ---
        self._buttonBar = ButtonBar(self._mainContentWidget)
        self._buttonBar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed) # type: ignore
        self._buttonBar.setMinimumHeight(44)
        self._buttonBar.setMinimumWidth(160)   # helps it not collapse horizontally

        bottomRow = QHBoxLayout()
        bottomRow.setContentsMargins(0, 0, 0, 0)
        bottomRow.setSpacing(6)
        bottomRow.addStretch(1)
        bottomRow.addWidget(self._buttonBar)

        mainLayout.addLayout(bottomRow, 0)

        if self.statusBar():
            self.statusBar().showMessage("Ready")


    def _connectSignals(self):
        """Connect UI signals to slots."""
        # Buttons
        self._btnSetInput.clicked.connect(self._onSetInputFolder)  
        self._btnSetOutput.clicked.connect(self._onSetOutputFolder) 

        # Menu actions
        if self._actionSetInput:
            self._actionSetInput.triggered.connect(self._onSetInputFolder)
        if self._actionSetOutput:
            self._actionSetOutput.triggered.connect(self._onSetOutputFolder)
        if self._actionRefresh:
            self._actionRefresh.triggered.connect(self._onRefresh)
        if self._actionAbout:
            self._actionAbout.triggered.connect(self._onAbout)

        # Menu exit
        if self._actionExit:
            self._actionExit.triggered.connect(self.close)  

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
            self._sidecarRegion.setSizes([400, 1000]) # type: ignore

        if hasattr(self, "_editorRegion"):
               self._sidecarRegion.setSizes([400, 1000]) # type: ignore

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
        self._txtInputFolder.setText(path)  # type: ignore
        self._txtInputFolder.setStyleSheet("")  # type: ignore
        sidecarConfig.setInputRoot(path)

    def _setOutputRoot(self, path: str):
        """Set the output root folder."""
        self._outputRoot = path
        self._txtOutputFolder.setText(path)  # type: ignore
        self._txtOutputFolder.setStyleSheet("")  # type: ignore
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
            self._editorPanel.loadFromImage(imagePath)  # type: ignore
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load sidecar:\n{str(e)}")

        # Update previews:
        # - left preview: input only
        # - right preview: output only (if not found, show input again as a fallback)
        self._inputPreview.setImage(imagePath) # type: ignore

        # Resolve output image path (same relative file under output root)
        outputPath = self._outputResolver.resolveOutput(imagePath, self._inputRoot)
        if outputPath:
            self._outputPreview.setImage(outputPath) # type: ignore
        else:
            self._outputPreview.setImage(None)  # type: ignore

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
