from PySide6.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout
from PySide6.QtGui import QIcon
import sys

app = QApplication(sys.argv)

window = QWidget()
layout = QVBoxLayout()

# Create a button and set an icon
button = QPushButton("Click Me")
button.setStyleSheet("""
    QPushButton {
        background-color: black;
        color: white;         /* Text color */
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
    }
    QPushButton:hover {
        background-color: #333;
    }
""")
icon = QIcon("graphics\white_camera.png")  # Replace with your image path
button.setIcon(icon)

layout.addWidget(button)
window.setLayout(layout)
window.show()

sys.exit(app.exec())
