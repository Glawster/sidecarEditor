"""
Main window for Sidecar Editor.
QMainWindow with split panes for image browsing and editing.
Loads UI from Qt Designer .ui file.
"""

import os
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QSplitter,
    QFileDialog,
    QMessageBox,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt, QTimer, QFile
from PySide6.QtGui import QAction
from PySide6.QtUiTools import QUiLoader
from typing import Optional

from ...src import sidecarConfig
from ...src.sidecarCore import scanImages, loadSidecar
from ...src.outputResolver import OutputResolver

from .thumbnailList import ThumbnailList
from .imagePreview import ImagePreview
from .editorPanel import EditorPanel


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
        QTimer.singleShot(100, self._showWelcome)

    def _setupUi(self):
        """Set up the user interface by loading from .ui file."""
        # Load UI from .ui file
        uiFilePath = Path(__file__).parent / "mainwindow.ui"

        # Create QUiLoader and load the .ui file
        loader = QUiLoader()
        uiFile = QFile(str(uiFilePath))
        if not uiFile.open(QFile.readOnly):
            raise RuntimeError(f"Failed to open UI file: {uiFilePath}")

        # Load UI into this QMainWindow
        # Note: We need to load the content, not create a new window
        uiWidget = loader.load(uiFile, self)
        uiFile.close()

        # Copy window properties from loaded widget to this MainWindow
        self.setWindowTitle(uiWidget.windowTitle())

        # Extract UI elements from the loaded widget
        # Get references to widgets defined in the .ui file
        self._inputLabel = uiWidget.findChild(QLabel, "lblInputPath")
        self._outputLabel = uiWidget.findChild(QLabel, "lblOutputPath")
        btnSetInput = uiWidget.findChild(QPushButton, "btnSetInput")
        btnSetOutput = uiWidget.findChild(QPushButton, "btnSetOutput")

        # Get the main content widget where we'll add the splitters
        mainContentWidget = uiWidget.findChild(QWidget, "wgtMainContent")

        # Verify all required widgets were found
        if not all(
            [
                self._inputLabel,
                self._outputLabel,
                btnSetInput,
                btnSetOutput,
                mainContentWidget,
            ]
        ):
            raise RuntimeError("Failed to find all required widgets in UI file")

        # Store button references for signal connections
        self._btnSetInput = btnSetInput
        self._btnSetOutput = btnSetOutput

        # Create layout for main content widget
        contentLayout = QVBoxLayout(mainContentWidget)
        contentLayout.setContentsMargins(0, 0, 0, 0)

        # Create main splitter (horizontal)
        mainSplitter = QSplitter(Qt.Horizontal)

        # Left panel: Thumbnail list
        self._thumbnailList = ThumbnailList()
        # Set minimum width to accommodate 3 thumbnails (100px each + 10px spacing + margins)
        # 3 * 100px (thumbnails) + 2 * 10px (spacing) + ~30px (margins/scrollbar) = ~350px
        self._thumbnailList.setMinimumWidth(350)
        mainSplitter.addWidget(self._thumbnailList)

        # Right panel: Splitter with preview and editor
        rightSplitter = QSplitter(Qt.Vertical)

        # Image preview
        self._imagePreview = ImagePreview()
        rightSplitter.addWidget(self._imagePreview)

        # Editor panel
        self._editorPanel = EditorPanel()
        rightSplitter.addWidget(self._editorPanel)

        # Set initial sizes for right splitter
        rightSplitter.setSizes([400, 300])

        mainSplitter.addWidget(rightSplitter)

        # Set initial sizes for main splitter
        # Left panel (thumbnails): 350px to fit 3 thumbnails wide
        # Right panel (preview/editor): remaining space
        mainSplitter.setSizes([350, 850])

        contentLayout.addWidget(mainSplitter)

        # Set the loaded widget as central widget
        self.setCentralWidget(uiWidget)

        # Get menu actions from the UI file
        self._actionSetInput = uiWidget.findChild(QAction, "actionSetInputFolder")
        self._actionSetOutput = uiWidget.findChild(QAction, "actionSetOutputFolder")
        self._actionRefresh = uiWidget.findChild(QAction, "actionRefresh")
        self._actionExit = uiWidget.findChild(QAction, "actionExit")
        self._actionAbout = uiWidget.findChild(QAction, "actionAbout")

        # Recreate menu structure with the actions from the loaded window
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_actions = [
            self._action_set_input,
            self._action_set_output,
            None,  # Separator
            self._action_refresh,
            None,  # Separator
            self._action_exit
        ]
        for action in file_actions:
            if action is None:
                file_menu.addSeparator()
            elif action:
                file_menu.addAction(action)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        if self._action_about:
            help_menu.addAction(self._action_about)

        # Status bar
        self.statusBar().showMessage("Ready")

    def _connectSignals(self):
        """Connect UI signals to slots."""
        # Connect button signals
        self._btnSetInput.clicked.connect(self._onSetInputFolder)
        self._btnSetOutput.clicked.connect(self._onSetOutputFolder)

        # Connect menu actions
        self._actionSetInput.triggered.connect(self._onSetInputFolder)
        self._actionSetOutput.triggered.connect(self._onSetOutputFolder)
        self._actionRefresh.triggered.connect(self._onRefresh)
        self._actionExit.triggered.connect(self.close)
        self._actionAbout.triggered.connect(self._onAbout)

        # Connect widget signals
        self._thumbnailList.imageSelected.connect(self._onImageSelected)
        self._thumbnailList.thumbnailsLoaded.connect(self._onThumbnailsLoaded)
        self._editorPanel.sidecarSaved.connect(self._onSidecarSaved)

    def _restoreState(self):
        """Restore window state and paths from config."""
        # Restore window geometry
        geometry = sidecarConfig.getWindowGeometry()
        if geometry:
            self.setGeometry(
                geometry["x"], geometry["y"], geometry["width"], geometry["height"]
            )

        # Restore input/output paths
        inputRoot = sidecarConfig.getInputRoot()
        if inputRoot:
            self._setInputRoot(inputRoot)
            # Defer scanning images until after window is shown
            # This prevents the app from appearing frozen on startup
            QTimer.singleShot(100, self._scanImages)

        outputRoot = sidecarConfig.getOutputRoot()
        if outputRoot:
            self._setOutputRoot(outputRoot)

    def _saveState(self):
        """Save window state and paths to config."""
        # Save window geometry
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
            # If we have an input root, show loading message since thumbnails will be loading
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
        """
        Set the input root folder.

        Args:
            path: Input folder path
        """
        self._inputRoot = path
        self._inputLabel.setText(path)
        self._inputLabel.setStyleSheet("")
        sidecarConfig.setInputRoot(path)

    def _setOutputRoot(self, path: str):
        """
        Set the output root folder.

        Args:
            path: Output folder path
        """
        self._outputRoot = path
        self._outputLabel.setText(path)
        self._outputLabel.setStyleSheet("")
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

            # Show loading message for thumbnails BEFORE loading starts
            if images:
                self.statusBar().showMessage(
                    f"Loading thumbnails for {len(images)} images..."
                )

            # Load images - this will emit thumbnailsLoaded signal when done
            self._thumbnailList.loadImages(images, self._inputRoot)

            # Select last selected image if available
            lastImage = sidecarConfig.getLastSelectedImage()
            if lastImage and lastImage in images:
                self._thumbnailList.selectImage(lastImage)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to scan images:\n{str(e)}")
            self.statusBar().showMessage("Error scanning images")

    def _onThumbnailsLoaded(self, imageCount: int):
        """
        Handle thumbnails loaded event.

        Args:
            imageCount: Number of thumbnails loaded
        """
        self.statusBar().showMessage(f"Loaded {imageCount} images")

    def _onRefresh(self):
        """Handle refresh action."""
        self._scanImages()

    def _onImageSelected(self, imagePath: str):
        """
        Handle image selection.

        Args:
            imagePath: Path to the selected image
        """
        # Save selection
        sidecarConfig.setLastSelectedImage(imagePath)

        # Load sidecar
        try:
            sidecar = loadSidecar(imagePath)
            self._editorPanel.loadSidecar(sidecar)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load sidecar:\n{str(e)}")

        # Resolve output image
        outputPath = None
        if self._outputRoot and self._inputRoot:
            outputPath = self._outputResolver.resolveOutput(imagePath, self._inputRoot)

        # Update preview
        self._imagePreview.setImages(imagePath, outputPath)

        # Update status
        status = f"Loaded: {os.path.basename(imagePath)}"
        if outputPath:
            status += f" (output: {os.path.basename(outputPath)})"
        else:
            status += " (no output image found)"
        self.statusBar().showMessage(status)

    def _onSidecarSaved(self, imagePath: str):
        """
        Handle sidecar saved event.

        Args:
            imagePath: Path to the image whose sidecar was saved
        """
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
        # Check for unsaved changes
        if self._editorPanel.hasUnsavedChanges():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to exit anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.No:
                event.ignore()
                return

        # Save state
        self._saveState()
        event.accept()
