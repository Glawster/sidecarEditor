from pathlib import Path
from typing import Optional

from PySide6.QtCore import QFile, Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QDialogButtonBox


class ButtonBar(QWidget):
    okRequested = Signal()
    cancelRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._buttonBox: Optional[QDialogButtonBox] = None
        self._setupUi()

    def _setupUi(self):
        uiFilePath = Path(__file__).parent / "buttonBar.ui"

        loader = QUiLoader()
        uiFile = QFile(str(uiFilePath))
        if not uiFile.open(QFile.ReadOnly):  # type: ignore
            raise RuntimeError(f"Failed to open UI file: {uiFilePath}")

        # Root of the .ui is a QWidget; parent it to self
        loadedRoot = loader.load(uiFile, self)
        uiFile.close()

        if loadedRoot is None:
            raise RuntimeError(f"Failed to load UI file: {uiFilePath}")

        self._buttonBox = loadedRoot.findChild(QDialogButtonBox, "buttonBox")  # type: ignore
        if self._buttonBox is None:
            raise RuntimeError("Missing widget in buttonBar.ui: buttonBox")

        self._buttonBox.accepted.connect(self.okRequested.emit)  # type: ignore
        self._buttonBox.rejected.connect(self.cancelRequested.emit)  # type: ignore
