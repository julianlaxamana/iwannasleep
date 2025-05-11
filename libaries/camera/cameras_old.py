import sys
import cv2
import os
from PySide6.QtCore import QTimer, Qt, QFile, QThread, Signal
from PySide6.QtGui import QImage, QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QSizePolicy
from PySide6.QtUiTools import QUiLoader

class CAMERA(QThread):
    frame_signal = Signal(QPixmap)
    def __init__(self, label, combo_box, toggle_button, parent=None):
        self.label = label
        self.combo_box = combo_box
        self.toggle_button = toggle_button
        self.capture = None
        self.timer = QTimer(parent)
        self.timer.timeout.connect(self.update_frame)

        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "graphics", "white_camera.png")  # Replace with your image path
        self.icon = QIcon(os.path.normpath(icon_path))
        self.toggle_button.setIcon(self.icon)
        self.toggle_button.clicked.connect(self.toggle_camera)
        self.combo_box.addItems([f"Camera {i+1}" for i in range(3)])  # Named cameras

    def toggle_camera(self):
        if self.capture is None:
            cam_text = self.combo_box.currentText()
            cam_index = int(cam_text.split()[-1]) - 1  # Convert "Camera 1" → 0
            
            cap = cv2.VideoCapture(cam_index)
            if cap.isOpened():
                self.capture = cap
                self.toggle_button.setStyleSheet("background-color: #007ACC;") #Turn OFF
                self.timer.start(30)
            else:
                no_signal_path = os.path.join(os.path.dirname(__file__), "..", "..", "graphics", "no_signal.png").replace("\\", "/")
                self.label.setText("Camera not found")
                no_signal_pixmap = QPixmap(no_signal_path)
                scaled_pixmap = no_signal_pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                # Ensure alignment is centered
                self.label.setAlignment(Qt.AlignCenter)
                # Clear any text and set the image
                self.label.clear()
                self.label.setPixmap(scaled_pixmap)
        else:
            self.stop_camera()

    def stop_camera(self):
        if self.capture:
            #self.timer.stop()
            #self.capture.release()
            self.capture = None
            self.label.clear()
            self.label.setStyleSheet("background-color: black;")
            self.toggle_button.setStyleSheet("background-color: #424242;") #Turn ON

    def update_frame(self):
        if self.capture and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Crop frame to 16:9
                h, w, _ = frame.shape
                desired_w = w
                desired_h = int(w * 9 / 16)
                if desired_h > h:
                    desired_h = h
                    desired_w = int(h * 16 / 9)

                y_offset = (h - desired_h) // 2
                x_offset = (w - desired_w) // 2
                frame = frame[y_offset:y_offset + desired_h, x_offset:x_offset + desired_w]

                # Convert to QPixmap
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img)

                scaled_pixmap = pixmap.scaled(
                    self.label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.label.setPixmap(scaled_pixmap)

    def cleanup(self):
        self.stop_camera()