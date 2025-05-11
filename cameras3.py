import sys
import cv2
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QComboBox, QHBoxLayout, QGridLayout, QPushButton
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap

class MultiCameraViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3-Camera Viewer with Selectable Feeds")

        self.num_cameras = 3
        self.labels = [QLabel(f"Feed {i+1}") for i in range(3)]
        self.combos = [QComboBox() for _ in range(3)]
        self.toggle_buttons = [QPushButton("Turn On") for _ in range(3)]
        self.selected_camera_indices = [0, 1, 2]  # Default mappings
        self.feed_enabled = [False] * 3  # All feeds OFF by default

        layout = QVBoxLayout()
        grid = QGridLayout()

        for i in range(3):
            self.labels[i].setAlignment(Qt.AlignCenter)
            self.labels[i].setFixedHeight(240)
            self.labels[i].clear()  # Ensure it's empty at start

            self.combos[i].addItems([f"Camera {j}" for j in range(self.num_cameras)])
            self.combos[i].setCurrentIndex(i)
            self.combos[i].currentIndexChanged.connect(self.update_camera_selection)

            self.toggle_buttons[i].setCheckable(True)
            self.toggle_buttons[i].setChecked(False)  # Start off
            self.toggle_buttons[i].setText("Turn On")
            self.toggle_buttons[i].toggled.connect(lambda checked, idx=i: self.toggle_feed(idx, checked))

            row_layout = QHBoxLayout()
            row_layout.addWidget(self.combos[i])
            row_layout.addWidget(self.toggle_buttons[i])

            grid.addLayout(row_layout, i, 0)
            grid.addWidget(self.labels[i], i, 1)

        layout.addLayout(grid)
        self.setLayout(layout)

        self.captures = [cv2.VideoCapture(i) for i in range(self.num_cameras)]
        self.frames = [None] * self.num_cameras

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(30)

    def update_camera_selection(self):
        self.selected_camera_indices = [combo.currentIndex() for combo in self.combos]

    def toggle_feed(self, index, checked):
        self.feed_enabled[index] = checked
        self.toggle_buttons[index].setText("Turn Off" if checked else "Turn On")
        if not checked:
            self.labels[index].clear()

    def update_frames(self):
        for i, cap in enumerate(self.captures):
            ret, frame = cap.read()
            if ret:
                self.frames[i] = frame

        for i in range(3):
            if not self.feed_enabled[i]:
                continue

            cam_index = self.selected_camera_indices[i]
            frame = self.frames[cam_index]
            if frame is not None:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                bytes_per_line = ch * w
                qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg).scaled(
                    self.labels[i].size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.labels[i].setPixmap(pixmap)

    def closeEvent(self, event):
        for cap in self.captures:
            cap.release()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = MultiCameraViewer()
    viewer.resize(800, 720)
    viewer.show()
    sys.exit(app.exec())
