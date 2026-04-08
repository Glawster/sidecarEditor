#!/usr/bin/env python3
"""
Test script to verify the Generate button and ComfyUI/RunPod integration.

This script tests:
1. btnGenerate exists in editorPanel.ui
2. btnSetRunpodId and txtRunpodPodId exist in mainwindow.ui
3. editorPanel.py has generateStarted signal and _onGenerate wired
4. mainWindow.py has RunPod helper methods and signal connection
5. sidecarConfig.py has generate-related config functions
"""

import sys
from pathlib import Path
import xml.etree.ElementTree as ET


def test_generate_button_in_editor_ui():
    """Test that btnGenerate exists in editorPanel.ui."""
    ui_file = Path('Qt/widgets/editorPanel.ui')
    assert ui_file.exists(), f"UI file not found: {ui_file}"

    tree = ET.parse(ui_file)
    root = tree.getroot()

    btn = None
    for widget in root.iter('widget'):
        if widget.get('name') == 'btnGenerate':
            btn = widget
            break

    assert btn is not None, "btnGenerate not found in editorPanel.ui"

    text_found = False
    for prop in btn.iter('property'):
        if prop.get('name') == 'text':
            text_found = True
            break

    assert text_found, "btnGenerate text property not found"
    print("✓ btnGenerate exists in editorPanel.ui")
    return True


def test_runpod_widgets_in_mainwindow_ui():
    """Test that RunPod Pod ID label, field and button exist in mainwindow.ui."""
    ui_file = Path('Qt/widgets/mainwindow.ui')
    assert ui_file.exists(), f"UI file not found: {ui_file}"

    tree = ET.parse(ui_file)
    root = tree.getroot()

    widget_names = {w.get('name') for w in root.iter('widget')}

    assert 'txtRunpodPodId' in widget_names, "txtRunpodPodId not found in mainwindow.ui"
    assert 'btnSetRunpodId' in widget_names, "btnSetRunpodId not found in mainwindow.ui"
    assert 'lblRunpodPodId' in widget_names, "lblRunpodPodId not found in mainwindow.ui"

    # The field should be read-only
    read_only_found = False
    for widget in root.iter('widget'):
        if widget.get('name') == 'txtRunpodPodId':
            for prop in widget.iter('property'):
                if prop.get('name') == 'readOnly':
                    val = prop.find('bool')
                    if val is not None and val.text == 'true':
                        read_only_found = True
            break

    assert read_only_found, "txtRunpodPodId is not marked readOnly"
    print("✓ RunPod widgets (label, field, button) exist in mainwindow.ui with correct properties")
    return True


def test_editor_panel_generate_code():
    """Test that editorPanel.py has generateStarted signal and _onGenerate wired."""
    with open('Qt/widgets/editorPanel.py', 'r') as f:
        content = f.read()

    checks = [
        ('generateStarted signal', 'generateStarted = Signal(str)'),
        ('_onGenerate method', 'def _onGenerate(self):'),
        ('generate button connection', 'self._generateButton.clicked.connect(self._onGenerate)'),
        ('subprocess import', 'import subprocess'),
        ('getTxt2ImgScriptPath call', 'sidecarConfig.getTxt2ImgScriptPath()'),
        ('getRunpodPodId call', 'sidecarConfig.getRunpodPodId()'),
        ('--remote flag', '"--remote", runpodPodId'),
        ('--local flag', '"--local", comfyUrl'),
        ('generateStarted emit', 'self.generateStarted.emit('),
    ]

    for check_name, check_string in checks:
        assert check_string in content, f"{check_name} not found in editorPanel.py"

    print("✓ editorPanel.py has all Generate button integration code")
    return True


def test_main_window_runpod_code():
    """Test that mainWindow.py has RunPod Pod ID wiring."""
    with open('Qt/widgets/mainWindow.py', 'r') as f:
        content = f.read()

    checks = [
        ('btnSetRunpodId lookup', 'findChild(QPushButton, "btnSetRunpodId")'),
        ('txtRunpodPodId lookup', 'findChild(QLineEdit, "txtRunpodPodId")'),
        ('btnSetRunpodId connect', 'self._btnSetRunpodId.clicked.connect(self._onSetRunpodId)'),
        ('_onSetRunpodId method', 'def _onSetRunpodId(self):'),
        ('_setRunpodPodId method', 'def _setRunpodPodId(self, podId: str):'),
        ('getRunpodPodId restore', 'sidecarConfig.getRunpodPodId()'),
        ('generateStarted connect', 'self._editorPanel.generateStarted.connect(self._onGenerateStarted)'),
        ('_onGenerateStarted method', 'def _onGenerateStarted(self, message: str):'),
        ('QInputDialog import', 'QInputDialog'),
    ]

    for check_name, check_string in checks:
        assert check_string in content, f"{check_name} not found in mainWindow.py"

    print("✓ mainWindow.py has all RunPod Pod ID integration code")
    return True


def test_sidecar_config_generate_functions():
    """Test that sidecarConfig.py has all generate-related config functions."""
    with open('src/sidecarConfig.py', 'r') as f:
        content = f.read()

    checks = [
        ('getRunpodPodId', 'def getRunpodPodId()'),
        ('setRunpodPodId', 'def setRunpodPodId(podId: str):'),
        ('getTxt2ImgScriptPath', 'def getTxt2ImgScriptPath()'),
        ('setTxt2ImgScriptPath', 'def setTxt2ImgScriptPath(path: str):'),
        ('getComfyUrl', 'def getComfyUrl()'),
        ('setComfyUrl', 'def setComfyUrl(url: str):'),
        ('runpodPodId key', '"runpodPodId"'),
        ('txt2ImgScriptPath key', '"txt2ImgScriptPath"'),
    ]

    for check_name, check_string in checks:
        assert check_string in content, f"{check_name} not found in sidecarConfig.py"

    print("✓ sidecarConfig.py has all generate-related config functions")
    return True


def test_runpod_config_fallback():
    """Test that getRunpodPodId checks both sidecarEditor section and global key."""
    with open('src/sidecarConfig.py', 'r') as f:
        content = f.read()

    # Should read from sidecarEditor.runpodPodId AND fall back to global runpodPodId
    assert 'sidecar.get("runpodPodId")' in content or "sidecar.get('runpodPodId')" in content, \
        "getRunpodPodId does not read from sidecarEditor section (local var 'sidecar' = config['sidecarEditor'])"
    assert 'config.get("runpodPodId")' in content or "config.get('runpodPodId')" in content, \
        "getRunpodPodId does not fall back to global runpodPodId key"

    print("✓ getRunpodPodId checks sidecarEditor section with global fallback")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Generate button and ComfyUI/RunPod integration")
    print("=" * 60)
    print()

    tests = [
        test_generate_button_in_editor_ui,
        test_runpod_widgets_in_mainwindow_ui,
        test_editor_panel_generate_code,
        test_main_window_runpod_code,
        test_sidecar_config_generate_functions,
        test_runpod_config_fallback,
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
