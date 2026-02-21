#!/usr/bin/env python3
"""
Test script to verify mainwindow.ui and mainWindow.py integration.

Updated for editor-panel-rework branch:
- mainwindow.ui no longer uses a btnExit button
- exit is provided via menu action "actionExit" and bottom button bar (OK/Cancel)
- verifies required placeholder widgets and top-bar controls exist
- verifies required QAction objects exist
- verifies .ui dimension rounding policy
"""

import sys
from pathlib import Path
import xml.etree.ElementTree as ET


UI_PATH = Path("Qt/widgets/mainwindow.ui")
MAINWINDOW_PY = Path("Qt/widgets/mainWindow.py")


def _parse_ui():
    assert UI_PATH.exists(), f"UI file not found: {UI_PATH}"
    tree = ET.parse(str(UI_PATH))
    return tree.getroot()


def _find_widget_by_name(root, name: str):
    for widget in root.iter("widget"):
        if widget.get("name") == name:
            return widget
    return None


def _find_action_by_name(root, name: str):
    # In .ui files, actions are represented as <action name="actionExit">...</action>
    for action in root.iter("action"):
        if action.get("name") == name:
            return action
    return None


def test_ui_file_exists():
    """Test that mainwindow.ui file exists."""
    assert UI_PATH.exists(), f"UI file not found: {UI_PATH}"
    print("✓ mainwindow.ui file exists")
    return True


def test_required_placeholders_exist_in_ui():
    """Verify widgets that MainWindow._setupUi expects exist in the UI."""
    root = _parse_ui()

    required_widgets = [
        "wgtTopBar",
        "wgtMainContent",
        "btnSetInput",
        "btnSetOutput",
        "txtInputFolder",
        "txtOutputFolder",
    ]

    missing = [name for name in required_widgets if _find_widget_by_name(root, name) is None]
    assert not missing, f"Missing widgets in mainwindow.ui: {', '.join(missing)}"

    print("✓ Required placeholder widgets and top-bar controls exist in mainwindow.ui")
    return True


def test_required_actions_exist_in_ui():
    """Verify QAction objects that MainWindow._setupUi looks up exist in the UI."""
    root = _parse_ui()

    required_actions = [
        "actionSetInput",
        "actionSetOutput",
        "actionRefresh",
        "actionExit",
        "actionAbout",
    ]

    missing = [name for name in required_actions if _find_action_by_name(root, name) is None]
    assert not missing, f"Missing actions in mainwindow.ui: {', '.join(missing)}"

    print("✓ Required actions exist in mainwindow.ui")
    return True


def test_mainwindow_code_patterns():
    """
    Verify mainWindow.py contains key patterns that tie to mainwindow.ui.
    This is intentionally looser than exact-string matching, so refactors don't break tests.
    """
    assert MAINWINDOW_PY.exists(), f"File not found: {MAINWINDOW_PY}"
    content = MAINWINDOW_PY.read_text(encoding="utf-8")

    checks = [
        # UI file name
        ('loads mainwindow.ui', 'Path(__file__).parent / "mainwindow.ui"'),
        # placeholder widgets
        ('finds wgtTopBar', 'findChild(QWidget, "wgtTopBar")'),
        ('finds wgtMainContent', 'findChild(QWidget, "wgtMainContent")'),
        # topbar controls
        ('finds btnSetInput', 'findChild(QPushButton, "btnSetInput")'),
        ('finds btnSetOutput', 'findChild(QPushButton, "btnSetOutput")'),
        ('finds txtInputFolder', 'findChild(QLineEdit, "txtInputFolder")'),
        ('finds txtOutputFolder', 'findChild(QLineEdit, "txtOutputFolder")'),
        # actions
        ('finds actionExit', 'findChild(QAction, "actionExit")'),
        # exit is wired through actionExit
        ('connects actionExit', 'self._actionExit.triggered.connect(self.close)'),
    ]

    for check_name, check_string in checks:
        assert check_string in content, f"{check_name} not found in mainWindow.py"

    print("✓ mainWindow.py contains required UI wiring patterns")
    return True


def test_dimensions_rounded():
    """Test that all dimensions are rounded to nnn0 or nnnn5."""
    ui_files = sorted(Path(".").rglob("*.ui"))

    def check_rounding(value):
        last_digit = value % 10
        return last_digit in [0, 5]

    all_rounded = True
    for ui_file in ui_files:
        tree = ET.parse(ui_file)
        root = tree.getroot()

        for element_type in ["width", "height"]:
            for elem in root.iter(element_type):
                try:
                    value = int(elem.text)
                    if not check_rounding(value):
                        print(f"✗ {ui_file.name}: {element_type}={value} not rounded")
                        all_rounded = False
                except (ValueError, TypeError):
                    continue

    assert all_rounded, "Some dimensions are not properly rounded"
    print(f"✓ All dimensions in {len(ui_files)} .ui files are rounded to nnn0 or nnnn5")
    return True


def test_roundui_script_exists():
    """Test that roundUiDimensions.py script exists."""
    script_file = Path("roundUiDimensions.py")
    assert script_file.exists(), f"Script not found: {script_file}"

    with open(script_file, "r", encoding="utf-8") as f:
        first_line = f.readline()
        assert first_line.startswith("#!"), "Script missing shebang"

    print("✓ roundUiDimensions.py script exists and has shebang")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing mainwindow.ui and mainWindow.py integration")
    print("=" * 60)
    print()

    tests = [
        test_ui_file_exists,
        test_required_placeholders_exist_in_ui,
        test_required_actions_exist_in_ui,
        test_mainwindow_code_patterns,
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