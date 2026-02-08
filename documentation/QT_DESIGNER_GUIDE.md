# Qt Designer Integration Guide

This guide explains how to use Qt Designer to create and modify UI files (.ui) for the Sidecar Editor application.

## Table of Contents

1. [Overview](#overview)
2. [Setting Up Qt Designer](#setting-up-qt-designer)
3. [Creating UI Files](#creating-ui-files)
4. [Loading UI Files in Python](#loading-ui-files-in-python)
5. [Widget Naming Conventions](#widget-naming-conventions)
6. [Best Practices](#best-practices)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)

## Overview

Qt Designer is a visual UI design tool that generates XML-based .ui files. These files can be:
- Loaded dynamically at runtime using `QUiLoader`
- Converted to Python code using `pyside6-uic` (compile-time approach)

This project uses the **dynamic loading approach** for flexibility and easier UI iteration.

### Why Use Qt Designer?

✅ **Visual Design**: Drag-and-drop interface design  
✅ **Rapid Prototyping**: Quick UI mockups and iteration  
✅ **Separation**: UI design separate from business logic  
✅ **Maintainability**: Easier for designers to modify UI  
✅ **Preview**: See exactly how your UI will look

## Setting Up Qt Designer

### Installation

Qt Designer comes with PySide6:

```bash
# Install PySide6 (already in requirements.txt)
pip install PySide6

# Qt Designer is included in the PySide6 installation
# Location varies by platform:
# - Linux: /usr/lib/qt6/bin/designer or similar
# - macOS: In PySide6 package installation
# - Windows: In Python site-packages/PySide6/designer.exe
```

### Finding Qt Designer

```bash
# Find Qt Designer executable
python -c "import PySide6; print(PySide6.__path__)"

# Or use the Qt Designer that may be installed separately
which designer  # Linux/macOS
where designer  # Windows
```

### Alternative: Use Qt Creator

Qt Creator includes Qt Designer and is available at: https://www.qt.io/download

## Creating UI Files

### Directory Structure

UI files should be stored alongside their corresponding Python modules:

```
sidecarEditor/
├── Qt/
│   ├── mainWindow.py          # Python code
│   ├── mainWindow.ui           # UI file for MainWindow (optional)
│   └── widgets/
│       ├── editorPanel.py      # Python code
│       ├── editorPanel.ui      # UI file for EditorPanel (optional)
│       ├── imagePreview.py
│       └── imagePreview.ui     # UI file for ImagePreview (optional)
```

### Creating a New UI File

1. **Open Qt Designer**
2. **Choose Template**: 
   - `Main Window` for QMainWindow
   - `Widget` for QWidget-based components
   - `Dialog` for QDialog windows
3. **Design Your UI**:
   - Drag widgets from the Widget Box
   - Set properties in the Property Editor
   - Create layouts (QVBoxLayout, QHBoxLayout, QGridLayout)
   - Name widgets with proper prefixes (see naming conventions)
4. **Save**: Save as `.ui` file in appropriate directory

### Key Qt Designer Features

- **Widget Box**: Available widgets (buttons, labels, etc.)
- **Property Editor**: Modify widget properties
- **Object Inspector**: View widget hierarchy
- **Form Editor**: Main design canvas
- **Layouts**: Right-click widgets to add layouts
- **Preview**: Form → Preview to test the UI

## Loading UI Files in Python

### Method 1: Dynamic Loading with QUiLoader (Current Approach)

This method loads .ui files at runtime:

```python
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from pathlib import Path

class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._load_ui()
    
    def _load_ui(self):
        """Load UI from .ui file."""
        # Get path to .ui file (same directory as this .py file)
        ui_file_path = Path(__file__).parent / "myWidget.ui"
        
        # Load the UI
        loader = QUiLoader()
        ui_file = QFile(str(ui_file_path))
        ui_file.open(QFile.ReadOnly)
        
        # Load into a container widget
        ui_widget = loader.load(ui_file, self)
        ui_file.close()
        
        # Set up layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(ui_widget)
        
        # Access widgets from loaded UI
        self.btnSave = ui_widget.findChild(QPushButton, "btnSave")
        self.lblStatus = ui_widget.findChild(QLabel, "lblStatus")
        
        # Connect signals
        self.btnSave.clicked.connect(self._on_save)
```

### Method 2: Compile to Python (Alternative)

Convert .ui file to Python code (useful for distribution):

```bash
# Convert .ui to .py file
pyside6-uic myWidget.ui -o ui_myWidget.py

# Use in your code
from .ui_myWidget import Ui_MyWidget

class MyWidget(QWidget, Ui_MyWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # Set up the UI from generated code
        
        # Widgets are now directly accessible as self.btnSave, etc.
        self.btnSave.clicked.connect(self._on_save)
```

**Note**: The current project uses Method 1 (dynamic loading) for flexibility.

## Widget Naming Conventions

**IMPORTANT**: Follow the GUI naming conventions for consistency:

### Required Prefixes

- `btn*` - Buttons (QPushButton, QToolButton)
- `lbl*` - Labels (QLabel)
- `ent*` - Entry fields (QLineEdit)
- `txt*` - Text areas (QTextEdit)
- `frm*` - Frames (QFrame, QWidget containers)
- `lst*` - List widgets (QListWidget)
- `cmb*` - Combo boxes (QComboBox)
- `chk*` - Check buttons (QCheckBox)
- `rad*` - Radio buttons (QRadioButton)
- `scr*` - Scrollbars (QScrollBar)
- `can*` - Canvas (QGraphicsView, custom paint widgets)

### Examples

✅ **Good Names**:
- `btnSave` - Save button
- `lblStatus` - Status label
- `entUsername` - Username entry field
- `txtDescription` - Description text area
- `frmMain` - Main container frame
- `lstThumbnails` - Thumbnail list

❌ **Bad Names**:
- `saveButton` - Wrong prefix order
- `button1` - Not descriptive
- `statusLabel` - Wrong prefix order
- `edit` - No prefix

### Naming in Qt Designer

1. Select a widget
2. Go to Property Editor
3. Find `objectName` property at the top
4. Set name with proper prefix: e.g., `btnSave`

## Best Practices

### 1. Design Principles

- **Keep It Simple**: Don't over-complicate layouts
- **Use Spacers**: Use horizontal/vertical spacers for proper alignment
- **Consistent Spacing**: Use consistent margins and padding
- **Responsive Design**: Use layouts instead of absolute positioning
- **Group Related Items**: Use QGroupBox for related controls

### 2. Layout Tips

- **Always Use Layouts**: Never use absolute positioning
- **Nested Layouts**: Combine QVBoxLayout, QHBoxLayout for complex UIs
- **Stretch Factors**: Use stretch in layouts for flexible sizing
- **Size Policies**: Set appropriate size policies for widgets
- **Minimum Sizes**: Set minimum sizes to prevent UI from breaking

### 3. Custom Widgets

For custom widgets (like ThumbnailList), you have two options:

**Option A: Use as Programmatic Widget** (Current approach)
```python
# In mainWindow.py
self._thumbnail_list = ThumbnailList()  # Create programmatically
layout.addWidget(self._thumbnail_list)
```

**Option B: Promote Widget in Qt Designer**
1. Add a QWidget placeholder in Qt Designer
2. Right-click → "Promote to..."
3. Enter custom class name: `ThumbnailList`
4. Enter header file: `widgets.thumbnailList`
5. Click "Add" then "Promote"

The project currently uses **Option A** for simplicity.

### 4. Signal/Slot Connections

**In Qt Designer**:
- Can create basic connections (Signal/Slot Editor)
- Limited to standard signals/slots

**In Python** (Recommended):
- More flexible and maintainable
- Connect after loading UI
- Better for custom signals

```python
# Connect in Python, not Qt Designer
self.btnSave.clicked.connect(self._on_save)
self.entSearch.textChanged.connect(self._on_search_changed)
```

### 5. Iterative Development

1. **Start Simple**: Create basic layout in Qt Designer
2. **Test in App**: Load and test functionality
3. **Iterate**: Go back to Qt Designer to refine
4. **Add Logic**: Implement business logic in Python

## Examples

### Example 1: Simple Form Widget

**In Qt Designer**:
1. Create new Widget template
2. Add QVBoxLayout to main widget
3. Add QLabel "Username:" → name: `lblUsername`
4. Add QLineEdit → name: `entUsername`
5. Add QPushButton "Submit" → name: `btnSubmit`
6. Save as `simpleForm.ui`

**In Python**:
```python
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

class SimpleForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._load_ui()
        self._connect_signals()
    
    def _load_ui(self):
        """Load UI from .ui file."""
        ui_path = Path(__file__).parent / "simpleForm.ui"
        loader = QUiLoader()
        ui_file = QFile(str(ui_path))
        ui_file.open(QFile.ReadOnly)
        ui_widget = loader.load(ui_file, self)
        ui_file.close()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(ui_widget)
        
        # Store widget references
        self.btnSubmit = ui_widget.findChild(QPushButton, "btnSubmit")
        self.entUsername = ui_widget.findChild(QLineEdit, "entUsername")
    
    def _connect_signals(self):
        """Connect widget signals."""
        self.btnSubmit.clicked.connect(self._on_submit)
    
    def _on_submit(self):
        """Handle submit button click."""
        username = self.entUsername.text()
        QMessageBox.information(self, "Submitted", f"Username: {username}")
```

### Example 2: Dialog with Layouts

**In Qt Designer**:
1. Create new Dialog template
2. Set dialog properties (title, size)
3. Add QGridLayout
4. Add labels, line edits, buttons in grid
5. Name all widgets with proper prefixes
6. Add button box with OK/Cancel
7. Save as `settingsDialog.ui`

**In Python**:
```python
from PySide6.QtWidgets import QDialog

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._load_ui()
        self._connect_signals()
        # Dialog-specific initialization
```

### Example 3: Main Window

**mainWindow.ui** structure:
- QMainWindow with central widget
- Menu bar with File, Edit, Help menus
- Tool bar with common actions
- Status bar
- Central widget with main layout
- Dock widgets for panels (optional)

**In Python**:
```python
from PySide6.QtWidgets import QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Option 1: Load entire UI from .ui file (if using .ui)
        # self._load_ui()
        
        # Option 2: Mix - load some from .ui, create others programmatically
        self._setup_ui()  # Programmatic approach (current)
        self._create_menu_bar()
```

## When to Use .ui Files vs Programmatic

### Use .ui Files When:
- ✅ UI is mostly static layout
- ✅ Design needs frequent visual tweaking
- ✅ Working with designers who prefer visual tools
- ✅ Simple forms and dialogs
- ✅ Complex layouts that are hard to code

### Use Programmatic Creation When:
- ✅ UI is highly dynamic
- ✅ Lots of conditional widget creation
- ✅ Custom widget behavior
- ✅ Need fine-grained control
- ✅ Complex signal/slot connections

### Hybrid Approach (Recommended)
- Use .ui files for static layouts (dialogs, forms)
- Use Python for dynamic content (lists, custom widgets)
- This is what Sidecar Editor does currently

## Troubleshooting

### UI File Not Found
```python
# Use absolute path or Path relative to module
from pathlib import Path
ui_path = Path(__file__).parent / "myWidget.ui"
```

### Widgets Not Found After Loading
```python
# Use findChild to locate widgets in loaded UI
self.btnSave = ui_widget.findChild(QPushButton, "btnSave")
if not self.btnSave:
    print("Widget 'btnSave' not found in UI!")
```

### Qt Designer Shows Wrong Widgets
- Check that PySide6 is properly installed
- Restart Qt Designer after installing new widgets
- For custom widgets, use "Promote Widget" feature

### Layout Issues
- Make sure main widget has a layout set
- Check size policies on widgets
- Use spacers for flexible spacing
- Preview in Qt Designer (Form → Preview)

### Changes Not Reflecting
- Make sure .ui file is saved
- Check file path is correct
- Restart application to reload .ui file
- Check for cached .pyc files if using compiled approach

## Summary

### Quick Start Checklist

1. ✅ Install PySide6 (already in requirements.txt)
2. ✅ Open Qt Designer
3. ✅ Create .ui file with proper widget names
4. ✅ Save in appropriate directory
5. ✅ Load in Python using QUiLoader
6. ✅ Connect signals and implement logic
7. ✅ Test and iterate

### Key Points to Remember

- **Naming**: Always use proper prefixes (btn, lbl, ent, etc.)
- **Layouts**: Always use layouts, never absolute positioning
- **Loading**: Use QUiLoader for dynamic loading
- **Separation**: Keep UI design separate from business logic
- **Iteration**: Design in Qt Designer, implement in Python

## Additional Resources

- [Qt Designer Manual](https://doc.qt.io/qt-6/qtdesigner-manual.html)
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [Qt Layouts Guide](https://doc.qt.io/qt-6/layout.html)
- [QUiLoader Documentation](https://doc.qt.io/qtforpython-6/PySide6/QtUiTools/QUiLoader.html)

---

**Happy Designing!** 🎨
