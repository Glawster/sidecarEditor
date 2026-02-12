#!/usr/bin/env python3
"""
Test script to verify mainWindow.ui and mainWindow.py integration.

This script tests:
1. UI file can be loaded
2. Exit button exists in UI file
3. Exit button can be found by mainWindow.py code pattern
4. All dimensions are rounded to nnn0 or nnnn5
"""

import sys
from pathlib import Path
import xml.etree.ElementTree as ET


def test_ui_file_exists():
    """Test that mainwindow.ui file exists."""
    ui_file = Path('Qt/widgets/mainwindow.ui')
    assert ui_file.exists(), f"UI file not found: {ui_file}"
    print("✓ mainwindow.ui file exists")
    return True


def test_exit_button_in_ui():
    """Test that exit button exists in UI file."""
    tree = ET.parse('Qt/widgets/mainwindow.ui')
    root = tree.getroot()
    
    # Find exit button
    exit_button = None
    for widget in root.iter('widget'):
        if widget.get('name') == 'btnExit':
            exit_button = widget
            break
    
    assert exit_button is not None, "Exit button not found in UI file"
    
    # Verify button text
    text_found = False
    for prop in exit_button.iter('property'):
        if prop.get('name') == 'text':
            text = prop.find('string').text
            assert text == 'Exit', f"Expected 'Exit', got '{text}'"
            text_found = True
            break
    
    assert text_found, "Exit button text not found"
    print("✓ Exit button exists in mainwindow.ui with correct text")
    return True


def test_exit_button_position():
    """Test that exit button is positioned at bottom right."""
    tree = ET.parse('Qt/widgets/mainwindow.ui')
    root = tree.getroot()
    
    # Get window dimensions
    for widget in root.iter('widget'):
        if widget.get('class') == 'QMainWindow':
            for prop in widget.iter('property'):
                if prop.get('name') == 'geometry':
                    rect = prop.find('rect')
                    win_width = int(rect.find('width').text)
                    win_height = int(rect.find('height').text)
                    break
            break
    
    # Get exit button position
    for widget in root.iter('widget'):
        if widget.get('name') == 'btnExit':
            for prop in widget.iter('property'):
                if prop.get('name') == 'geometry':
                    rect = prop.find('rect')
                    x = int(rect.find('x').text)
                    y = int(rect.find('y').text)
                    width = int(rect.find('width').text)
                    height = int(rect.find('height').text)
                    break
            break
    
    # Verify position is bottom right
    right_margin = win_width - (x + width)
    bottom_margin = win_height - (y + height)
    
    assert right_margin < 50, f"Button too far from right edge: {right_margin}px"
    assert bottom_margin < 50, f"Button too far from bottom edge: {bottom_margin}px"
    assert bottom_margin > 0, f"Button below window bottom: {bottom_margin}px"
    
    print(f"✓ Exit button positioned at bottom right ({right_margin}px from right, {bottom_margin}px from bottom)")
    return True


def test_mainwindow_code():
    """Test that mainWindow.py contains exit button code."""
    with open('Qt/widgets/mainWindow.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('btnExit extraction', 'btnExit = loadedCentral.findChild(QPushButton, "btnExit")'),
        ('btnExit verification', 'btnExit,'),
        ('btnExit storage', 'self._btnExit = btnExit'),
        ('btnExit signal connection', 'self._btnExit.clicked.connect(self.close)'),
    ]
    
    for check_name, check_string in checks:
        assert check_string in content, f"{check_name} not found in mainWindow.py"
    
    print("✓ mainWindow.py contains all exit button code")
    return True


def test_dimensions_rounded():
    """Test that all dimensions are rounded to nnn0 or nnnn5."""
    ui_files = sorted(Path('.').rglob('*.ui'))
    
    def check_rounding(value):
        last_digit = value % 10
        return last_digit in [0, 5]
    
    all_rounded = True
    for ui_file in ui_files:
        tree = ET.parse(ui_file)
        root = tree.getroot()
        
        for element_type in ['width', 'height']:
            for elem in root.iter(element_type):
                try:
                    value = int(elem.text)
                    if not check_rounding(value):
                        print(f"✗ {ui_file.name}: {element_type}={value} not rounded")
                        all_rounded = False
                except (ValueError, TypeError):
                    continue
    
    assert all_rounded, "Some dimensions are not properly rounded"
    print(f"✓ All dimensions in {len(ui_files)} .ui files are rounded to nnn0 or nnn5")
    return True


def test_roundui_script_exists():
    """Test that roundUiDimensions.py script exists."""
    script_file = Path('roundUiDimensions.py')
    assert script_file.exists(), f"Script not found: {script_file}"
    
    # Check script is executable (has shebang)
    with open(script_file, 'r') as f:
        first_line = f.readline()
        assert first_line.startswith('#!'), "Script missing shebang"
    
    print("✓ roundUiDimensions.py script exists and has shebang")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing mainWindow.ui and mainWindow.py changes")
    print("=" * 60)
    print()
    
    tests = [
        test_ui_file_exists,
        test_exit_button_in_ui,
        test_exit_button_position,
        test_mainwindow_code,
        test_dimensions_rounded,
        test_roundui_script_exists,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Tests: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
