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
from ...src.sidecarCore import scan_images, load_sidecar
from ...src.outputResolver import OutputResolver

from .thumbnailList import ThumbnailList
from .imagePreview import ImagePreview
from .editorPanel import EditorPanel


class MainWindow(QMainWindow):
    """Main window for the Sidecar Editor application."""

    def __init__(self):

        super().__init__()

        # Initialize components
        self._output_resolver = OutputResolver()
        self._current_images = []
        self._input_root: Optional[str] = None
        self._output_root: Optional[str] = None

        self._setup_ui()
        self._connect_signals()
        self._restore_state()

        # Show welcome message after window is shown
        QTimer.singleShot(100, self._show_welcome)

    def _setup_ui(self):

        """Set up the user interface by loading from .ui file."""
        # Load UI from .ui file
        ui_file_path = Path(__file__).parent / "mainwindow.ui"

        # Create QUiLoader and load the .ui file
        loader = QUiLoader()
        ui_file = QFile(str(ui_file_path))
        if not ui_file.open(QFile.ReadOnly):
            raise RuntimeError(f"Failed to open UI file: {ui_file_path}")

        # Load the UI - this creates a QMainWindow with all its properties
        # Keep a reference to prevent garbage collection of actions
        self._loaded_window = loader.load(ui_file, None)
        ui_file.close()

        # Copy window properties from loaded window
        self.setWindowTitle(self._loaded_window.windowTitle())
        self.setGeometry(self._loaded_window.geometry())

        # Extract the central widget from the loaded window
        loaded_central = self._loaded_window.centralWidget()
        if not loaded_central:
            raise RuntimeError("Loaded UI has no central widget")

        # Extract UI elements from the loaded central widget
        self._input_label = loaded_central.findChild(QLabel, "lblInputPath")
        self._output_label = loaded_central.findChild(QLabel, "lblOutputPath")
        btnSetInput = loaded_central.findChild(QPushButton, "btnSetInput")
        btnSetOutput = loaded_central.findChild(QPushButton, "btnSetOutput")

        # Get the main content widget where we'll add the splitters
        main_content_widget = loaded_central.findChild(QWidget, "wgtMainContent")

        # Verify all required widgets were found
        if not all([self._input_label, self._output_label, btnSetInput, btnSetOutput, main_content_widget]):
            raise RuntimeError("Failed to find all required widgets in UI file")

        # Store button references for signal connections
        self._btnSetInput = btnSetInput
        self._btnSetOutput = btnSetOutput

        # Create layout for main content widget
        content_layout = QVBoxLayout(main_content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Create main splitter (horizontal)
        main_splitter = QSplitter(Qt.Horizontal)

        # Left panel: Thumbnail list
        self._thumbnail_list = ThumbnailList()
        # Set minimum width to accommodate 3 thumbnails (100px each + 10px spacing + margins)
        # 3 * 100px (thumbnails) + 2 * 10px (spacing) + ~30px (margins/scrollbar) = ~350px
        self._thumbnail_list.setMinimumWidth(350)
        main_splitter.addWidget(self._thumbnail_list)

        # Right panel: Splitter with preview and editor
        right_splitter = QSplitter(Qt.Vertical)

        # Image preview
        self._image_preview = ImagePreview()
        right_splitter.addWidget(self._image_preview)

        # Editor panel
        self._editor_panel = EditorPanel()
        right_splitter.addWidget(self._editor_panel)

        # Set initial sizes for right splitter
        right_splitter.setSizes([400, 300])

        main_splitter.addWidget(right_splitter)

        # Set initial sizes for main splitter
        # Left panel (thumbnails): 350px to fit 3 thumbnails wide
        # Right panel (preview/editor): remaining space
        main_splitter.setSizes([350, 850])

        content_layout.addWidget(main_splitter)

        # Set the loaded central widget as our central widget
        self.setCentralWidget(loaded_central)

        # Get menu actions from the loaded window and add them to our menu bar
        self._action_set_input = self._loaded_window.findChild(QAction, "actionSetInputFolder")
        self._action_set_output = self._loaded_window.findChild(QAction, "actionSetOutputFolder")
        self._action_refresh = self._loaded_window.findChild(QAction, "actionRefresh")
        self._action_exit = self._loaded_window.findChild(QAction, "actionExit")
        self._action_about = self._loaded_window.findChild(QAction, "actionAbout")

        # Recreate menu structure with the actions from the loaded window
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        if self._action_set_input:
            file_menu.addAction(self._action_set_input)
        if self._action_set_output:
            file_menu.addAction(self._action_set_output)
        file_menu.addSeparator()
        if self._action_refresh:
            file_menu.addAction(self._action_refresh)
        file_menu.addSeparator()
        if self._action_exit:
            file_menu.addAction(self._action_exit)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        if self._action_about:
            help_menu.addAction(self._action_about)

        # Status bar
        self.statusBar().showMessage("Ready")

    def _connect_signals(self):

        """Connect UI signals to slots."""
        # Connect button signals
        self._btnSetInput.clicked.connect(self._on_set_input_folder)
        self._btnSetOutput.clicked.connect(self._on_set_output_folder)
        
        # Connect menu actions
        self._action_set_input.triggered.connect(self._on_set_input_folder)
        self._action_set_output.triggered.connect(self._on_set_output_folder)
        self._action_refresh.triggered.connect(self._on_refresh)
        self._action_exit.triggered.connect(self.close)
        self._action_about.triggered.connect(self._on_about)
        
        # Connect widget signals
        self._thumbnail_list.imageSelected.connect(self._on_image_selected)
        self._thumbnail_list.thumbnailsLoaded.connect(self._on_thumbnails_loaded)
        self._editor_panel.sidecarSaved.connect(self._on_sidecar_saved)

    def _restore_state(self):

        """Restore window state and paths from config."""
        # Restore window geometry
        geometry = sidecarConfig.get_window_geometry()
        if geometry:
            self.setGeometry(
                geometry["x"], geometry["y"], geometry["width"], geometry["height"]
            )

        # Restore input/output paths
        input_root = sidecarConfig.get_input_root()
        if input_root:
            self._set_input_root(input_root)
            # Defer scanning images until after window is shown
            # This prevents the app from appearing frozen on startup
            QTimer.singleShot(100, self._scan_images)

        output_root = sidecarConfig.get_output_root()
        if output_root:
            self._set_output_root(output_root)

    def _save_state(self):
        """Save window state and paths to config."""
        # Save window geometry
        geometry = self.geometry()
        sidecarConfig.set_window_geometry(
            geometry.x(), geometry.y(), geometry.width(), geometry.height()
        )

    def _show_welcome(self):
        """Show welcome message on first run or when no folders are set."""
        if not self._input_root:
            self.statusBar().showMessage(
                "Welcome! Please set an input folder to get started (File > Set Input Folder)"
            )
        else:
            # If we have an input root, show loading message since thumbnails will be loading
            self.statusBar().showMessage("Loading thumbnails...")

    def _on_set_input_folder(self):
        """Handle set input folder action."""
        initial_dir = self._input_root or ""

        folder = QFileDialog.getExistingDirectory(
            self, "Select Input Folder", initial_dir
        )

        if folder:
            self._set_input_root(folder)
            self._scan_images()

    def _on_set_output_folder(self):
        """Handle set output folder action."""
        initial_dir = self._output_root or ""

        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Folder", initial_dir
        )

        if folder:
            self._set_output_root(folder)

    def _set_input_root(self, path: str):

        """
        Set the input root folder.

        Args:
            path: Input folder path
        """
        self._input_root = path
        self._input_label.setText(path)
        self._input_label.setStyleSheet("")
        sidecarConfig.set_input_root(path)

    def _set_output_root(self, path: str):

        """
        Set the output root folder.

        Args:
            path: Output folder path
        """
        self._output_root = path
        self._output_label.setText(path)
        self._output_label.setStyleSheet("")
        self._output_resolver.set_output_root(path)
        sidecarConfig.set_output_root(path)

    def _scan_images(self):
        """Scan the input folder for images."""
        if not self._input_root:
            return

        self.statusBar().showMessage("Scanning for images...")

        try:
            images = scan_images(self._input_root)
            self._current_images = images
            
            # Show loading message for thumbnails BEFORE loading starts
            if images:
                self.statusBar().showMessage(f"Loading thumbnails for {len(images)} images...")
            
            # Load images - this will emit thumbnailsLoaded signal when done
            self._thumbnail_list.load_images(images, self._input_root)
            
            # Select last selected image if available
            last_image = sidecarConfig.get_last_selected_image()
            if last_image and last_image in images:
                self._thumbnail_list.select_image(last_image)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to scan images:\n{str(e)}")
            self.statusBar().showMessage("Error scanning images")
    
    def _on_thumbnails_loaded(self, image_count: int):
        """
        Handle thumbnails loaded event.
        
        Args:
            image_count: Number of thumbnails loaded
        """
        self.statusBar().showMessage(f"Loaded {image_count} images")
    
    def _on_refresh(self):
        """Handle refresh action."""
        self._scan_images()

    def _on_image_selected(self, image_path: str):

        """
        Handle image selection.

        Args:
            image_path: Path to the selected image
        """
        # Save selection
        sidecarConfig.set_last_selected_image(image_path)

        # Load sidecar
        try:
            sidecar = load_sidecar(image_path)
            self._editor_panel.load_sidecar(sidecar)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load sidecar:\n{str(e)}")

        # Resolve output image
        output_path = None
        if self._output_root and self._input_root:
            output_path = self._output_resolver.resolve_output(
                image_path, self._input_root
            )

        # Update preview
        self._image_preview.set_images(image_path, output_path)

        # Update status
        status = f"Loaded: {os.path.basename(image_path)}"
        if output_path:
            status += f" (output: {os.path.basename(output_path)})"
        else:
            status += " (no output image found)"
        self.statusBar().showMessage(status)

    def _on_sidecar_saved(self, image_path: str):
        """
        Handle sidecar saved event.

        Args:
            image_path: Path to the image whose sidecar was saved
        """
        self.statusBar().showMessage(
            f"Saved sidecar for {os.path.basename(image_path)}"
        )

    def _on_about(self):
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
        if self._editor_panel.has_unsaved_changes():
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
        self._save_state()
        event.accept()
