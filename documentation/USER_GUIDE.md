# Sidecar Editor User Guide

Welcome to Sidecar Editor! This guide will help you get started with reviewing and editing image prompt sidecar files.

## What is Sidecar Editor?

Sidecar Editor is a desktop application that helps you:
- Review images in a folder
- Edit prompt text files (sidecars) associated with each image
- Compare original images with generated outputs
- Organize and refine your image generation prompts

## Getting Started

### Installation

1. **Install Python 3.10 or higher** if not already installed
   - Download from [python.org](https://www.python.org/)

2. **Install the application:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python -m sidecarEditor
   ```

### First Launch

When you first launch Sidecar Editor:

1. The main window will open with three panels:
   - **Left**: Thumbnail list (for browsing images)
   - **Top Right**: Image preview
   - **Bottom Right**: Prompt editor

2. You'll see a message: "Welcome! Please set an input folder to get started"

3. Click **"File > Set Input Folder"** or the **"Set Input Folder"** button

4. Select the folder containing your images

## Basic Workflow

### 1. Setting Up Folders

#### Input Folder
The input folder contains your original images.

**To set:**
- Click **File > Set Input Folder** (or press `Ctrl+I`)
- Browse to your images folder
- Click "Select Folder"

The application will scan this folder for images and display thumbnails on the left.

#### Output Folder (Optional)
The output folder contains generated/processed versions of your images.

**To set:**
- Click **File > Set Output Folder** (or press `Ctrl+O`)
- Browse to your outputs folder
- Click "Select Folder"

If set, you can toggle between original and output images.

### 2. Browsing Images

**Thumbnail List (Left Panel):**
- Displays all images found in the input folder
- Shows image thumbnail and filename
- Click any thumbnail to view and edit

**Supported Image Formats:**
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)

### 3. Viewing Images

**Image Preview (Top Right):**
- Displays the selected image
- Shows current image name
- Automatically scales to fit window

**Toggle Button:**
- If an output image is found, use "Show Output" to switch views
- Click "Show Original" to switch back
- If no output is found, button is disabled

### 4. Editing Prompts

**Editor Panel (Bottom Right):**

**Prompt Field:**
- Enter or edit the main image generation prompt
- Supports multi-line text
- This is the primary description for image generation

**Negative Prompt Field:**
- Enter things you want to avoid in the image
- Examples: "blur, low quality, distorted"
- Optional field

**Buttons:**
- **Save Sidecar**: Saves your changes to disk
  - Creates a backup file (`.prompt.json.bak`)
  - Shows confirmation message
- **Revert Changes**: Discards unsaved changes
  - Reloads the original sidecar data
  - Asks for confirmation

### 5. Understanding Sidecar Files

**What is a Sidecar File?**

A sidecar file stores prompt information next to each image:

```
my_image.png                    (your image)
my_image.png.prompt.json        (sidecar file)
my_image.png.prompt.json.bak    (backup)
```

**Sidecar Content:**
```json
{
  "prompt": "A beautiful sunset over mountains",
  "negative_prompt": "blur, low quality",
  "tags": [],
  "metadata": {}
}
```

**Automatic Creation:**
- If an image has no sidecar, one is created in memory
- Empty prompt and negative_prompt fields
- Only saved when you click "Save Sidecar"

**Backup Protection:**
- Each save creates a `.bak` backup
- Protects against accidental data loss
- Previous version is always preserved

## Features in Detail

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+I` | Set Input Folder |
| `Ctrl+O` | Set Output Folder |
| `F5` | Refresh image list |
| `Ctrl+Q` | Quit application |

### Status Bar

The status bar at the bottom shows:
- Current operation status
- Number of images found
- Save confirmations
- Error messages

### Menu Bar

**File Menu:**
- Set Input Folder
- Set Output Folder
- Refresh
- Exit

**Help Menu:**
- About (shows application information)

## Common Tasks

### Task 1: Review and Edit Prompts

1. Set your input folder
2. Click an image thumbnail
3. Review the prompt in the editor
4. Make changes as needed
5. Click "Save Sidecar"
6. Move to next image

### Task 2: Compare Original and Output

1. Set both input and output folders
2. Select an image
3. Click "Show Output" to see the generated version
4. Click "Show Original" to switch back
5. Edit prompt based on comparison
6. Save changes

### Task 3: Batch Review

1. Set input folder with many images
2. Work through thumbnails one by one
3. Application remembers last selected image
4. Your progress is saved between sessions

### Task 4: Organize Prompts

1. Review existing prompts
2. Standardize formatting
3. Add negative prompts where missing
4. Ensure consistency across images

## Tips and Best Practices

### Writing Good Prompts

**Be Specific:**
- ✅ "A red sports car on a mountain road at sunset"
- ❌ "A car"

**Use Descriptive Language:**
- Include style, lighting, mood, composition
- Example: "photorealistic, dramatic lighting, cinematic composition"

**Negative Prompts:**
- List unwanted elements
- Common: "blur, low quality, distorted, artifacts"
- Helps AI avoid common issues

### Organizing Your Workflow

1. **Start with one folder** at a time
2. **Work systematically** through thumbnails
3. **Save frequently** - each save is backed up
4. **Compare outputs** when available
5. **Refine iteratively** - review and improve

### Managing Large Collections

- Application remembers your last position
- Use refresh (F5) after adding new images
- Thumbnails load on-demand for performance
- Configuration persists between sessions

## Troubleshooting

### Problem: No images appear in thumbnail list

**Solutions:**
- Check that input folder contains supported image formats
- Click "File > Refresh" (F5) to rescan
- Ensure folder path is correct in the path display

### Problem: Output images not found

**Solutions:**
- Verify output folder is set correctly
- Check that output images have same or similar filenames
- Application tries multiple resolution strategies

### Problem: Cannot save sidecar

**Solutions:**
- Check folder permissions (must be writable)
- Ensure sufficient disk space
- Close other applications that might lock files

### Problem: Changes not persisting

**Solutions:**
- Click "Save Sidecar" before moving to next image
- Check for error messages in status bar
- Verify sidecar file was created in input folder

### Problem: Application won't start

**Solutions:**
- Ensure Python 3.10+ is installed
- Install dependencies: `pip install -r requirements.txt`
- Try from command line to see error messages
- Check that PySide6 installed correctly

## Configuration

Settings are automatically saved in:
```
~/.config/kohya/kohyaConfig.json
```

This includes:
- Last input folder
- Last output folder
- Window position and size
- Last selected image

**Manual Configuration:**

You can edit this file directly if needed:

```json
{
  "sidecarEditor": {
    "inputRoot": "/path/to/images",
    "outputRoot": "/path/to/outputs",
    "lastSelectedImage": "/path/to/image.png",
    "windowGeometry": {
      "x": 100,
      "y": 100,
      "width": 1200,
      "height": 800
    }
  }
}
```

## Frequently Asked Questions

**Q: What image formats are supported?**
A: PNG, JPEG, GIF, BMP, and WebP.

**Q: Can I edit multiple images at once?**
A: Not in the current version. Batch editing is planned for a future release.

**Q: Where are my changes saved?**
A: Changes are saved as `.prompt.json` files next to each image.

**Q: What if I make a mistake?**
A: Each save creates a `.bak` backup file. You can manually restore from the backup.

**Q: Can I use this on multiple computers?**
A: Yes! Sidecar files travel with your images. Just point each installation to the same folders.

**Q: Does this work offline?**
A: Yes, completely offline. No internet connection required.

**Q: How do I undo changes?**
A: Use the "Revert Changes" button before saving, or manually restore from the `.bak` file.

**Q: Can I delete sidecar files?**
A: Yes, manually delete `.prompt.json` files. The application will create new defaults when you select those images.

**Q: How do I export my prompts?**
A: Sidecar files are plain JSON - you can read/process them with any text editor or script.

## Advanced Usage

### Command Line

Run from different locations:
```bash
# From parent directory
python -m sidecarEditor

# Directly (when in sidecarEditor directory)
python __main__.py
```

### Scripting with Sidecar Files

You can read sidecar files with any JSON tool:

**Python:**
```python
import json

with open('image.png.prompt.json', 'r') as f:
    data = json.load(f)
    print(data['prompt'])
```

**Shell:**
```bash
cat image.png.prompt.json | jq '.prompt'
```

### Integration with Other Tools

Sidecar files are designed to work with:
- LLaVA (image captioning)
- Stable Diffusion training
- Other image generation tools
- Custom processing scripts

## Getting Help

### Resources

- **Documentation**: See `documentation/` folder
  - ARCHITECTURE.md - Technical architecture
  - API.md - API reference
  - DEVELOPMENT.md - Developer guide

- **GitHub**: [https://github.com/Glawster/sidecarEditor](https://github.com/Glawster/sidecarEditor)
  - Report issues
  - Request features
  - View source code

### Support

For bugs or feature requests:
1. Check existing GitHub issues
2. Create a new issue with details
3. Include error messages if applicable

## What's Next?

Planned features for future versions:

- [ ] Drag-and-drop support
- [ ] Batch editing
- [ ] Undo/redo functionality
- [ ] Tag editing with autocomplete
- [ ] Search and filter
- [ ] Custom themes
- [ ] LLaVA integration
- [ ] Prompt templates
- [ ] Export/import presets
- [ ] Keyboard navigation improvements

## Conclusion

Sidecar Editor helps you organize and refine your image prompts efficiently. With practice, you'll develop a workflow that suits your needs.

**Quick Tips to Remember:**
1. Set input folder first
2. Click thumbnails to view/edit
3. Edit prompts in the editor
4. Save your changes
5. Backups are created automatically

Happy editing! 🎨
