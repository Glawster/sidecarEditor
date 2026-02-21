from pathlib import Path

import pytest

from Qt.widgets.editorPanel import EditorPanel
from src.sidecarCore import SidecarData


@pytest.fixture
def sidecar(tmp_path: Path) -> SidecarData:
    return SidecarData(imagePath=str(tmp_path / "test.png"))


def test_revert_restores_baseline(qtbot, sidecar):
    panel = EditorPanel()
    qtbot.addWidget(panel)

    panel.loadSidecar(sidecar)

    baseline = panel._promptText["subject"].toPlainText()
    panel._promptText["subject"].setPlainText("changed")
    qtbot.waitUntil(lambda: panel._revertButton.isEnabled() is True)

    panel._onRevert()

    assert panel._promptText["subject"].toPlainText() == (panel._rawText["subject"] or "")
    assert panel._revertButton.isEnabled() is False