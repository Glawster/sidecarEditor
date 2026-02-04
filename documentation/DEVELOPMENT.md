# Sidecar Editor Development Guide

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

### Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/Glawster/sidecarEditor.git
cd sidecarEditor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install development dependencies (optional):
```bash
pip install -r dev-requirements.txt
```

### Running the Application

From the repository root:

```bash
python -m sidecarEditor
```

### Development Mode

For development, you can run directly:

```bash
cd sidecarEditor
python __main__.py
```

## Project Structure

```
sidecarEditor/
├── src/                      # Core business logic (no Qt)
│   ├── sidecarCore.py       # Sidecar file management
│   ├── outputResolver.py    # Output image resolution
│   └── sidecarConfig.py     # Configuration management
│
├── ui/                       # Qt user interface
│   ├── mainWindow.py        # Main application window
│   └── widgets/             # Custom Qt widgets
│
├── documentation/            # Documentation files
├── tests/                    # Test files (if added)
├── __main__.py              # Entry point
├── requirements.txt         # Runtime dependencies
└── dev-requirements.txt     # Development dependencies
```

## Coding Standards

### Python Style

- Follow PEP 8 style guidelines
- Use type hints where helpful
- Write clear, readable code over clever code
- Document public functions and classes

### Import Organization

1. Standard library imports
2. Third-party imports (PySide6, etc.)
3. Local imports (from src, from ui)

Example:
```python
import json
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QWidget

from ..src.sidecarCore import SidecarData
```

### Separation of Concerns

**CRITICAL**: Core logic (`src/`) must have ZERO Qt dependencies.

✅ Good:
```python
# In src/sidecarCore.py
def scan_images(root_path: str) -> List[str]:
    """Scan directory for images (no Qt)."""
    ...
```

❌ Bad:
```python
# In src/sidecarCore.py
from PySide6.QtCore import QDir  # NO! Qt in core logic

def scan_images(root_path: str) -> List[str]:
    dir = QDir(root_path)  # NO!
    ...
```

### Naming Conventions

- **Classes**: PascalCase (`SidecarData`, `MainWindow`)
- **Functions**: snake_case (`load_sidecar`, `scan_images`)
- **Constants**: UPPER_SNAKE_CASE (`DEFAULT_EXTENSIONS`)
- **Private members**: Leading underscore (`_internal_method`)

## Adding Features

### Adding a New Core Function

1. Implement in appropriate `src/` module
2. Add type hints
3. Add docstring
4. Test independently of UI
5. Update API.md documentation

Example:
```python
# In src/sidecarCore.py

def validate_sidecar(sidecar: SidecarData) -> bool:
    """
    Validate sidecar data.
    
    Args:
        sidecar: SidecarData to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not sidecar.prompt:
        return False
    # More validation...
    return True
```

### Adding a New UI Widget

1. Create in `ui/widgets/`
2. Inherit from appropriate Qt class
3. Use signals for communication
4. Keep logic minimal (delegate to core)
5. Update ARCHITECTURE.md

Example:
```python
# In ui/widgets/tagEditor.py

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal

class TagEditor(QWidget):
    """Widget for editing tags."""
    
    tagsChanged = Signal(list)  # Emit when tags change
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        # Build UI...
        pass
```

### Adding Configuration Options

1. Add getter/setter in `sidecarConfig.py`
2. Use under `sidecarEditor` config key
3. Update configuration documentation

Example:
```python
# In src/sidecarConfig.py

def get_theme() -> str:
    """Get UI theme preference."""
    section = _get_sidecar_section()
    return section.get('theme', 'default')

def set_theme(theme: str):
    """Set UI theme preference."""
    section = _get_sidecar_section()
    section['theme'] = theme
    _save_sidecar_section(section)
```

## Testing

### Manual Testing

1. Create test images:
```bash
mkdir -p /tmp/test_images
# Add some .png or .jpg files
```

2. Run the application:
```bash
python -m sidecarEditor
```

3. Test workflow:
   - Set input folder to `/tmp/test_images`
   - Select an image
   - Edit the prompt
   - Save the sidecar
   - Verify `.prompt.json` and `.prompt.json.bak` files created

### Automated Testing

Create test files in `tests/` directory:

```python
# tests/test_sidecar_core.py

import tempfile
from pathlib import Path
from src.sidecarCore import SidecarData, save_sidecar, load_sidecar

def test_save_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        image_path = str(Path(tmpdir) / "test.png")
        Path(image_path).touch()
        
        # Create and save
        sidecar = SidecarData(
            image_path=image_path,
            prompt="Test prompt"
        )
        save_sidecar(sidecar)
        
        # Load and verify
        loaded = load_sidecar(image_path)
        assert loaded.prompt == "Test prompt"
```

Run tests with pytest:
```bash
pytest tests/
```

## Debugging

### Print Debugging

Add debug prints in core logic:

```python
def load_sidecar(image_path: str) -> SidecarData:
    sidecar_path = get_sidecar_path(image_path)
    print(f"DEBUG: Loading sidecar from {sidecar_path}")  # Debug line
    ...
```

### Qt Debugging

Use Qt's debugging features:

```python
# In UI code
from PySide6.QtCore import qDebug

qDebug(f"Image selected: {image_path}")
```

### Logging

Add logging support (future enhancement):

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Loading sidecar...")
```

## Common Tasks

### Adding a New Menu Item

In `ui/mainWindow.py`:

```python
def _create_menu_bar(self):
    menubar = self.menuBar()
    
    # Add to existing menu
    file_menu = menubar.addMenu("&File")
    
    action_export = QAction("&Export...", self)
    action_export.setShortcut("Ctrl+E")
    action_export.triggered.connect(self._on_export)
    file_menu.addAction(action_export)

def _on_export(self):
    """Handle export action."""
    # Implementation...
    pass
```

### Adding a New Signal/Slot Connection

```python
# In widget
class MyWidget(QWidget):
    dataChanged = Signal(str)  # Define signal
    
    def _do_something(self):
        self.dataChanged.emit("new data")  # Emit signal

# In parent/consumer
widget = MyWidget()
widget.dataChanged.connect(self._on_data_changed)  # Connect slot

def _on_data_changed(self, data: str):
    print(f"Data changed: {data}")
```

### Updating Configuration Schema

1. Update `sidecarConfig.py` with new getters/setters
2. Update documentation in API.md
3. Update ARCHITECTURE.md configuration section
4. Test configuration persistence

## Building and Packaging

### Creating a Distribution

(To be added when packaging is implemented)

Planned approaches:
- PyInstaller for standalone executables
- Python wheel for pip installation
- Platform-specific installers (MSI, DMG, DEB)

## Code Review Checklist

Before submitting changes:

- [ ] Core logic has no Qt imports
- [ ] Type hints added to public functions
- [ ] Docstrings added to public functions/classes
- [ ] Code follows PEP 8 style
- [ ] No hardcoded paths or config values
- [ ] Error handling added where appropriate
- [ ] Manual testing completed
- [ ] Documentation updated (if needed)
- [ ] No debug print statements left in code

## Troubleshooting

### Qt Platform Plugin Error

If you see "Could not load the Qt platform plugin":

**Linux:**
```bash
sudo apt-get install libxcb-cursor0
```

**macOS:**
```bash
brew install qt6
```

**Windows:**
Usually works out of the box with `pip install PySide6`

### Import Errors

If you see "No module named 'ui'" or "No module named 'src'":

Make sure you're running from the correct directory:

```bash
# Wrong:
cd sidecarEditor/sidecarEditor
python -m sidecarEditor  # Will fail

# Correct:
cd sidecarEditor  # Parent of sidecarEditor package
python -m sidecarEditor  # Works
```

### Configuration Not Persisting

Check that `~/.config/kohya/` is writable:

```bash
ls -ld ~/.config/kohya/
# Should show write permissions
```

### Images Not Displaying

Check supported formats:
- Supported: PNG, JPG, JPEG, GIF, BMP, WEBP
- Files must have correct extensions
- Files must be readable

## Contributing

### Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes
4. Test thoroughly
5. Commit: `git commit -m "Add my feature"`
6. Push: `git push origin feature/my-feature`
7. Create pull request

### Commit Messages

Use clear, descriptive commit messages:

✅ Good:
- "Add tag editing widget"
- "Fix output resolution for nested directories"
- "Update documentation for new config options"

❌ Bad:
- "Update"
- "Fix bug"
- "WIP"

## Development Tools

### Recommended IDE Setup

**VS Code:**
- Python extension
- Qt for Python extension
- Pylint
- Black formatter

**PyCharm:**
- Professional or Community edition
- Qt support plugin

### Useful Commands

```bash
# Format code with black
black sidecarEditor/

# Check style with pylint
pylint sidecarEditor/src/

# Type checking with mypy (future)
mypy sidecarEditor/src/

# Run tests
pytest tests/

# Generate documentation (future)
sphinx-build docs/ docs/_build/
```

## Resources

### Documentation

- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [Qt Documentation](https://doc.qt.io/)
- [Python Documentation](https://docs.python.org/3/)

### Learning Resources

- PySide6 tutorials
- Qt Layout management
- Signal/Slot mechanism
- Python async programming (for future enhancements)

## FAQ

**Q: Why separate core logic from UI?**
A: Enables CLI tools, batch processing, and testing without Qt dependencies.

**Q: Why PySide6 instead of Tkinter?**
A: Better cross-platform support, modern UI, richer widget set, better integration with desktop environments.

**Q: Can I add Tkinter widgets?**
A: No, the project uses Qt exclusively. Tkinter is not compatible with Qt.

**Q: How do I add a new file format?**
A: Update `DEFAULT_EXTENSIONS` in `sidecarCore.py` and test thoroughly.

**Q: Where is the logging configured?**
A: Logging is not yet implemented. It's a planned future enhancement.

**Q: How do I run on a headless server?**
A: Use `QT_QPA_PLATFORM=offscreen` for testing. For production, use the planned CLI tools.

## Next Steps

After completing the MVP, planned enhancements include:

1. Comprehensive test suite
2. CLI tool for batch operations
3. Drag-and-drop support
4. Undo/redo functionality
5. LLaVA integration
6. Theme support
7. Plugin system
8. Automated builds/packaging

For questions or issues, please open an issue on GitHub.
