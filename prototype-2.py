import sys
import threading
from PySide6.QtGui import QAction, QFont, QFontDatabase, QKeyEvent
from PySide6.QtCore import QCoreApplication, QFile, Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QStackedWidget, QLabel, QComboBox, QWidget
)
from PySide6.QtUiTools import QUiLoader
import mqtt

from libaries.visual.visualEffects import STYLE
from libaries.camera.cameras import CAMERAS

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load UI file dynamically
        loader = QUiLoader()
        file = QFile("ui/main4-test.ui")  # Path to your UI file
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file)  # Loads in "main.ui" 
        self.setCentralWidget(self.ui)
        self.setWindowTitle("ROV Dashboard")  

        # Open up on first tab
        self.stacked_widget = self.ui.findChild(QStackedWidget, "stackedWidget") # stacked widget
        self.stacked_widget.setCurrentIndex(0) 

        # Grabbing buttons for switching tabs
        self.controlPanelButton = self.ui.findChild(QPushButton, "controlPanelButton")
        self.dataButton = self.ui.findChild(QPushButton, "dataButton")
        self.mappingButton = self.ui.findChild(QPushButton, "mappingButton")

        # Switching tabs
        self.controlPanelButton.clicked.connect(lambda: self.switchTabs(0))
        self.dataButton.clicked.connect(lambda: self.switchTabs(1))
        self.mappingButton.clicked.connect(lambda: self.switchTabs(2))

        self.style = STYLE()
        self.style.setStylesheet(QApplication.instance())
        self.t =  threading.Thread(target=self.update)
        self.t.start()

        self.controlPanelTab() # Control Panel

    def switchTabs(self, tab_index: int):
        # Switch stacked widget
        if 0 <= tab_index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(tab_index)

        # Reset all button styles
        buttons = [self.controlPanelButton, self.dataButton, self.mappingButton]
        for i, btn in enumerate(buttons):
            if i == tab_index:
                # Active button style
                btn.setStyleSheet("background-color: #007ACC;")  # blue
            else:
                # Inactive button style
                btn.setStyleSheet("background-color: #424242;")  # gray


    def update(self):
        while True:
            self.t1_label = self.ui.findChild(QLabel, "thruster1")
            self.t1_label.setText("Thruster1: " + str(mqtt.thruster1[0]))

            self.t2_label = self.ui.findChild(QLabel, "thruster2")
            self.t2_label.setText("Thruster2: " + str(mqtt.thruster1[1]))

    def controlPanelTab(self):
        
        # Find object and it's name
        self.program_exit = self.ui.findChild(QPushButton, "program_exit") # Quit action
        # Connect the QAction "actionQuit" to quit the application
        self.program_exit.clicked.connect(QApplication.instance().quit)  # Quit the application

        # Example toggle button in your GUI
        self.secondary_cameras = self.ui.findChild(QWidget, "secondary_camera_feeds")
        self.toggle_view_button = self.ui.findChild(QPushButton, "toggleViewButton")
        self.toggle_view_button.clicked.connect(self.toggle_view_mode)
        self.current_mode = "multi"

        # Dynamically change children once for
        self.cam_1_label = self.ui.findChild(QLabel, "camera_feed_1")
        self.cam_2_label = self.ui.findChild(QLabel, "camera_feed_2")
        self.cam_3_label = self.ui.findChild(QLabel, "camera_feed_3")

        self.cam_1_combo = self.ui.findChild(QComboBox, "camera_feed_1_menu")
        self.cam_2_combo = self.ui.findChild(QComboBox, "camera_feed_2_menu")
        self.cam_3_combo = self.ui.findChild(QComboBox, "camera_feed_3_menu")

        self.cam_1_toggle_btn = self.ui.findChild(QPushButton, "primaryCameraToggleButton")
        self.cam_2_toggle_btn = self.ui.findChild(QPushButton, "secondaryCamera_1_ToggleButton")
        self.cam_3_toggle_btn = self.ui.findChild(QPushButton, "secondaryCamera_2_ToggleButton")

        # Initialize camera handlers
        self.cameras = CAMERAS(
            labels=[
                self.cam_1_label,
                self.cam_2_label,
                self.cam_3_label
            ],
            combos=[
                self.cam_1_combo,
                self.cam_2_combo,
                self.cam_3_combo
            ],
            toggle_buttons=[
                self.cam_1_toggle_btn,
                self.cam_2_toggle_btn,
                self.cam_3_toggle_btn
            ]
        )

    def closeEvent(self, event):
        self.cameras.release_captures()
        super().closeEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.showMaximized()
        elif event.key() == Qt.Key_1:
            self.cameras.switch_primary_camera_to(0)
        elif event.key() == Qt.Key_2:
            self.cameras.switch_primary_camera_to(1)
        elif event.key() == Qt.Key_3:
            self.cameras.switch_primary_camera_to(2)

    def toggle_view_mode(self):
            camera_panel_container = self.ui.findChild(QWidget, "control_panel_camera_widget")
            layout = camera_panel_container.layout()

            if self.current_mode == "multi":
                self.cameras.set_primary_only_view(camera_index=0)
                self.secondary_cameras.hide()
                layout.setRowStretch(0, 0)  # Top row
                layout.setRowStretch(1, 1)  # Second row
                self.current_mode = "primary"
            else:
                self.cameras.set_three_camera_view()
                self.secondary_cameras.show()
                layout.setRowStretch(0, 1)  # Top row
                layout.setRowStretch(1, 0)  # Second row
                self.current_mode = "multi"

            # ⏩ Force layout recalculation
            camera_panel_container.updateGeometry()
            camera_panel_container.update()
            camera_panel_container.repaint()


def guiInitiate(): 
    """
    PURPOSE

    Launches program and selects font.

    INPUTS

    NONE

    RETURNS

    NONE
    """
    # Set the attribute BEFORE creating QApplication
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    # Run the application
    app = QApplication(sys.argv)

    # Load the font file
    font_id = QFontDatabase.addApplicationFont("graphics/fonts/bahnschrift.ttf")

    # Get the font family name
    if font_id != -1:
        family = QFontDatabase.applicationFontFamilies(font_id)[0]
        custom_font = QFont(family)
        app.setFont(custom_font)
        print(f"Loaded custom font: {family}")
    else:
        print("Failed to load custom font.")
        
    app.setStyle("Fusion")

    window = MyApp()
    window.showFullScreen() # Show screen
    sys.exit(app.exec())

if __name__ == '__main__':
    guiInitiate()
