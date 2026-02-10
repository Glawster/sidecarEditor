# Qt Designer Workflow for Sidecar Editor

This document provides a step-by-step workflow for using Qt Designer to create and modify UI components in the Sidecar Editor project.

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Complete Workflow](#complete-workflow)
4. [Example: Creating a New Widget](#example-creating-a-new-widget)
5. [Example: Modifying an Existing Widget](#example-modifying-an-existing-widget)
6. [Tips and Best Practices](#tips-and-best-practices)

## Overview

The Sidecar Editor uses a **hybrid approach**:
- **Static layouts** are designed in Qt Designer (.ui files)
- **Dynamic components** are created programmatically in Python
- **Custom widgets** (ThumbnailList) remain fully programmatic

This provides the best of both worlds:
- Visual design for forms and layouts
- Full control for complex dynamic UIs

## Project Structure

```
sidecarEditor/
├── Qt/
│   ├── mainWindow.py          # Main window (currently programmatic)
│   ├── mainWindow.ui           # Main window UI (optional, for reference)
│   └── widgets/
│       ├── editorPanel.py      # Editor panel widget
│       ├── editorPanel.ui      # Editor panel UI file
│       ├── imagePreview.py     # Image preview widget
│       ├── imagePreview.ui     # Image preview UI file
│       ├── thumbnailList.py    # Thumbnail list (fully programmatic)
│       ├── exampleWidget.py    # Example showing .ui integration
│       └── exampleWidget.ui    # Example UI file
```

## Complete Workflow

### Step 1: Design in Qt Designer

1. **Launch Qt Designer**
   ```bash
   # Find Qt Designer (varies by platform)
   python -c "import PySide6; print(PySide6.__path__)"
   # Or if installed separately:
   designer  # Linux/macOS
   designer.exe  # Windows
   ```

2. **Create New .ui File**
   - File → New Form
   - Choose template:
     - `Widget` for general widgets
     - `Main Window` for top-level windows
     - `Dialog` for dialogs
   - Click "Create"

3. **Design Your UI**
   - Drag widgets from Widget Box
   - Set properties in Property Editor
   - Create layouts (right-click → Lay Out)
   - Name widgets with proper prefixes

4. **Name Widgets Properly**
   
   **IMPORTANT**: Follow naming conventions!
   
   - `btnSave` - Save button
   - `lblStatus` - Status label
   - `entUsername` - Username entry
   - `txtDescription` - Text area
   - `frmContainer` - Container frame
   
   See [QT_DESIGNER_GUIDE.md](QT_DESIGNER_GUIDE.md) for full naming rules.

5. **Save .ui File**
   - Save in same directory as corresponding .py file
   - Use same base name: `myWidget.py` → `myWidget.ui`

### Step 2: Load UI in Python

Create or modify the Python file:

```python
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._load_ui()
        self._connect_signals()
    
    def _load_ui(self):
        """Load UI from .ui file."""
        ui_path = Path(__file__).parent / "myWidget.ui"
        
        loader = QUiLoader()
        ui_file = QFile(str(ui_path))
        ui_file.open(QFile.ReadOnly)
        ui_widget = loader.load(ui_file, self)
        ui_file.close()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(ui_widget)
        
        # Find widgets
        self.btnSave = ui_widget.findChild(QPushButton, "btnSave")
        self.lblStatus = ui_widget.findChild(QLabel, "lblStatus")
    
    def _connect_signals(self):
        """Connect widget signals to slots."""
        self.btnSave.clicked.connect(self._on_save)
    
    def _on_save(self):
        """Handle save button click."""
        # Implement save logic
        pass
```

### Step 3: Test Your Widget

1. **Run the Application**
   ```bash
   cd /path/to/sidecarEditor
   python -m sidecarEditor
   ```

2. **Test Standalone** (for individual widgets)
   ```python
   # Add to bottom of your widget file
   if __name__ == "__main__":
       import sys
       from PySide6.QtWidgets import QApplication
       
       app = QApplication(sys.argv)
       widget = MyWidget()
       widget.show()
       sys.exit(app.exec())
   ```

3. **Run Standalone**
   ```bash
   python Qt/widgets/myWidget.py
   ```

### Step 4: Iterate

1. **Modify in Qt Designer**
   - Open .ui file in Qt Designer
   - Make changes
   - Save

2. **Reload in Application**
   - Restart the application
   - Changes are loaded automatically (dynamic loading)

3. **Update Python if Needed**
   - Add new widget references
   - Update signal connections
   - Implement new functionality

## Example: Creating a New Widget

Let's create a "Settings Panel" widget from scratch.

### 1. Design in Qt Designer

1. Open Qt Designer
2. File → New Form → Widget
3. Add widgets:
   - QLabel: "Settings" (name: `lblTitle`)
   - QCheckBox: "Enable Auto-Save" (name: `chkAutoSave`)
   - QCheckBox: "Dark Mode" (name: `chkDarkMode`)
   - QPushButton: "Apply" (name: `btnApply`)
   - QPushButton: "Cancel" (name: `btnCancel`)
4. Apply layouts:
   - Right-click main widget → Lay Out Vertically
5. Save as: `Qt/widgets/settingsPanel.ui`

### 2. Create Python File

Create `Qt/widgets/settingsPanel.py`:

```python
"""Settings panel widget."""

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QPushButton
from PySide6.QtCore import QFile, Signal
from PySide6.QtUiTools import QUiLoader


class SettingsPanel(QWidget):
    """Settings panel for application preferences."""
    
    settingsChanged = Signal(dict)  # Emit when settings change
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._load_ui()
        self._connect_signals()
    
    def _load_ui(self):
        """Load UI from .ui file."""
        ui_path = Path(__file__).parent / "settingsPanel.ui"
        
        loader = QUiLoader()
        ui_file = QFile(str(ui_path))
        ui_file.open(QFile.ReadOnly)
        ui_widget = loader.load(ui_file, self)
        ui_file.close()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(ui_widget)
        
        # Find widgets
        self.chkAutoSave = ui_widget.findChild(QCheckBox, "chkAutoSave")
        self.chkDarkMode = ui_widget.findChild(QCheckBox, "chkDarkMode")
        self.btnApply = ui_widget.findChild(QPushButton, "btnApply")
        self.btnCancel = ui_widget.findChild(QPushButton, "btnCancel")
    
    def _connect_signals(self):
        """Connect signals."""
        self.btnApply.clicked.connect(self._on_apply)
        self.btnCancel.clicked.connect(self._on_cancel)
    
    def _on_apply(self):
        """Apply settings."""
        settings = {
            'auto_save': self.chkAutoSave.isChecked(),
            'dark_mode': self.chkDarkMode.isChecked(),
        }
        self.settingsChanged.emit(settings)
    
    def _on_cancel(self):
        """Cancel changes."""
        self.close()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    panel = SettingsPanel()
    panel.show()
    sys.exit(app.exec())
```

### 3. Test

```bash
# Test standalone
python Qt/widgets/settingsPanel.py

# Or integrate into main application
# (Add to MainWindow as a dialog or panel)
```

## Example: Modifying an Existing Widget

Let's modify the `editorPanel` widget to add a word count label.

### 1. Open in Qt Designer

1. Launch Qt Designer
2. File → Open: `Qt/widgets/editorPanel.ui`
3. You'll see the existing layout with:
   - Prompt group box
   - Negative prompt group box
   - Tags label
   - Button bar

### 2. Add New Widget

1. Drag a `QLabel` from Widget Box
2. Place it below the "Tags" label
3. Set properties:
   - `objectName`: `lblWordCount`
   - `text`: `Words: 0`
   - `styleSheet`: `color: gray;`
4. Save the file

### 3. Update Python Code

Edit `Qt/widgets/editorPanel.py`:

```python
def _setup_ui(self):
    """Set up the user interface."""
    # ... existing code ...
    
    # Find the new widget
    self._word_count_label = ui_widget.findChild(QLabel, "lblWordCount")
    
    # Connect to update word count
    self._prompt_edit.textChanged.connect(self._update_word_count)

def _update_word_count(self):
    """Update word count display."""
    text = self._prompt_edit.toPlainText()
    word_count = len(text.split())
    self._word_count_label.setText(f"Words: {word_count}")
```

### 4. Test

```bash
python -m sidecarEditor
```

The word count should now update as you type!

## Tips and Best Practices

### Naming Widgets

✅ **DO**:
- Use descriptive names: `btnSaveSettings`, not `btn1`
- Follow prefix conventions: `btnSave`, `lblStatus`, `entName`
- Be consistent across the project

❌ **DON'T**:
- Use generic names: `button`, `label1`, `widget`
- Mix naming styles: `saveBtn`, `btnSave` in same project
- Ignore naming conventions

### Layout Strategy

✅ **DO**:
- Use layouts for everything
- Nest layouts for complex UIs
- Use spacers for flexible spacing
- Set proper size policies

❌ **DON'T**:
- Use absolute positioning (geometry)
- Hard-code sizes unnecessarily
- Forget to add stretches

### Signal Connections

✅ **DO**:
- Connect signals in Python code
- Keep connections in `_connect_signals()` method
- Use descriptive slot names: `_on_save`, not `_slot1`

❌ **DON'T**:
- Connect signals in Qt Designer (limited and less maintainable)
- Scatter connections throughout the code
- Use lambda for complex logic

### Testing

✅ **DO**:
- Test widgets standalone first
- Use `if __name__ == "__main__"` for quick testing
- Test in actual application context

❌ **DON'T**:
- Only test in full application
- Skip edge cases
- Forget to test layouts at different sizes

### Version Control

✅ **DO**:
- Commit .ui files with corresponding .py files
- Keep .ui files in same directory as .py files
- Document major UI changes in commit messages

❌ **DON'T**:
- Commit generated Python files from `pyside6-uic` (if using that approach)
- Separate .ui files from their Python counterparts
- Make large UI changes without testing

## When to Use .ui Files vs Python

### Use .ui Files For:
- ✅ Static layouts (forms, dialogs)
- ✅ Simple controls and inputs
- ✅ Preference panels
- ✅ About dialogs
- ✅ Settings windows

### Use Python For:
- ✅ Dynamic content (lists, tables that change)
- ✅ Custom widgets with special behavior
- ✅ Complex signal/slot logic
- ✅ Programmatic widget creation
- ✅ Widgets that need fine-grained control

### Current Sidecar Editor Approach:
- **MainWindow**: Python (complex layout with dynamic splitters)
- **EditorPanel**: Can use .ui for static layout
- **ImagePreview**: Can use .ui for basic layout
- **ThumbnailList**: Python (custom list behavior)

## Troubleshooting

### Widget Not Found After Loading

**Problem**: `findChild` returns `None`

**Solution**:
1. Check widget name in Qt Designer (objectName property)
2. Ensure .ui file is saved
3. Verify path to .ui file is correct
4. Check for typos in widget name

### Layout Not Working

**Problem**: Widgets overlap or don't resize

**Solution**:
1. Ensure main widget has a layout
2. Check all container widgets have layouts
3. Set proper size policies
4. Use spacers for flexible spacing

### Changes Not Appearing

**Problem**: Modified .ui file but no changes in app

**Solution**:
1. Save .ui file in Qt Designer
2. Restart application (dynamic loading)
3. Check correct .ui file is being loaded
4. Verify file path in Python code

## Additional Resources

- [Qt Designer Guide](QT_DESIGNER_GUIDE.md) - Comprehensive guide
- [Qt Layouts Tutorial](https://doc.qt.io/qt-6/layout.html)
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)

## Summary

The Qt Designer workflow for Sidecar Editor:

1. **Design** in Qt Designer (visual tool)
2. **Save** .ui file with proper naming
3. **Load** in Python using QUiLoader
4. **Connect** signals in Python
5. **Test** standalone and in context
6. **Iterate** by modifying .ui file

This approach provides:
- Visual design for static layouts
- Full Python control for logic
- Easy iteration and modification
- Clear separation of concerns

---

Happy designing! 🎨
