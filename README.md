# Sidecar Editor

A Qt-based desktop application for editing image prompt sidecar files.

![Version](https://img.shields.io/badge/version-0.1.0--MVP-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Qt](https://img.shields.io/badge/Qt-PySide6-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## Overview

Sidecar Editor helps you review and refine image generation prompts stored as JSON files next to your images. Perfect for managing LLaVA-generated captions or Stable Diffusion training data.

### Key Features

✨ **Browse Images** - Thumbnail view of all images in a folder  
📝 **Edit Prompts** - Edit positive and negative prompts  
🔄 **Compare Images** - Toggle between original and generated images  
💾 **Auto-Backup** - Automatic backup before saving  
⚙️ **State Persistence** - Remembers your folders and last position  

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Glawster/sidecarEditor.git
cd sidecarEditor

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m sidecarEditor
```

### Basic Usage

1. **Set Input Folder**: Click "Set Input Folder" and choose your images folder
2. **Browse Images**: Click thumbnails to view and edit
3. **Edit Prompts**: Modify the prompt text in the editor panel
4. **Save**: Click "Save Sidecar" to save your changes

## Documentation

- 📖 **[User Guide](documentation/USER_GUIDE.md)** - Complete usage instructions
- 🏗️ **[Architecture](documentation/ARCHITECTURE.md)** - Technical architecture
- 🔧 **[Development Guide](documentation/DEVELOPMENT.md)** - Contributing guide
- 📚 **[API Reference](documentation/API.md)** - API documentation

## Sidecar File Format

Sidecar files are JSON files stored next to images:

```
my_image.png                    # Your image
my_image.png.prompt.json        # Sidecar file (editable)
my_image.png.prompt.json.bak    # Backup (auto-created)
```

Example sidecar content:
```json
{
  "prompt": "A beautiful sunset over mountains",
  "negative_prompt": "blur, low quality",
  "tags": [],
  "metadata": {}
}
```

## Requirements

- **Python**: 3.10 or higher
- **Qt**: PySide6
- **OS**: Linux, macOS, Windows

## Project Structure

```
sidecarEditor/
├── src/              # Core logic (no Qt dependencies)
├── ui/               # Qt user interface
├── documentation/    # All documentation files
├── __main__.py       # Application entry point
└── requirements.txt  # Dependencies
```

## Features in Detail

### Image Management
- Scans folders for images (PNG, JPEG, GIF, BMP, WebP)
- Thumbnail preview grid
- Fast navigation between images
- Remembers last selected image

### Prompt Editing
- Multi-line text editor for prompts
- Separate negative prompt editor
- Real-time change tracking
- Revert unsaved changes

### Output Comparison
- Set output folder for generated images
- Toggle between original and output
- Multiple resolution strategies
- Gracefully handles missing outputs

### Configuration
- Settings stored in `~/.config/kohya/kohyaConfig.json`
- Window position and size remembered
- Folder paths persisted
- Integrates with existing kohyaConfig ecosystem

## Development

### Architecture Highlights

- **Separation of Concerns**: Core logic is Qt-independent
- **Reusable Core**: Business logic can be used by CLI tools
- **Clean UI Layer**: Qt widgets only in `ui/` directory
- **Type Hints**: Modern Python with type annotations

### Running from Source

```bash
# From repository root
python -m sidecarEditor

# Or with virtual environment
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python -m sidecarEditor
```

### Contributing

See [DEVELOPMENT.md](documentation/DEVELOPMENT.md) for:
- Coding standards
- Adding features
- Testing guidelines
- Pull request process

## Roadmap

Current version: **0.1.0 (MVP)**

### Planned Features

- [ ] **Batch Editing** - Edit multiple sidecars at once
- [ ] **Drag & Drop** - Drag images to reorder
- [ ] **Undo/Redo** - Full undo stack
- [ ] **Tag Editor** - Visual tag management
- [ ] **Search/Filter** - Find images by prompt content
- [ ] **LLaVA Integration** - Direct caption generation
- [ ] **Themes** - Custom UI themes
- [ ] **CLI Tool** - Command-line batch operations

## Screenshots

> *Screenshots coming soon - application just completed!*

## FAQ

**Q: What are sidecar files?**  
A: JSON files stored next to images containing prompt and metadata.

**Q: Can I use this offline?**  
A: Yes! Completely offline, no internet required.

**Q: Does this modify my images?**  
A: No, only creates/edits the `.prompt.json` files.

**Q: Where are backups stored?**  
A: Next to the sidecar as `.prompt.json.bak`.

**Q: Can I edit the JSON directly?**  
A: Yes! They're plain text JSON files.

## Support

- **Issues**: [GitHub Issues](https://github.com/Glawster/sidecarEditor/issues)
- **Documentation**: See `documentation/` folder
- **Email**: Create an issue for support

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [PySide6](https://doc.qt.io/qtforpython-6/)
- Integrates with [kohyaConfig](https://github.com/Glawster/linuxMigration) ecosystem
- Inspired by LLaVA image captioning workflow

---

**Made with ❤️ for the AI image generation community**
