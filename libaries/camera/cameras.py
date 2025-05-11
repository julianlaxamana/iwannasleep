import sys
import os
import cv2
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap, QIcon

class CAMERAS:
    def __init__(self, labels, combos, toggle_buttons, num_cameras=3):
        self.num_cameras = num_cameras
        self.labels = labels
        self.combos = combos
        self.toggle_buttons = toggle_buttons

        self.selected_camera_indices = [0, 1, 2]
        self.feed_enabled = [False] * 3
        self.frames = [None] * self.num_cameras

        # Load icon and no signal image path
        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "graphics", "white_camera.png")
        self.icon = QIcon(os.path.normpath(icon_path))
        self.no_signal_path = os.path.join(os.path.dirname(__file__), "..", "..", "graphics", "no_signal.png").replace("\\", "/")

        # Safely initialize camera captures
        self.captures = []
        for i in range(self.num_cameras):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.captures.append(cap)
            else:
                print(f"[Warning] Camera index {i} not available.")
                self.captures.append(None)

        # Setup widgets
        for i in range(3):
            self.labels[i].setAlignment(Qt.AlignCenter)
            self.labels[i].clear()

            self.combos[i].addItems([f"Camera {j+1}" for j in range(self.num_cameras)])
            self.combos[i].setCurrentIndex(i)
            self.combos[i].currentIndexChanged.connect(self.update_camera_selection)

            self.toggle_buttons[i].setCheckable(True)
            self.toggle_buttons[i].setChecked(False)
            self.toggle_buttons[i].setIcon(self.icon)
            self.toggle_buttons[i].setStyleSheet("background-color: #424242;")
            self.toggle_buttons[i].toggled.connect(lambda checked, idx=i: self.toggle_feed(idx, checked))

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(30)

    def update_camera_selection(self):
        self.selected_camera_indices = [combo.currentIndex() for combo in self.combos]

    def toggle_feed(self, index, checked):
        self.feed_enabled[index] = checked
        if checked:
            self.toggle_buttons[index].setStyleSheet("background-color: #007ACC;")
        else:
            self.toggle_buttons[index].setStyleSheet("background-color: #424242;")

            # Show "No Signal" image when toggled off
            no_signal_pixmap = QPixmap(self.no_signal_path)
            scaled_pixmap = no_signal_pixmap.scaled(
                self.labels[index].size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.labels[index].setPixmap(scaled_pixmap)

    def update_frames(self):
        for i, cap in enumerate(self.captures):
            if cap is not None:
                ret, frame = cap.read()
                self.frames[i] = frame if ret else None
            else:
                self.frames[i] = None

        for i in range(3):
            cam_index = self.selected_camera_indices[i]

            # If feed is turned off, show a black screen
            if not self.feed_enabled[i]:
                black_pixmap = QPixmap(self.labels[i].size())
                black_pixmap.fill(Qt.black)
                self.labels[i].setPixmap(black_pixmap)
                continue

            # If the camera index is out of bounds, skip
            if cam_index >= len(self.frames):
                continue

            frame = self.frames[cam_index]

            # Show "No Signal" if the camera feed failed
            if frame is None:
                no_signal_pixmap = QPixmap(self.no_signal_path)
                scaled_pixmap = no_signal_pixmap.scaled(
                    self.labels[i].size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.labels[i].setPixmap(scaled_pixmap)
                continue

            # Crop to 16:9
            h, w, _ = frame.shape
            desired_h = int(w * 9 / 16)
            desired_w = int(h * 16 / 9)
            if desired_h <= h and desired_w <= w:
                if desired_h > h:
                    desired_h = h
                    desired_w = int(h * 16 / 9)
                if desired_w > w:
                    desired_w = w
                    desired_h = int(w * 9 / 16)

                y_offset = (h - desired_h) // 2
                x_offset = (w - desired_w) // 2
                frame = frame[y_offset:y_offset + desired_h, x_offset:x_offset + desired_w]

            # Convert to RGB and show
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg).scaled(
                self.labels[i].size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.labels[i].setPixmap(pixmap)

    def switch_primary_camera_to(self, new_index):
        if 0 <= new_index < self.num_cameras:
            self.combos[0].setCurrentIndex(new_index)  # Switch the primary feed (index 0)
            print(f"[Info] Switched primary feed to camera index {new_index}")
            # Optionally ensure it's turned on
            if not self.feed_enabled[0]:
                self.toggle_buttons[0].click()  # Programmatically toggle it on

    def set_primary_only_view(self, camera_index=0):
        """
        Display only the primary camera on the first label.
        Hide other feeds and turn off their capture.
        """
        for i in range(3):
            if i == 0:
                #self.combos[i].setCurrentIndex(camera_index)
                self.feed_enabled[i] = True
                self.toggle_buttons[i].setChecked(True)
                self.labels[i].show()
            else:
                self.feed_enabled[i] = False
                self.toggle_buttons[i].setChecked(False)
                self.labels[i].hide()  # Hide the QLabel

        # print(f"[View] Primary-only view set to Camera {camera_index}")

    def set_three_camera_view(self):
        """
        Display all three camera feeds on all three labels.
        Set default camera indices (0, 1, 2) or use previously selected.
        """
        for i in range(3):
            #self.combos[i].setCurrentIndex(i)
            self.feed_enabled[i] = True
            self.toggle_buttons[i].setChecked(True)
            self.labels[i].show()  # Make sure all labels are visible

        # print("[View] Switched to 3-camera view")


    def release_captures(self):
        for cap in self.captures:
            if cap is not None:
                cap.release()
