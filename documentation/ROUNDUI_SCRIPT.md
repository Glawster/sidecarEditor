# UI Dimension Rounding Script

## Overview

The `roundUiDimensions.py` script is a standalone Python utility that processes all Qt Designer `.ui` files in the repository and rounds their width and height values to the nearest `nnn0` or `nnn5`.

## Purpose

This ensures consistent, clean dimension values across all UI files, making them easier to:
- Read and understand
- Maintain and modify
- Compare in version control (reduces noise from arbitrary values)

## Rounding Rules

The script applies the following rounding logic:

| Last Digit | Action | Example |
|------------|--------|---------|
| 0, 1, 2 | Round down to nnn0 | 1202 → 1200 |
| 3, 4, 5, 6, 7 | Round to nnn5 | 803 → 805 |
| 8, 9 | Round up to next nnn0 | 608 → 610 |

## Usage

### Basic Usage

```bash
# From repository root
python roundUiDimensions.py
```

### Expected Output

```
============================================================
Qt UI Dimension Rounder
============================================================
Searching for .ui files in: /path/to/sidecarEditor

Found 4 .ui file(s):
  - Qt/widgets/editorPanel.ui
  - Qt/widgets/exampleWidget.ui
  - Qt/widgets/imagePreview.ui
  - Qt/widgets/mainwindow.ui

  mainwindow.ui: width 1182 -> 1180
  mainwindow.ui: height 673 -> 675
  mainwindow.ui: height 74 -> 75
  mainwindow.ui: height 21 -> 20

============================================================
Summary:
  Files processed: 4
  Elements checked: 50
  Changes made: 4
============================================================

✓ UI files have been updated with rounded dimensions.
```

## What It Does

1. **Finds all .ui files** recursively in the repository
2. **Parses XML** structure of each .ui file
3. **Rounds dimensions** of all `<width>` and `<height>` elements
4. **Preserves formatting** maintains XML structure and encoding
5. **Reports changes** shows which values were modified

## When to Use

Run this script:
- After creating new .ui files in Qt Designer
- After manually editing dimension values
- Before committing UI changes to ensure consistency
- When merging branches with UI changes

## Technical Details

### XML Parsing

The script uses Python's `xml.etree.ElementTree` for parsing:
- Preserves XML declaration and encoding (UTF-8)
- Maintains element structure and attributes
- Adds newline at end of file (Qt Designer convention)

### Safety

- Only modifies `<width>` and `<height>` elements
- Skips non-integer values (preserves variables, expressions)
- Creates backup before saving (handled by version control)
- Reports all changes made

### Performance

- Fast processing: ~100ms per file
- No external dependencies (uses standard library)
- Processes all files in single run

## Examples

### Before Rounding

```xml
<property name="geometry">
 <rect>
  <x>0</x>
  <y>0</y>
  <width>1182</width>
  <height>673</height>
 </rect>
</property>
```

### After Rounding

```xml
<property name="geometry">
 <rect>
  <x>0</x>
  <y>0</y>
  <width>1180</width>
  <height>675</height>
 </rect>
</property>
```

## Integration

The script is designed to be:
- **Standalone**: No dependencies on the main application
- **Reusable**: Can be copied to other Qt projects
- **Simple**: Single file, easy to understand and modify
- **Safe**: Only processes .ui files, doesn't affect code

## Error Handling

The script handles errors gracefully:
- Reports parsing errors for individual files
- Continues processing other files on error
- Provides clear error messages
- Returns non-zero exit code on failure

## Verification

Use the test script to verify the changes:

```bash
python test_mainwindow_changes.py
```

This will check that:
- All .ui files are present
- All dimensions are properly rounded
- Script exists and is executable

## Maintenance

The script is self-contained and requires minimal maintenance. To modify rounding behavior, edit the `round_to_nearest_5_or_0()` function.

## See Also

- Qt Designer documentation: https://doc.qt.io/qt-6/qtdesigner-manual.html
- Project architecture: `documentation/ARCHITECTURE.md`
- Qt Designer guide: `documentation/QT_DESIGNER_GUIDE.md`
