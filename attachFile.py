import sys
import pandas as pd
import sqlite3
import uuid
import io
import datetime
import os
import json
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog,
    QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
    QComboBox, QHBoxLayout
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Automatically open file dialog on startup
        QTimer.singleShot(0, self.open_file_dialog)

        self.setWindowTitle("JSON to CSV Viewer and Grapher")

        # Button to attach file
        self.attach_button = QPushButton("Attach JSON File")
        self.attach_button.clicked.connect(self.open_file_dialog)

        # Table widget to display data
        self.table_widget = QTableWidget()

        # Combo boxes for axis selection
        self.x_axis_combo = QComboBox()
        self.y_axis_combo = QComboBox()
        self.plot_button = QPushButton("Plot Graph")
        self.plot_button.clicked.connect(self.plot_graph)
        self.plot_button.setEnabled(False) # Disable initially
        self.save_button = QPushButton("Save Files")
        self.save_button.clicked.connect(self.save_to_db)
        #self.save_button.setEnabled(False) # Disable initially

        # Matplotlib canvas
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)

        # Layout for axis selection
        axis_layout = QHBoxLayout()
        axis_layout.addWidget(QLabel("X-Axis:"))
        axis_layout.addWidget(self.x_axis_combo)
        axis_layout.addWidget(QLabel("Y-Axis:"))
        axis_layout.addWidget(self.y_axis_combo)
        axis_layout.addWidget(self.plot_button)
        axis_layout.addWidget(self.save_button)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.attach_button)
        layout.addWidget(self.table_widget)
        layout.addLayout(axis_layout)
        layout.addWidget(self.canvas)

        print(self.width())   # returns 640
        print(self.height())  # returns 480


        # Container widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.df = None # Store the DataFrame

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select a JSON File", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.convert_json_to_csv(file_path)

    def convert_json_to_csv(self, file_path):
        try:
            # Read JSON file
            with open(file_path, "r", encoding="utf-8") as file:
                json_data = json.load(file)

            # Convert JSON to DataFrame
            self.df = pd.DataFrame(json_data)

            # Display CSV Data in Table
            self.display_csv_in_table(self.df)

            # Populate combo boxes
            self.x_axis_combo.clear()
            self.y_axis_combo.clear()
            self.x_axis_combo.addItems(self.df.columns)
            self.y_axis_combo.addItems(self.df.columns)
            self.plot_button.setEnabled(True) # Enable plot button

        except Exception as e:
            print(f"Error: {e}")
            self.table_widget.clear()
            self.x_axis_combo.clear()
            self.y_axis_combo.clear()
            self.plot_button.setEnabled(False)

    def display_csv_in_table(self, df):
        self.table_widget.setRowCount(df.shape[0])
        self.table_widget.setColumnCount(df.shape[1])
        self.table_widget.setHorizontalHeaderLabels(df.columns)

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iat[row, col]))
                self.table_widget.setItem(row, col, item)

    def plot_graph(self):
        if self.df is not None:
            x_axis_column = self.x_axis_combo.currentText()
            y_axis_column = self.y_axis_combo.currentText()

            if x_axis_column and y_axis_column and x_axis_column in self.df.columns and y_axis_column in self.df.columns:
                try:
                    x_data = self.df[x_axis_column]
                    y_data = self.df[y_axis_column]

                    self.canvas.axes.clear()
                    self.canvas.axes.plot(x_data, y_data)
                    self.canvas.axes.set_xlabel(x_axis_column)
                    self.canvas.axes.set_ylabel(y_axis_column)
                    self.canvas.axes.set_title(f"{y_axis_column} vs {x_axis_column}")
                    self.canvas.draw()
                    self.save_button.setEnabled(True)
                except Exception as e:
                    print(f"Error plotting graph: {e}")
            else:
                print("Please select valid X and Y axis columns.")
        else:
            print("No data loaded to plot.")

    def save_graph_as_image(self):
        if self.df is not None:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Graph as Image", "", "PNG Files (*.png);;All Files (*)"
            )
            if file_path:
                try:
                    self.canvas.figure.savefig(file_path)
                    print(f"Graph saved to {file_path}")
                except Exception as e:
                    print(f"Error saving graph: {e}")
            else:
                print("Save operation cancelled.")
        else:
            print("No data available to save.")

    def save_to_db(self):
        if self.df is not None:
            os.makedirs("data", exist_ok=True)
            conn = sqlite3.connect("data/drone_data.db")
            cursor = conn.cursor()

            # Unique ID for the DataFrame table
            unique_id = str(uuid.uuid4()).replace("-", "_")

            # Save DataFrame
            self.df.to_sql(unique_id, conn, if_exists='replace', index=False)

            # Prepare metadata
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

            # Save the plot as PNG to memory
            buf = io.BytesIO()
            self.canvas.figure.savefig(buf, format='png')
            image_blob = buf.getvalue()
            buf.close()

            # Create metadata table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metadata (
                    table_name TEXT PRIMARY KEY,
                    timestamp TEXT,
                    image BLOB
                )
            ''')

            # Insert metadata
            cursor.execute('''
                INSERT INTO metadata (table_name, timestamp, image) VALUES (?, ?, ?)
            ''', (unique_id, timestamp, image_blob))

            conn.commit()
            conn.close()
            print(f"Data and metadata saved to database under table '{unique_id}'")

from PySide6.QtWidgets import QLabel

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
