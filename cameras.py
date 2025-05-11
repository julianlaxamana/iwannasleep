import sys
import cv2
import threading
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer, Qt

class CameraApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multiple Feeds from One Camera")

        self.label1 = QLabel("Feed 1")
        self.label2 = QLabel("Feed 2")

        self.label1.setAlignment(Qt.AlignCenter)
        self.label2.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        self.setLayout(layout)

        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # roughly 30 FPS

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(self.label1.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.label1.setPixmap(pixmap)
        self.label2.setPixmap(pixmap)  # same image used in both

    def closeEvent(self, event):
        self.cap.release()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraApp()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
