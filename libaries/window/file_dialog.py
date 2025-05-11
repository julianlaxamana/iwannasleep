import os
import io
import json
import uuid
import sqlite3
import datetime
import pandas as pd

#os.environ["QT_API"] = "pyside6" 

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PySide6.QtCore import QTimer, QFile
from PySide6.QtWidgets import (
    QDialog, QFileDialog, QVBoxLayout, QWidget, QComboBox, QPushButton,
    QMessageBox, QTableWidgetItem
)
from PySide6.QtUiTools import QUiLoader

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class FILE_SELECTOR(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loader = QUiLoader()

        ui_path = os.path.join(os.path.dirname(__file__), "..", "..", "ui", "file_dialog.ui")
        ui_path = os.path.normpath(ui_path)  # normalize slashes for Windows
        file = QFile(ui_path)  # Path to your UI file
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file) # Organize the UIs into folder and find them.

        # Set the layout of this QDialog to hold the loaded UI
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

        # Set window title and fit the contents
        self.adjustSize()
        self.setWindowTitle("JSON to CSV Viewer")

        # Find object and it's name
        self.x_axis_combo = self.ui.findChild(QComboBox, "xAxisComboBox")
        self.y_axis_combo = self.ui.findChild(QComboBox, "yAxisComboBox")
        self.plot_button = self.ui.findChild(QPushButton, "plotButton")
        self.plot_button.setEnabled(False) # Disable initially
        self.save_button = self.ui.findChild(QPushButton, "saveFilesButton")

        # Create canvas
        self.canvas = MplCanvas(self)
        # Find the placeholder QWidget
        placeholder = self.ui.findChild(QWidget, "canvasPlaceholder")
        # Insert the canvas into the placeholder
        layout = QVBoxLayout(placeholder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        # Connect the QPushButton "plotButton" to plot a graph
        self.plot_button.clicked.connect(self.plot_graph)

        # Connect the QPushButton "saveFilesbutton" to save to db file
        self.save_button.clicked.connect(self.save_to_db)

        # Delay file dialog until UI is fully shown
        QTimer.singleShot(0, self.open_file_dialog)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select a JSON File", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.convert_json_to_csv(file_path)
        else:
            self.reject()  # Close the dialog if no file is selected

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
        table = self.ui.tableWidget
        table.setRowCount(df.shape[0])
        table.setColumnCount(df.shape[1])
        table.setHorizontalHeaderLabels(df.columns)

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iat[row, col]))
                table.setItem(row, col, item)

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

    def save_to_db(self):
        if self.df is not None:
            # Resolve full path to database file
            db_path = os.path.join(os.path.dirname(__file__), "..", "..", "database", "drone_data.db")
            db_path = os.path.normpath(db_path)

            # Make sure the parent folder exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

            # Connect to the DB
            conn = sqlite3.connect(db_path)
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

            # Show confirmation to the user
            QMessageBox.information(self, "Saved", "Data and metadata saved successfully!")
            print(f"Data and metadata saved to database under table '{unique_id}'")
            # Close the dialog or give user feedback
            self.accept()  # use self.reject() if canceling instead
