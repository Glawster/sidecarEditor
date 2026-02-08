# Sidecar Editor - Project-Specific Copilot Instructions

## Project Overview

**Sidecar Editor** is a Qt (PySide6) desktop application for editing image prompt sidecar files. It's designed for managing LLaVA-generated captions and Stable Diffusion training data.

**Key Technologies:**
- Python 3.10+
- PySide6 (Qt 6)
- Pillow for image processing
- JSON for sidecar file format

## Project Structure

```
sidecarEditor/
├── src/                      # Core logic (NO Qt dependencies!)
│   ├── sidecarCore.py       # Sidecar file management
│   ├── outputResolver.py    # Output image resolution
│   └── sidecarConfig.py     # Configuration management
│
├── Qt/                       # Qt user interface ONLY
│   ├── mainWindow.py        # Main application window
│   └── widgets/             # Custom Qt widgets
│       ├── thumbnailList.py # Image thumbnail list
│       ├── imagePreview.py  # Image preview with toggle
│       └── editorPanel.py   # Sidecar editing panel
│
├── documentation/            # Comprehensive documentation
│   ├── ARCHITECTURE.md      # Architecture details
│   ├── DEVELOPMENT.md       # Development guide
│   ├── API.md               # API documentation
│   └── USER_GUIDE.md        # User guide
│
├── tests/                    # Test files
├── __main__.py              # Entry point
└── requirements.txt         # Dependencies
```

## Critical Architecture Rule

**ABSOLUTE REQUIREMENT**: Code in `src/` directory must have **ZERO Qt dependencies**.

✅ **Correct**:
```python
# In src/sidecarCore.py
from pathlib import Path
import json

def load_sidecar(image_path: str) -> SidecarData:
    """Load sidecar - pure Python, no Qt."""
    ...
```

❌ **WRONG** (Never do this):
```python
# In src/sidecarCore.py
from PySide6.QtCore import QFile  # NEVER! Qt in core logic
```

**Why?** Core logic must be reusable by CLI tools, batch processors, and other non-GUI applications.

## Naming Conventions

This project uses specific naming conventions:

- **Modules**: camelCase files (e.g., `sidecarCore.py`, `outputResolver.py`)
- **Functions**: snake_case (e.g., `load_sidecar()`, `scan_images()`, `get_sidecar_path()`)
- **Variables**: snake_case (e.g., `image_path`, `sidecar_data`, `output_root`)
- **Classes**: PascalCase (e.g., `SidecarData`, `OutputResolver`, `MainWindow`)
- **Qt Signals**: camelCase (e.g., `imageSelected`, `sidecarSaved`)
- **Constants**: UPPERCASE_WITH_UNDERSCORES (e.g., `DEFAULT_EXTENSIONS`, `SIDECAR_SUFFIX`)

## Sidecar File Format

Sidecar files are JSON files stored alongside images:

**File naming pattern:**
```
image.png                    # Original image
image.png.prompt.json        # Sidecar file (editable)
image.png.prompt.json.bak    # Backup (auto-created on save)
```

**JSON structure:**
```json
{
  "prompt": "A beautiful sunset over mountains",
  "negative_prompt": "blur, low quality",
  "tags": [],
  "metadata": {}
}
```

## Configuration Management

Configuration is stored in `~/.config/kohya/kohyaConfig.json` under the `"sidecarEditor"` key.

**Note**: This project integrates with the [kohyaConfig](https://github.com/Glawster/linuxMigration) ecosystem, which is a shared configuration system used across multiple tools in the author's workflow.

```json
{
  "sidecarEditor": {
    "inputRoot": "/path/to/images",
    "outputRoot": "/path/to/outputs",
    "lastSelectedImage": "/path/to/images/image.png",
    "windowGeometry": {
      "x": 100,
      "y": 100,
      "width": 1200,
      "height": 800
    }
  }
}
```

**Access via**: `src/sidecarConfig.py` functions

## Key Components

### Core Modules (src/)

#### sidecarCore.py
- `scan_images(root_path)` - Scan directory for images
- `load_sidecar(image_path)` - Load sidecar data
- `save_sidecar(sidecar, create_backup=True)` - Save sidecar
- `get_sidecar_path(image_path)` - Get sidecar file path
- `SidecarData` - Dataclass for sidecar content

#### outputResolver.py
- `OutputResolver` class - Resolve original → output images
- Strategies: relative path, filename match, stem-prefix match

#### sidecarConfig.py
- Configuration management wrapper
- Functions: `get_input_root()`, `set_input_root()`, etc.
- Window geometry persistence

### UI Modules (Qt/)

#### mainWindow.py
- Main application window
- Horizontal splitter layout
- Menu bar, status bar
- Coordinates widget interactions

#### Qt/widgets/thumbnailList.py
- Thumbnail grid view
- Emits `imageSelected` signal
- 100x100 thumbnail generation

#### Qt/widgets/imagePreview.py
- Image display with scaling
- Original ↔ Output toggle
- Handles missing output images

#### Qt/widgets/editorPanel.py
- Prompt editing interface
- Save/Revert buttons
- Emits `sidecarSaved` signal
- Unsaved changes tracking

## Development Workflows

### Running the Application

```bash
# From repository root
python -m sidecarEditor
```

### Adding a New Feature

1. **Core Logic First**: Implement in `src/` without Qt
2. **Test Core Logic**: Create tests for the core functionality
3. **Add UI Layer**: Create/modify Qt widgets in `Qt/`
4. **Connect Signals**: Wire up signal/slot connections
5. **Update Documentation**: Update relevant docs in `documentation/`

### Testing

```bash
# Run tests
pytest tests/

# Test specific file
pytest tests/test_sidecar_core.py
```

Use `tmp_path` fixture for file-based tests (automatic cleanup).

## Signal and Slot Patterns

### Widget Communication

```python
# In widget (define signal)
from PySide6.QtCore import Signal

class ThumbnailList(QListWidget):
    imageSelected = Signal(str)  # image_path
    
    def _on_selection_changed(self):
        self.imageSelected.emit(selected_path)

# In parent (connect slot)
self.thumbnail_list.imageSelected.connect(self._on_image_selected)

def _on_image_selected(self, image_path: str):
    """Handle image selection."""
    ...
```

## Common Patterns

### Loading an Image Flow

1. User clicks thumbnail in `ThumbnailList`
2. `ThumbnailList` emits `imageSelected(image_path)`
3. `MainWindow` receives signal
4. `MainWindow` calls `load_sidecar(image_path)` from core
5. `MainWindow` updates `ImagePreview` widget
6. `MainWindow` updates `EditorPanel` widget

### Saving a Sidecar Flow

1. User clicks "Save" in `EditorPanel`
2. `EditorPanel` reads text from QTextEdit widgets
3. `EditorPanel` updates `SidecarData` object
4. `EditorPanel` calls `save_sidecar(sidecar)` from core
5. Core creates `.bak` backup file
6. Core writes new JSON file
7. `EditorPanel` emits `sidecarSaved` signal
8. `MainWindow` updates status bar

## Error Handling

### Core Layer (src/)
- Raise exceptions for unrecoverable errors
- Return `None` for missing/optional data
- Log warnings for non-critical issues

### UI Layer (Qt/)
- Use `QMessageBox` for user-facing errors
- Update status bar for operation feedback
- Graceful degradation when features unavailable

Example:
```python
try:
    sidecar = load_sidecar(image_path)
except FileNotFoundError:
    QMessageBox.warning(self, "Error", "Image file not found")
except json.JSONDecodeError:
    QMessageBox.warning(self, "Error", "Invalid sidecar format")
```

## Image Format Support

Supported formats (case-insensitive):
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)

Defined in: `sidecarCore.DEFAULT_EXTENSIONS`

## Output Image Resolution

The `OutputResolver` class tries multiple strategies to find generated images:

1. **Relative Path**: Same structure from input_root → output_root
2. **Filename Match**: Search output_root for same filename
3. **Stem-Prefix Match**: Match by filename stem (e.g., "image" → "image_001.png")

## Common Tasks

### Adding a New Configuration Option

1. Add getter/setter in `src/sidecarConfig.py`
2. Use `_get_sidecar_section()` and `_save_sidecar_section()`
3. Update this documentation

### Adding a New Widget

1. Create in `Qt/widgets/`
2. Inherit from appropriate Qt class
3. Define custom signals if needed
4. Keep business logic in core modules
5. Update `ARCHITECTURE.md`

### Adding a New Menu Action

1. Add action in `mainWindow._create_menu_bar()`
2. Connect to handler method
3. Implement handler method
4. Update user documentation

## Testing Guidelines

### Core Module Testing
```python
def test_load_sidecar(tmp_path):
    """Test sidecar loading."""
    # Create test file
    image = tmp_path / "test.png"
    image.touch()
    
    sidecar_path = tmp_path / "test.png.prompt.json"
    sidecar_path.write_text('{"prompt": "test"}')
    
    # Test
    result = load_sidecar(str(image))
    assert result.prompt == "test"
```

### UI Widget Testing
```python
def test_editor_panel():
    """Test editor panel widget."""
    from PySide6.QtWidgets import QApplication
    from Qt.widgets.editorPanel import EditorPanel
    
    app = QApplication.instance() or QApplication([])
    panel = EditorPanel()
    
    # Test functionality
    panel.set_sidecar(test_sidecar)
    assert panel.has_unsaved_changes() == False
```

## Resources

### Documentation Files
- **ARCHITECTURE.md** - Detailed architecture and design
- **DEVELOPMENT.md** - Development guide and workflows
- **API.md** - API reference for core modules
- **USER_GUIDE.md** - User-facing documentation
- **README.md** - Quick start and overview

### External Resources
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [Qt Documentation](https://doc.qt.io/)

## Future Enhancements

Planned features (see README.md for full list):
- Batch editing multiple sidecars
- Drag & drop support
- Undo/Redo stack
- Tag editor with autocomplete
- Search/filter functionality
- LLaVA integration
- Custom UI themes
- CLI tool for batch operations

## When Making Changes

### Checklist
- [ ] Core logic has no Qt imports (if touching `src/`)
- [ ] Type hints added to functions
- [ ] Docstrings added to public functions
- [ ] Code follows snake_case naming
- [ ] No hardcoded paths or credentials
- [ ] Error handling appropriate for layer (raise vs dialog)
- [ ] Tests added/updated
- [ ] Documentation updated if needed
- [ ] Manual testing completed

### Code Review Focus
- Separation of concerns maintained
- Signal/slot connections correct
- Error handling appropriate
- Resource cleanup proper
- Configuration persisted correctly

## Common Pitfalls

❌ **Don't**: Import Qt in `src/` modules
✅ **Do**: Keep core logic pure Python

❌ **Don't**: Use hardcoded paths like `/home/user/...`
✅ **Do**: Use configuration management

❌ **Don't**: Catch all exceptions silently
✅ **Do**: Log errors and show user feedback

❌ **Don't**: Forget to create backups before modifying
✅ **Do**: Use `save_sidecar(create_backup=True)`

❌ **Don't**: Block UI thread with long operations
✅ **Do**: Use QThread for long-running tasks (future enhancement)

## Questions?

For detailed information, refer to:
1. `documentation/ARCHITECTURE.md` - System design
2. `documentation/DEVELOPMENT.md` - Development workflows
3. `documentation/API.md` - API reference
4. This file - Project-specific patterns
5. `.github/copilot-instructions.md` - General Qt/Python guidelines
