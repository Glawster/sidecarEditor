#!/usr/bin/env python3
"""
Standalone script to round width and height values in Qt .ui files.

This script parses all .ui files in the repository and rounds width and height
values to the nearest nnn0 or nnnn5 (e.g., 1200, 805, 600, 355).

Rounding rules:
- Values ending in 0-2: round down to nnn0
- Values ending in 3-7: round to nnn5
- Values ending in 8-9: round up to next nnn0

Examples:
- 1198 -> 1200
- 803 -> 805
- 607 -> 605
- 352 -> 350
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import sys


def round_to_nearest_5_or_0(value: int) -> int:
    """
    Round value to nearest nnn0 or nnn5.
    
    Args:
        value: Integer value to round
        
    Returns:
        Rounded integer value
    """
    last_digit = value % 10
    
    if last_digit in [0, 1, 2]:
        # Round down to nnn0
        return (value // 10) * 10
    elif last_digit in [3, 4, 5, 6, 7]:
        # Round to nnn5
        return (value // 10) * 10 + 5
    else:  # 8, 9
        # Round up to next nnn0
        return ((value // 10) + 1) * 10


def process_ui_file(file_path: Path) -> tuple[int, int]:
    """
    Process a single .ui file and round all width/height values.
    
    Args:
        file_path: Path to the .ui file
        
    Returns:
        Tuple of (number of changes made, total elements checked)
    """
    try:
        # Parse XML with explicit encoding
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        changes_made = 0
        elements_checked = 0
        
        # Find all <width> and <height> elements
        for element_type in ['width', 'height']:
            for elem in root.iter(element_type):
                elements_checked += 1
                try:
                    original_value = int(elem.text)
                    rounded_value = round_to_nearest_5_or_0(original_value)
                    
                    if original_value != rounded_value:
                        print(f"  {file_path.name}: {element_type} {original_value} -> {rounded_value}")
                        elem.text = str(rounded_value)
                        changes_made += 1
                except (ValueError, TypeError):
                    # Skip non-integer values
                    continue
        
        # Save the file if changes were made
        if changes_made > 0:
            # Write with proper XML formatting
            tree.write(file_path, encoding='UTF-8', xml_declaration=True)
            
            # Add newline at end of file (Qt Designer convention)
            with open(file_path, 'a', encoding='utf-8') as f:
                if not file_path.read_text(encoding='utf-8').endswith('\n'):
                    f.write('\n')
        
        return changes_made, elements_checked
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0, 0


def find_ui_files(root_dir: Path) -> list[Path]:
    """
    Find all .ui files in the repository.
    
    Args:
        root_dir: Root directory to search from
        
    Returns:
        List of paths to .ui files
    """
    return sorted(root_dir.rglob("*.ui"))


def main():
    """Main function to process all .ui files."""
    # Get script directory
    script_dir = Path(__file__).parent
    
    print("=" * 60)
    print("Qt UI Dimension Rounder")
    print("=" * 60)
    print(f"Searching for .ui files in: {script_dir}")
    print()
    
    # Find all .ui files
    ui_files = find_ui_files(script_dir)
    
    if not ui_files:
        print("No .ui files found!")
        return 1
    
    print(f"Found {len(ui_files)} .ui file(s):")
    for ui_file in ui_files:
        print(f"  - {ui_file.relative_to(script_dir)}")
    print()
    
    # Process each file
    total_changes = 0
    total_elements = 0
    
    for ui_file in ui_files:
        changes, elements = process_ui_file(ui_file)
        total_changes += changes
        total_elements += elements
    
    print()
    print("=" * 60)
    print("Summary:")
    print(f"  Files processed: {len(ui_files)}")
    print(f"  Elements checked: {total_elements}")
    print(f"  Changes made: {total_changes}")
    print("=" * 60)
    
    if total_changes > 0:
        print("\n✓ UI files have been updated with rounded dimensions.")
    else:
        print("\n✓ All dimensions were already rounded correctly.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
