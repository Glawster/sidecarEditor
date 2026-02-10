# Sidecar Editor - Project-Specific Copilot Instructions

## Project Overview

Sidecar Editor is a **Qt/PySide6** desktop application for editing image prompt sidecar files. It follows a clean architecture with strict separation between core business logic and UI layer.

**Important**: This project uses **PySide6 (Qt)**, NOT Tkinter. The generic `copilot-instructions.md` in `.github/` contains Tkinter guidelines that do NOT apply to this project. Follow the Qt-specific patterns described here.

## Architecture

### Core Principles

1. **Separation of Concerns**: Core logic (`src/`) has ZERO Qt dependencies
2. **Qt UI Layer**: All Qt code lives in `Qt/` directory
3. **Reusable Core**: Business logic can be used by CLI tools or batch processors
4. **Configuration**: Uses existing kohyaConfig.py under `"sidecarEditor"` key

### Directory Structure

```
sidecarEditor/
├── src/              # Core business logic (NO Qt imports allowed)
│   ├── sidecarCore.py       # Sidecar file management
│   ├── outputResolver.py    # Output image resolution
│   └── sidecarConfig.py     # Configuration management
├── Qt/               # Qt user interface layer
│   ├── mainWindow.py        # Main application window
│   └── widgets/             # Custom Qt widgets
├── documentation/    # All documentation files
└── tests/            # Test files
```

### Critical Rule: NO Qt in Core Logic

❌ **NEVER** import Qt in `src/` modules:
```python
# WRONG - In src/sidecarCore.py
from PySide6.QtCore import QDir  # NO!
```

✅ **ALWAYS** keep core logic pure Python:
```python
# CORRECT - In src/sidecarCore.py
from pathlib import Path
import json
```

## Coding Standards

### Naming Conventions

This project uses **PySide6 (Qt)**, which follows different conventions than Tkinter:

- **Classes**: PascalCase (`MainWindow`, `SidecarData`, `OutputResolver`)
- **Functions and Variables**: snake_case (`load_sidecar`, `scan_images`, `image_path`)
- **Constants**: UPPER_SNAKE_CASE (`DEFAULT_EXTENSIONS`, `SIDECAR_SUFFIX`)
- **Private Members**: Leading underscore (`_internal_method`, `_setup_ui`)
- **Files**: camelCase for Python modules (`sidecarCore.py`, `outputResolver.py`)

### UI Widget Naming (Qt/PySide6)

While the generic instructions reference Tkinter widget prefixes (btn, lbl, frm), this project uses standard Qt naming:

**Qt Widget Convention:**
- Use descriptive names without mandatory prefixes
- Follow Qt naming patterns: `thumbnailList`, `imagePreview`, `editorPanel`
- Private UI setup methods: `_setup_ui()`, `_create_menu_bar()`

**Example (Qt style):**
```python
from PySide6.QtWidgets import QMainWindow, QPushButton, QLabel

class MainWindow(QMainWindow):
    def _setup_ui(self):
        self.save_button = QPushButton("Save")
        self.status_label = QLabel("Ready")
```

**NOT the Tkinter style** (from generic instructions):
```python
# This is Tkinter - DO NOT use in this project
import tkinter as tk
self.btnSave = tk.Button(...)  # Wrong framework
```

### Function Formatting Rules

Functions with **more than 4 logical statements** must include **a blank line after the `def` line**:

✅ **Correct:**
```python
def short_method(self):
    return True

def longer_method(self, data):

    validated = self._validate(data)
    processed = self._process(validated)
    result = self._transform(processed)
    self._store(result)
    return result
```

❌ **Incorrect:**
```python
def longer_method(self, data):
    validated = self._validate(data)  # Missing blank line after def
    processed = self._process(validated)
    result = self._transform(processed)
    self._store(result)
    return result
```

## Logging Standards

### Logging Format Rules

All logging must follow these conventions:

1. **Message Format**: Keep messages **lowercase** unless logging an error
2. **Major Actions**: `"...doing something"` - action being initiated
3. **Action Completion**: `"...something done"` - action completed
4. **General Updates**: `"...message"` - informational updates
5. **Information Display**: `"...key: value"` - reporting variables
6. **Error Messages**: Use **Sentence Case** for ERROR level messages

### Logging Examples

```python
import logging

logger = logging.getLogger(__name__)

def load_sidecar(image_path: str):
    """Load sidecar with proper logging."""
    try:
        logger.info("...loading sidecar")
        logger.info(f"...image path: {image_path}")
        
        # Do work
        sidecar = _read_sidecar_file(image_path)
        
        logger.info("...sidecar loaded")
        return sidecar
        
    except FileNotFoundError as e:
        logger.error(f"Sidecar file not found: {image_path}")
        raise
    except Exception as e:
        logger.error(f"Failed to load sidecar: {e}")
        raise
```

### Logging Guidelines

- Use centralized logging configuration (when available)
- Include module name and operation context
- Log at appropriate levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Store logs with timestamp and rotation as appropriate
- When logging collections, log one entry per line or as a formatted list

## Development Patterns

### Import Organization

1. Standard library imports
2. Third-party imports (PySide6, etc.)
3. Local imports (from src, from Qt)

```python
import json
from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import QWidget, QPushButton
from PySide6.QtCore import Signal

from ..src.sidecarCore import SidecarData
```

### Error Handling

- Implement graceful degradation for non-critical failures
- Provide user-actionable error messages
- Validate input before processing
- Use try-except blocks with proper logging
- Log errors with sufficient context for debugging
- Maintain application stability during errors

### Qt Signal/Slot Pattern

Use Qt's signal/slot mechanism for communication:

```python
from PySide6.QtCore import Signal

class EditorPanel(QWidget):
    """Panel for editing sidecar data."""
    
    # Define signals
    sidecarChanged = Signal(object)
    saveRequested = Signal()
    
    def _on_text_changed(self):
        """Handle text changes."""
        self.sidecarChanged.emit(self._get_sidecar_data())
```

### Adding New Features

#### Adding Core Functionality

1. Implement in appropriate `src/` module
2. NO Qt dependencies allowed
3. Add type hints
4. Add docstring
5. Test independently of UI
6. Update API.md documentation

#### Adding UI Components

1. Create in `Qt/widgets/` directory
2. Inherit from appropriate Qt class
3. Use signals for communication
4. Keep logic minimal (delegate to core)
5. Update ARCHITECTURE.md

#### Adding Configuration

1. Add getter/setter in `sidecarConfig.py`
2. Use under `sidecarEditor` config key
3. Update documentation

## Testing

### Test Structure

- Use pytest conventions (`test_*.py` files, `test_*` functions)
- Create focused, single-purpose test functions
- Use `tmp_path` fixture for temporary file/directory testing
- Mock external dependencies appropriately
- Test core logic independently of Qt UI

### Test Example

```python
from pathlib import Path
from src.sidecarCore import SidecarData, save_sidecar, load_sidecar

def test_save_and_load(tmp_path):
    """Test sidecar save and load."""
    # Arrange
    image_path = str(tmp_path / "test.png")
    Path(image_path).touch()
    
    sidecar = SidecarData(
        image_path=image_path,
        prompt="Test prompt",
        negative_prompt="blur"
    )
    
    # Act
    save_sidecar(sidecar)
    loaded = load_sidecar(image_path)
    
    # Assert
    assert loaded.prompt == "Test prompt"
    assert loaded.negative_prompt == "blur"
```

## Configuration Management

### Using kohyaConfig

All configuration is stored under the `"sidecarEditor"` key:

```python
from src import sidecarConfig

# Get configuration
input_root = sidecarConfig.get_input_root()
output_root = sidecarConfig.get_output_root()

# Set configuration
sidecarConfig.set_input_root("/path/to/images")
sidecarConfig.set_output_root("/path/to/output")

# Window state
geometry = sidecarConfig.get_window_geometry()
sidecarConfig.set_window_geometry(geometry)
```

### Configuration Location

- Config file: `~/.config/kohya/kohyaConfig.json`
- All settings under `"sidecarEditor"` key
- Integrates with existing kohyaConfig ecosystem

## Sidecar File Conventions

### File Naming

```
image.png                    # Original image
image.png.prompt.json        # Sidecar file (editable)
image.png.prompt.json.bak    # Backup (auto-created on save)
```

### JSON Structure

```json
{
  "prompt": "A beautiful sunset over mountains",
  "negative_prompt": "blur, low quality",
  "tags": ["landscape", "sunset"],
  "metadata": {
    "model": "SD 1.5",
    "steps": 20
  }
}
```

### Default Behavior

- If sidecar doesn't exist, a minimal default is generated in memory
- Backups are created before saving (`.bak` suffix)
- Missing fields are filled with defaults

## Output Image Resolution

The application resolves original images to generated outputs using multiple strategies:

1. **Same Relative Path**: `input/folder/img.png` → `output/folder/img.png`
2. **Filename Match**: Find exact filename in output root
3. **Stem-Prefix Match**: `img.png` matches `img_001.png`, `img_final.png`

Implemented in `src/outputResolver.py`.

## Common Tasks

### Adding a Menu Item

```python
def _create_menu_bar(self):
    menubar = self.menuBar()
    file_menu = menubar.addMenu("&File")
    
    action_export = QAction("&Export...", self)
    action_export.setShortcut("Ctrl+E")
    action_export.triggered.connect(self._on_export)
    file_menu.addAction(action_export)
```

### Creating Custom Widgets

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal

class CustomWidget(QWidget):
    """Custom widget for specific functionality."""
    
    actionTriggered = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        button = QPushButton("Action")
        button.clicked.connect(self._on_action)
        layout.addWidget(button)
    
    def _on_action(self):
        self.actionTriggered.emit("action_data")
```

## Documentation Files

- **README.md**: Quick start and overview
- **ARCHITECTURE.md**: Technical architecture
- **DEVELOPMENT.md**: Development guide and coding standards
- **API.md**: API reference for core modules
- **USER_GUIDE.md**: User documentation
- **projectGuidelines.md**: Linting rules and coding guidelines

## Best Practices

### Code Quality

- Write self-documenting code with clear names
- Keep functions short and focused (single responsibility)
- Use type hints for function signatures
- Add docstrings to public functions and classes
- Follow PEP 8 style guidelines

### Performance

- Profile before optimizing
- Use appropriate data structures
- Lazy load images in thumbnail view
- Cache expensive computations

### Security

- Validate all user input
- Never hardcode credentials
- Handle exceptions without leaking sensitive information
- Use secure file operations

### Maintainability

- Keep dependencies minimal and well-documented
- Write tests that document expected behavior
- Use version control effectively
- Document breaking changes

## Summary

**Key Takeaways:**

1. ✅ Use **PySide6 (Qt)**, NOT Tkinter
2. ✅ NO Qt imports in `src/` directory
3. ✅ Follow snake_case for functions, PascalCase for classes
4. ✅ Logging messages are lowercase (except errors)
5. ✅ Blank line after `def` for functions >4 lines
6. ✅ Use Qt signals/slots for component communication
7. ✅ Configuration under `"sidecarEditor"` key
8. ✅ Test core logic independently of UI

For more details, see:
- `/documentation/ARCHITECTURE.md` - Architecture details
- `/documentation/DEVELOPMENT.md` - Development guide
- `/documentation/API.md` - API reference
- `/documentation/projectGuidelines.md` - Linting and guidelines
