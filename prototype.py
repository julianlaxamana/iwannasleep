import sys
from PySide6.QtGui import QAction
from PySide6.QtCore import QCoreApplication, QFile, Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTabWidget
)
from PySide6.QtUiTools import QUiLoader

from libaries.visual.visualEffects import STYLE
from libaries.window.file_dialog import FILE_SELECTOR 

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load UI file dynamically
        loader = QUiLoader()
        file = QFile("ui/main.ui")  # Path to your UI file
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file)  # Loads in "main.ui" 
        self.setCentralWidget(self.ui)
        self.setWindowTitle("ROV Dashboard")  

        # Find object and it's name
        self.action_quit = self.ui.findChild(QAction, "actionQuit") # Quit action
        self.button_attachFile = self.ui.findChild(QPushButton, "attachFile") # Attach file button
        self.tab_widget = self.ui.findChild(QTabWidget, "tabWidget") # Tab widget

        # Open up on first tab
        self.tab_widget.setCurrentIndex(0)

        # Connect the QAction "actionQuit" to quit the application
        self.action_quit.triggered.connect(QApplication.instance().quit)  # Quit the application

        # Connect the QPushButton "attachFile" to open up file dialog
        self.button_attachFile.clicked.connect(self.open_file_dialog)

    def open_file_dialog(self):
        self.dialog = FILE_SELECTOR(self)
        self.dialog.show()

# Set the attribute BEFORE creating QApplication
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
# Run the application
app = QApplication(sys.argv)
window = MyApp()
window.show() # Remove this if on
sys.exit(app.exec())