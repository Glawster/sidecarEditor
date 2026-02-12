# Sidecar Editor Architecture

## Overview

Sidecar Editor is a Qt (PySide6) desktop application for reviewing and refining image prompt sidecar files. The application follows a clean separation of concerns architecture with strict boundaries between core logic and UI layers.

## Design Principles

### 1. Separation of Concerns

The application is divided into two main layers:

- **Core Logic (`src/`)**: Pure Python business logic with no Qt dependencies
- **UI Layer (`Qt/`)**: Qt-based user interface that consumes the core logic

This separation ensures:
- Core logic can be reused by future CLI or batch tools
- Business logic can be tested independently of UI
- Clear boundaries make the codebase maintainable

### 2. Configuration Management

The application uses the existing `kohyaConfig.py` module from the linuxMigration repository. All editor state is stored under a single configuration key: `"sidecarEditor"`.

### 3. Sidecar Convention

Sidecar files follow these conventions:
- Stored next to the image: `image.png` → `image.png.prompt.json`
- JSON format with prompt, negative_prompt, tags, and metadata fields
- If a sidecar doesn't exist, a minimal default is generated in memory
- Backups are created before saving: `image.png.prompt.json.bak`

### 4. Output Image Resolution

The application attempts to find generated/output images using multiple strategies:
1. Same relative path from input_root to output_root
2. Filename match in output_root
3. Stem-prefix match (e.g., "image" matches "image_001.png")

## Directory Structure

```
sidecarEditor/
├── src/                      # Core logic (no Qt dependencies)
│   ├── __init__.py
│   ├── sidecarCore.py       # Scan, load/save sidecars, assemble prompts
│   ├── outputResolver.py    # Original → output image lookup logic
│   └── sidecarConfig.py     # Configuration wrapper around kohyaConfig
│
├── Qt/                       # UI layer (Qt only)
│   ├── __init__.py
│   ├── mainWindow.py        # QMainWindow with split layout
│   └── widgets/
│       ├── __init__.py
│       ├── thumbnailList.py # Image thumbnail list/grid widget
│       ├── imagePreview.py  # Image preview with original/output toggle
│       └── editorPanel.py   # Sidecar editing panel
│
├── documentation/            # Documentation
│   ├── ARCHITECTURE.md      # This file
│   ├── API.md               # API documentation
│   ├── DEVELOPMENT.md       # Development guide
│   └── USER_GUIDE.md        # User guide
│
├── __main__.py              # Entry point (python -m sidecarEditor)
├── requirements.txt         # Python dependencies
└── README.md                # Quick start guide
```

## Core Components

### sidecarCore.py

**Purpose**: Core sidecar file management functionality

**Key Classes**:
- `SidecarData`: Dataclass representing a prompt sidecar file

**Key Functions**:
- `scan_images(root_path)`: Scan directory for image files
- `load_sidecar(image_path)`: Load sidecar data for an image
- `save_sidecar(sidecar, create_backup)`: Save sidecar to disk
- `get_sidecar_path(image_path)`: Get sidecar file path for an image
- `assemble_prompt(sidecar)`: Assemble full prompt text

**Dependencies**: None (pure Python with standard library)

### outputResolver.py

**Purpose**: Resolve original images to their generated output images

**Key Classes**:
- `OutputResolver`: Manages output image resolution logic

**Resolution Strategies**:
1. Same relative path
2. Filename match
3. Stem-prefix match

**Dependencies**: None (pure Python with standard library)

### sidecarConfig.py

**Purpose**: Configuration management wrapper

**Key Functions**:
- `get_input_root()` / `set_input_root(path)`: Input folder management
- `get_output_root()` / `set_output_root(path)`: Output folder management
- `get_window_geometry()` / `set_window_geometry(...)`: Window state persistence
- `get_last_selected_image()` / `set_last_selected_image(path)`: Selection state

**Dependencies**: Uses kohyaConfig.py pattern (currently placeholder implementation)

## UI Components

### mainWindow.py

**Purpose**: Main application window with split pane layout

**Features**:
- Horizontal splitter: thumbnail list | (preview + editor)
- Menu bar with File and Help menus
- Path display and folder selection
- Status bar for user feedback
- State persistence (window geometry, paths, selection)

**Signals Used**:
- `imageSelected` from ThumbnailList
- `sidecarSaved` from EditorPanel

### ThumbnailList Widget

**Purpose**: Display images as thumbnails in a list/grid

**Features**:
- Icon-based list view
- Thumbnail generation (100x100 pixels)
- Selection handling
- Emits `imageSelected` signal

### ImagePreview Widget

**Purpose**: Display image with original/output toggle

**Features**:
- Image scaling to fit widget
- Toggle button for original ↔ output
- Status label showing current image
- Handles missing output images gracefully

### EditorPanel Widget

**Purpose**: Edit sidecar prompt data

**Features**:
- Prompt text editor
- Negative prompt text editor
- Save button (creates backup)
- Revert button (discard changes)
- Unsaved changes tracking
- Emits `sidecarSaved` signal

## Data Flow

### Loading an Image

```
User selects thumbnail
  ↓
ThumbnailList emits imageSelected(image_path)
  ↓
MainWindow receives signal
  ↓
MainWindow calls load_sidecar(image_path)
  ↓
MainWindow calls OutputResolver.resolve_output()
  ↓
MainWindow updates ImagePreview
  ↓
MainWindow updates EditorPanel
```

### Saving a Sidecar

```
User clicks "Save Sidecar"
  ↓
EditorPanel reads text from editors
  ↓
EditorPanel updates SidecarData object
  ↓
EditorPanel calls save_sidecar() (creates backup)
  ↓
EditorPanel emits sidecarSaved signal
  ↓
MainWindow receives signal and updates status
```

## Configuration Storage

Configuration is stored in `~/.config/kohya/kohyaConfig.json`:

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

## Sidecar File Format

```json
{
  "prompt": "A beautiful sunset over mountains",
  "negative_prompt": "blur, low quality, distorted",
  "tags": ["landscape", "sunset", "mountains"],
  "metadata": {
    "created": "2024-01-01T12:00:00Z",
    "modified": "2024-01-02T14:30:00Z"
  }
}
```

## Future Enhancements

The current implementation is an MVP. Planned enhancements include:

1. **Drag-and-Drop**: Drag images to reorder or move
2. **Batch Editing**: Edit multiple sidecars at once
3. **Undo/Redo Stack**: Full undo/redo support
4. **Prompt Packs**: Template-based prompt management
5. **LLaVA Integration**: Direct LLaVA API calls for generation
6. **Custom Styling**: Theme support and custom styling
7. **Tag Editor**: Visual tag editing with autocomplete
8. **Search/Filter**: Search and filter images by prompt content

## Testing Strategy

### Core Logic Testing

Core logic is testable without Qt:
- Unit tests for `sidecarCore` functions
- Unit tests for `OutputResolver` class
- Integration tests for configuration management

### UI Testing

UI testing requires Qt environment:
- Widget unit tests with QTest
- Integration tests for signal/slot connections
- Manual testing for visual aspects

## Error Handling

### Core Layer

- Raises exceptions for unrecoverable errors
- Returns None or empty collections for missing data
- Prints warnings for non-critical issues

### UI Layer

- QMessageBox for user-facing errors
- Status bar messages for operation feedback
- Graceful degradation when features unavailable

## Performance Considerations

### Thumbnail Generation

- Thumbnails generated on-demand
- Could be cached in future versions
- Image loading is synchronous (could use threads)

### File Scanning

- `scan_images()` is synchronous
- Large directories may cause UI freeze
- Future: Use QThread for background scanning

### Configuration I/O

- Configuration written on every change
- Could batch writes in future versions
- No observable performance impact for typical usage

## Security Considerations

1. **File System Access**: Application only accesses user-selected directories
2. **Configuration Storage**: Plain text JSON (no sensitive data expected)
3. **Input Validation**: Paths validated before file operations
4. **Backup Creation**: Original files preserved before modification

## Compatibility

- **Python**: 3.10+
- **Qt**: PySide6 (Qt 6)
- **Operating Systems**: Linux, macOS, Windows
- **Image Formats**: PNG, JPG, JPEG, GIF, BMP, WEBP

## Dependencies

### Required

- `PySide6`: Qt 6 bindings for Python
- `Pillow`: Image processing library

### Optional

- `python-dateutil`: Date/time handling (future use)
- `watchdog`: File system watching (future use)

## Module Dependencies Graph

```
__main__.py
  └── ui.mainWindow
      ├── ui.widgets.thumbnailList
      ├── ui.widgets.imagePreview
      ├── ui.widgets.editorPanel
      │   └── src.sidecarCore
      ├── src.sidecarCore
      ├── src.outputResolver
      └── src.sidecarConfig
```

Note: No circular dependencies exist. Core modules have no UI dependencies.
