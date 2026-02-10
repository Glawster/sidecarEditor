# Qt Designer Quick Reference

Quick reference for using Qt Designer with Sidecar Editor.

## Widget Naming Conventions

| Widget Type | Prefix | Example |
|------------|--------|---------|
| QPushButton | `btn` | `btnSave` |
| QLabel | `lbl` | `lblStatus` |
| QLineEdit | `ent` | `entUsername` |
| QTextEdit | `txt` | `txtDescription` |
| QFrame/QWidget | `frm` | `frmContainer` |
| QListWidget | `lst` | `lstItems` |
| QComboBox | `cmb` | `cmbOptions` |
| QCheckBox | `chk` | `chkEnabled` |
| QRadioButton | `rad` | `radOption1` |
| QScrollBar | `scr` | `scrVertical` |

## Essential Qt Designer Actions

| Action | How To |
|--------|--------|
| **Create Layout** | Select widgets → Right-click → Lay Out → Choose layout type |
| **Set Object Name** | Select widget → Property Editor → objectName (at top) |
| **Add Spacer** | Drag Horizontal/Vertical Spacer from Widget Box |
| **Preview UI** | Form → Preview or Ctrl+R |
| **Adjust Tab Order** | Form → Tab Order |
| **Break Layout** | Select widget → Right-click → Break Layout |
| **Size Policy** | Property Editor → sizePolicy → Set horizontal/vertical |
| **Minimum Size** | Property Editor → minimumSize → Set width/height |

## Common Layouts

| Layout | When to Use | Properties |
|--------|-------------|------------|
| **QVBoxLayout** | Stack widgets vertically | Top to bottom |
| **QHBoxLayout** | Stack widgets horizontally | Left to right |
| **QGridLayout** | Grid of rows and columns | Complex forms |
| **QFormLayout** | Label-field pairs | Settings, forms |

## Loading .ui Files in Python

### Basic Template

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
        
        # Find widgets by objectName
        self.btnSave = ui_widget.findChild(QPushButton, "btnSave")
    
    def _connect_signals(self):
        """Connect signals to slots."""
        self.btnSave.clicked.connect(self._on_save)
    
    def _on_save(self):
        """Handle save action."""
        pass
```

## Common Signals

| Widget | Common Signals |
|--------|---------------|
| QPushButton | `clicked`, `pressed`, `released` |
| QLineEdit | `textChanged`, `textEdited`, `returnPressed` |
| QTextEdit | `textChanged`, `cursorPositionChanged` |
| QComboBox | `currentIndexChanged`, `currentTextChanged` |
| QCheckBox | `stateChanged`, `toggled` |
| QListWidget | `itemClicked`, `itemDoubleClicked`, `currentItemChanged` |

## Testing Widgets

### Standalone Test

Add to bottom of widget file:

```python
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
```

Run:
```bash
python Qt/widgets/myWidget.py
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Widget not found | Check objectName in Qt Designer |
| .ui file not loading | Verify path: `Path(__file__).parent / "widget.ui"` |
| Layout issues | Ensure all containers have layouts |
| Changes not showing | Restart app (dynamic loading) |
| Overlapping widgets | Use layouts instead of absolute positioning |

## File Organization

```
Qt/
├── mainWindow.py
├── mainWindow.ui          ← Optional
└── widgets/
    ├── myWidget.py
    └── myWidget.ui         ← Same name, same directory
```

## Size Policies

| Policy | Meaning |
|--------|---------|
| **Fixed** | Fixed size, doesn't resize |
| **Minimum** | Can grow but not shrink below minimum |
| **Maximum** | Can shrink but not grow above maximum |
| **Preferred** | Has preferred size, can grow/shrink |
| **Expanding** | Can grow/shrink, uses extra space |
| **MinimumExpanding** | Uses extra space, minimum size enforced |

## Workflow Checklist

- [ ] Design UI in Qt Designer
- [ ] Name all widgets with proper prefixes
- [ ] Use layouts (no absolute positioning)
- [ ] Save .ui file in correct directory
- [ ] Create Python file with same base name
- [ ] Load .ui file with QUiLoader
- [ ] Find widgets with findChild
- [ ] Connect signals in Python
- [ ] Test standalone
- [ ] Test in application
- [ ] Commit .ui and .py together

## Quick Commands

```bash
# Find Qt Designer
python -c "import PySide6; print(PySide6.__path__)"

# Run standalone widget
python Qt/widgets/myWidget.py

# Run full application
python -m sidecarEditor

# Lint code (check naming)
python tests/runLinter.py Qt/widgets/myWidget.py
```

## Resources

- [Full Qt Designer Guide](QT_DESIGNER_GUIDE.md)
- [Qt Designer Workflow](QT_DESIGNER_WORKFLOW.md)
- [Qt Documentation](https://doc.qt.io/qt-6/)
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)

---

**Quick Tip**: Always use layouts! Never use absolute positioning (`geometry`) in Qt Designer.
