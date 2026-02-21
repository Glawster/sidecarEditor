from pathlib import Path

import pytest

from Qt.widgets.editorPanel import EditorPanel
from src.sidecarCore import SidecarData


@pytest.fixture
def sidecar(tmp_path: Path) -> SidecarData:
    return SidecarData(imagePath=str(tmp_path / "test.png"))


def test_save_builds_expected_payload(qtbot, sidecar, monkeypatch):
    panel = EditorPanel()
    qtbot.addWidget(panel)

    panel.loadSidecar(sidecar)

    panel._promptText["description"].setPlainText("a person")
    panel._promptText["subject"].setPlainText("blonde hair")
    panel._negGeneralText.setPlainText("lowres")
    panel._txtNotes.setPlainText("note")

    captured = {}

    def _fake_save_sidecar(sidecar_obj, createBackup=True):
        # capture what would be saved
        captured["data"] = getattr(sidecar_obj, "data", None)

    monkeypatch.setattr(panel, "_saveSidecar", _fake_save_sidecar)

    assert panel.saveCurrentSidecar() is True

    data = captured["data"]
    assert isinstance(data, dict)

    # Minimum schema assertions
    assert "positive" in data
    assert "negative" in data
    assert "status" in data
    assert "assembled" in data
    assert "generator" in data

    assert "description" in data["positive"]
    assert "subject" in data["positive"]
    assert "prompt" in data["positive"]["subject"]

    assert "general" in data["negative"]
    assert "style" in data["negative"]

    assert "notes" in data["status"]
    assert "positive" in data["assembled"]
    assert "negative" in data["assembled"]