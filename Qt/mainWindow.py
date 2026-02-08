from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

def load_ui(path):
    f = QFile(path)
    f.open(QFile.ReadOnly)
    ui = QUiLoader().load(f)
    f.close()
    return ui

def chooseInputFolder():
    folder = QFileDialog.getExistingDirectory(None, "Select Input Folder")
    if folder:
        ui.textInputFolder.setText(folder)

def chooseOutputFolder():
    folder = QFileDialog.getExistingDirectory(None, "Select Output Folder")
    if folder:
        ui.textOutputFolder.setText(folder)

app = QApplication([])
ui = load_ui("mainwindow.ui")
ui.selectInput.clicked.connect(chooseInputFolder)
ui.selectOutput.clicked.connect(chooseOutputFolder)
ui.show()
app.exec()
