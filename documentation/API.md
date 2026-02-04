# Sidecar Editor API Documentation

## Core API (src/)

### sidecarCore.py

#### SidecarData

Dataclass representing a prompt sidecar file.

```python
@dataclass
class SidecarData:
    image_path: str
    prompt: str = ""
    negative_prompt: str = ""
    tags: List[str] = None
    metadata: Dict[str, Any] = None
```

**Methods:**

- `to_dict() -> Dict[str, Any]`: Convert to dictionary for JSON serialization
- `from_dict(image_path: str, data: Dict[str, Any]) -> SidecarData`: Create from dictionary

**Example:**

```python
from src.sidecarCore import SidecarData

sidecar = SidecarData(
    image_path="/path/to/image.png",
    prompt="A beautiful sunset",
    negative_prompt="blur, low quality",
    tags=["landscape", "sunset"]
)

# Convert to dict for saving
data = sidecar.to_dict()

# Create from dict
sidecar2 = SidecarData.from_dict("/path/to/image.png", data)
```

#### get_sidecar_path

Get the sidecar file path for an image.

```python
def get_sidecar_path(image_path: str) -> Path
```

**Parameters:**
- `image_path`: Path to the image file

**Returns:**
- Path object pointing to the sidecar file

**Example:**

```python
from src.sidecarCore import get_sidecar_path

sidecar_path = get_sidecar_path("/path/to/image.png")
# Returns: Path("/path/to/image.png.prompt.json")
```

#### load_sidecar

Load sidecar data for an image. If the sidecar doesn't exist, returns a minimal default.

```python
def load_sidecar(image_path: str) -> SidecarData
```

**Parameters:**
- `image_path`: Path to the image file

**Returns:**
- SidecarData object

**Example:**

```python
from src.sidecarCore import load_sidecar

sidecar = load_sidecar("/path/to/image.png")
print(f"Prompt: {sidecar.prompt}")
```

#### save_sidecar

Save sidecar data to disk.

```python
def save_sidecar(sidecar: SidecarData, create_backup: bool = True)
```

**Parameters:**
- `sidecar`: SidecarData to save
- `create_backup`: If True, create .bak backup before saving

**Raises:**
- `IOError`: If file cannot be written

**Example:**

```python
from src.sidecarCore import SidecarData, save_sidecar

sidecar = SidecarData(
    image_path="/path/to/image.png",
    prompt="Updated prompt"
)
save_sidecar(sidecar, create_backup=True)
```

#### scan_images

Scan a directory for image files.

```python
def scan_images(root_path: str, extensions: Optional[List[str]] = None) -> List[str]
```

**Parameters:**
- `root_path`: Root directory to scan
- `extensions`: List of file extensions to include (default: common image formats)

**Returns:**
- List of absolute image file paths (sorted)

**Default Extensions:**
`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`

**Example:**

```python
from src.sidecarCore import scan_images

images = scan_images("/path/to/images")
print(f"Found {len(images)} images")

# Custom extensions
png_images = scan_images("/path/to/images", extensions=['.png'])
```

#### assemble_prompt

Assemble the full prompt text from sidecar data.

```python
def assemble_prompt(sidecar: SidecarData) -> str
```

**Parameters:**
- `sidecar`: SidecarData object

**Returns:**
- Assembled prompt string

**Example:**

```python
from src.sidecarCore import SidecarData, assemble_prompt

sidecar = SidecarData(
    image_path="/path/to/image.png",
    prompt="A sunset",
    tags=["landscape", "sunset"]
)

full_prompt = assemble_prompt(sidecar)
# Returns: "A sunset\n\nTags: landscape, sunset"
```

---

### outputResolver.py

#### OutputResolver

Class for resolving original images to their generated output images.

```python
class OutputResolver:
    def __init__(self, output_root: Optional[str] = None)
```

**Parameters:**
- `output_root`: Root directory where output images are stored

**Methods:**

##### set_output_root

Set or update the output root directory.

```python
def set_output_root(self, output_root: str)
```

**Example:**

```python
from src.outputResolver import OutputResolver

resolver = OutputResolver()
resolver.set_output_root("/path/to/outputs")
```

##### resolve_output

Attempt to find the output image for an original image.

```python
def resolve_output(
    self, 
    original_path: str, 
    input_root: Optional[str] = None
) -> Optional[str]
```

**Resolution Strategy:**
1. Try same relative path from input_root to output_root
2. Try filename match in output_root
3. Try stem-prefix match (e.g., "image" matches "image_001.png")

**Parameters:**
- `original_path`: Path to the original image
- `input_root`: Root directory of input images (for relative path calculation)

**Returns:**
- Path to output image if found, None otherwise

**Example:**

```python
from src.outputResolver import OutputResolver

resolver = OutputResolver("/path/to/outputs")
output = resolver.resolve_output(
    "/path/to/inputs/image.png",
    "/path/to/inputs"
)
if output:
    print(f"Found output: {output}")
else:
    print("No output found")
```

##### get_possible_outputs

Get all possible output images for an original image.

```python
def get_possible_outputs(
    self,
    original_path: str,
    input_root: Optional[str] = None
) -> List[str]
```

**Parameters:**
- `original_path`: Path to the original image
- `input_root`: Root directory of input images

**Returns:**
- List of possible output image paths (sorted)

**Example:**

```python
from src.outputResolver import OutputResolver

resolver = OutputResolver("/path/to/outputs")
candidates = resolver.get_possible_outputs(
    "/path/to/inputs/image.png",
    "/path/to/inputs"
)
print(f"Found {len(candidates)} candidates")
for path in candidates:
    print(f"  - {path}")
```

---

### sidecarConfig.py

Configuration management wrapper around kohyaConfig.py.

#### get_input_root / set_input_root

```python
def get_input_root() -> Optional[str]
def set_input_root(path: str)
```

Get or set the last-used input root directory.

**Example:**

```python
from src.sidecarConfig import get_input_root, set_input_root

set_input_root("/path/to/images")
path = get_input_root()
```

#### get_output_root / set_output_root

```python
def get_output_root() -> Optional[str]
def set_output_root(path: str)
```

Get or set the last-used output root directory.

#### get_window_geometry / set_window_geometry

```python
def get_window_geometry() -> Optional[dict]
def set_window_geometry(x: int, y: int, width: int, height: int)
```

Get or set the saved window geometry.

**Example:**

```python
from src.sidecarConfig import set_window_geometry, get_window_geometry

set_window_geometry(100, 100, 1200, 800)
geometry = get_window_geometry()
# Returns: {'x': 100, 'y': 100, 'width': 1200, 'height': 800}
```

#### get_last_selected_image / set_last_selected_image

```python
def get_last_selected_image() -> Optional[str]
def set_last_selected_image(path: str)
```

Get or set the last selected image path.

#### get_all_settings / set_all_settings

```python
def get_all_settings() -> dict
def set_all_settings(settings: dict)
```

Get or set all sidecar editor settings at once.

---

## UI API (ui/)

### mainWindow.py

#### MainWindow

Main application window.

```python
class MainWindow(QMainWindow):
    def __init__(self)
```

**Key Methods:**

- `_on_set_input_folder()`: Handle set input folder action
- `_on_set_output_folder()`: Handle set output folder action
- `_on_refresh()`: Refresh image list
- `_on_image_selected(image_path: str)`: Handle image selection
- `_on_sidecar_saved(image_path: str)`: Handle sidecar saved event

**Signals:**
- Uses signals from child widgets (ThumbnailList, EditorPanel)

---

### widgets/thumbnailList.py

#### ThumbnailList

List widget that displays image thumbnails.

```python
class ThumbnailList(QListWidget):
    imageSelected = Signal(str)  # Emitted when image is selected
    
    def __init__(self, parent=None)
```

**Key Methods:**

- `load_images(image_paths: List[str])`: Load images into the thumbnail list
- `get_selected_image() -> Optional[str]`: Get currently selected image path
- `select_image(image_path: str)`: Select an image by path

**Signals:**
- `imageSelected(str)`: Emitted when an image is selected

**Example:**

```python
from ui.widgets.thumbnailList import ThumbnailList

thumbnail_list = ThumbnailList()
thumbnail_list.imageSelected.connect(lambda path: print(f"Selected: {path}"))
thumbnail_list.load_images(["/path/to/image1.png", "/path/to/image2.png"])
```

---

### widgets/imagePreview.py

#### ImagePreview

Widget for displaying image preview with original/output toggle.

```python
class ImagePreview(QWidget):
    def __init__(self, parent=None)
```

**Key Methods:**

- `set_images(original_path: str, output_path: Optional[str] = None)`: Set images to display
- `clear()`: Clear the displayed image

**Example:**

```python
from ui.widgets.imagePreview import ImagePreview

preview = ImagePreview()
preview.set_images("/path/to/original.png", "/path/to/output.png")
```

---

### widgets/editorPanel.py

#### EditorPanel

Widget for editing sidecar prompt data.

```python
class EditorPanel(QWidget):
    sidecarSaved = Signal(str)  # Emitted when sidecar is saved
    
    def __init__(self, parent=None)
```

**Key Methods:**

- `load_sidecar(sidecar: SidecarData)`: Load sidecar data into the editor
- `clear()`: Clear the editor
- `has_unsaved_changes() -> bool`: Check if there are unsaved changes

**Signals:**
- `sidecarSaved(str)`: Emitted when sidecar is saved (with image_path)

**Example:**

```python
from ui.widgets.editorPanel import EditorPanel
from src.sidecarCore import SidecarData

editor = EditorPanel()
editor.sidecarSaved.connect(lambda path: print(f"Saved: {path}"))

sidecar = SidecarData(image_path="/path/to/image.png", prompt="Test")
editor.load_sidecar(sidecar)
```

---

## Entry Point

### __main__.py

```python
def main()
```

Entry point for the application. Run with:

```bash
python -m sidecarEditor
```

---

## Error Handling

### Core Layer Exceptions

- `IOError`: File I/O errors (cannot read/write files)
- `json.JSONDecodeError`: Invalid JSON in sidecar files
- `ValueError`: Invalid data or configuration

### UI Layer Error Handling

- `QMessageBox.critical()`: Unrecoverable errors
- `QMessageBox.warning()`: Recoverable warnings
- `QMessageBox.information()`: Success messages
- Status bar messages for operation feedback

---

## Configuration File Format

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

Sidecar files use the `.prompt.json` extension:

```json
{
  "prompt": "A beautiful sunset over mountains",
  "negative_prompt": "blur, low quality, distorted",
  "tags": ["landscape", "sunset", "mountains"],
  "metadata": {
    "key": "value"
  }
}
```

**Fields:**
- `prompt` (string): Main generation prompt
- `negative_prompt` (string): Negative/exclusion prompt
- `tags` (array): List of tags
- `metadata` (object): Additional metadata
