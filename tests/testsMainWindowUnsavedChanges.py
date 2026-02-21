from pathlib import Path

import pytest
from PySide6.QtWidgets import QMessageBox

from Qt.widgets.mainWindow import MainWindow
from src.sidecarCore import SidecarData


@pytest.fixture
def sidecar(tmp_path: Path) -> SidecarData:
    return SidecarData(imagePath=str(tmp_path / "test.png"))


def _make_dirty(mainWindow: MainWindow, sidecar: SidecarData, qtbot):
    # Load a sidecar into the editor and change a field so hasUnsavedChanges() becomes True.
    mainWindow._editorPanel.loadSidecar(sidecar)
    mainWindow._editorPanel._promptText["subject"].setPlainText("changed")
    qtbot.waitUntil(lambda: mainWindow._editorPanel.hasUnsavedChanges() is True)


def test_ok_cancel_does_not_close(qtbot, monkeypatch, sidecar):
    win = MainWindow()
    qtbot.addWidget(win)
    win.show()

    _make_dirty(win, sidecar, qtbot)

    # Always choose Cancel
    monkeypatch.setattr(
        "Qt.widgets.mainWindow.QMessageBox.question",
        lambda *args, **kwargs: QMessageBox.Cancel,
    )

    win._onOk()
    assert win.isVisible() is True


def test_ok_yes_saves_then_closes(qtbot, monkeypatch, sidecar):
    win = MainWindow()
    qtbot.addWidget(win)
    win.show()

    _make_dirty(win, sidecar, qtbot)

    # Avoid disk writes in EditorPanel.saveCurrentSidecar()
    monkeypatch.setattr(win._editorPanel, "_saveSidecar", lambda *args, **kwargs: None)

    # Choose Yes on the prompt
    monkeypatch.setattr(
        "Qt.widgets.mainWindow.QMessageBox.question",
        lambda *args, **kwargs: QMessageBox.Yes,
    )

    win._onOk()
    qtbot.waitUntil(lambda: win.isVisible() is False)


def test_closeEvent_no_ignores_close(qtbot, monkeypatch, sidecar):
    win = MainWindow()
    qtbot.addWidget(win)
    win.show()

    _make_dirty(win, sidecar, qtbot)

    monkeypatch.setattr(
        "Qt.widgets.mainWindow.QMessageBox.question",
        lambda *args, **kwargs: QMessageBox.No,
    )

    win.close()
    assert win.isVisible() is True