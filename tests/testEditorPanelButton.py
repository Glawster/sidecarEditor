from pathlib import Path

import pytest

from Qt.widgets.editorPanel import EditorPanel
from src.sidecarCore import SidecarData


@pytest.fixture
def sidecar(tmp_path: Path) -> SidecarData:
    # plausible image path; does not need to exist for button-state tests
    return SidecarData(imagePath=str(tmp_path / "test.png"))


def test_initial_buttons_disabled(qtbot):
    panel = EditorPanel()
    qtbot.addWidget(panel)

    assert panel._saveButton.isEnabled() is False
    assert panel._revertButton.isEnabled() is False
    assert panel.hasUnsavedChanges() is False


def test_load_sidecar_sets_expected_button_state(qtbot, sidecar):
    panel = EditorPanel()
    qtbot.addWidget(panel)

    panel.loadSidecar(sidecar)

    # editor-panel-rework behavior: sidecar loaded but clean => nothing to save/revert
    assert panel._saveButton.isEnabled() is False
    assert panel._revertButton.isEnabled() is False
    assert panel.hasUnsavedChanges() is False


def test_edit_enables_save_and_revert(qtbot, sidecar):
    panel = EditorPanel()
    qtbot.addWidget(panel)

    panel.loadSidecar(sidecar)
    assert panel._saveButton.isEnabled() is False
    assert panel._revertButton.isEnabled() is False

    # Simulate a user edit; QTextEdit.textChanged should fire
    panel._promptText["subject"].setPlainText("changed")

    qtbot.waitUntil(lambda: panel._saveButton.isEnabled() is True)
    qtbot.waitUntil(lambda: panel._revertButton.isEnabled() is True)

    assert panel.hasUnsavedChanges() is True


def test_save_clears_unsaved_changes(qtbot, sidecar, monkeypatch):
    panel = EditorPanel()
    qtbot.addWidget(panel)

    panel.loadSidecar(sidecar)

    panel._promptText["subject"].setPlainText("changed")
    qtbot.waitUntil(lambda: panel.hasUnsavedChanges() is True)

    # Avoid filesystem writes: on editor-panel-rework saveCurrentSidecar calls self._saveSidecar(...)
    monkeypatch.setattr(panel, "_saveSidecar", lambda *args, **kwargs: None)

    assert panel.saveCurrentSidecar() is True

    assert panel.hasUnsavedChanges() is False
    assert panel._saveButton.isEnabled() is False
    assert panel._revertButton.isEnabled() is False