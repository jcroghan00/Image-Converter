import os
from pathlib import Path

import ffmpeg

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


directories = [""] * 2

start_type = "heic"
end_type = "heic"

last_path = os.path.join(Path.home(), "Pictures")


class ErrorDialog(QMessageBox):
    def __init__(self, parent, error_text):
        super().__init__(parent)

        self.setWindowTitle("ERROR")
        self.setIcon(QMessageBox.Icon.Warning)

        self.setText(error_text)

        self.setStandardButtons(QMessageBox.StandardButton.Ok)


class PathWidget(QWidget):
    path_line = None
    directory_i = -1

    def __init__(self, placeholder_text, i):
        super().__init__()

        self.directory_i = i

        path_layout = QHBoxLayout()

        self.path_line = QLineEdit()
        self.path_line.setMaxLength(255)
        self.path_line.setPlaceholderText(placeholder_text)
        self.path_line.textChanged.connect(self.line_updated)

        path_button = QPushButton()
        path_button.setIcon(QIcon("Images/folder.png"))
        path_button.clicked.connect(self.get_directory)
        path_button.setFixedSize(QSize(24, 24))

        path_layout.addWidget(self.path_line)
        path_layout.addWidget(path_button)

        self.setLayout(path_layout)

    def get_directory(self):
        global directories, last_path

        dlg = QFileDialog(self)
        directory = dlg.getExistingDirectory(self, "Open Directory", last_path)
        last_path = os.path.dirname(directory)

        self.path_line.setText(directory)

    def line_updated(self, s):
        global directories

        if s == "":
            self.setStyleSheet(None)
            directories[self.directory_i] = ""
        elif os.path.isdir(s):
            self.setStyleSheet(None)
            directories[self.directory_i] = s
        else:
            self.setStyleSheet("QLineEdit { border-style: solid; border-width: 2px; border-color: red;}")
            directories[self.directory_i] = ""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Converter")
        self.setWindowIcon(QIcon("Images/gallery.png"))

        vertical_layout = QVBoxLayout()

        type_layout = QHBoxLayout()
        path_layout = QHBoxLayout()

        image_type_list = ["heic", "jpg", "png"]

        start_type_widget = QComboBox()
        start_type_widget.addItems(image_type_list)
        start_type_widget.currentTextChanged.connect(self.SetStartType)

        type_layout.addWidget(start_type_widget)

        type_label = QLabel("to", alignment=Qt.AlignmentFlag.AlignCenter)
        type_label.setFixedSize(QSize(24, 24))

        type_layout.addWidget(type_label)

        end_type_widget = QComboBox()
        end_type_widget.addItems(image_type_list)
        end_type_widget.currentTextChanged.connect(self.SetEndType)

        type_layout.addWidget(end_type_widget)

        path_layout.setContentsMargins(0, 10, 0, 10)

        path_layout.addWidget(PathWidget("Start Path", 0))
        path_layout.addWidget(PathWidget("End Path", 1))

        convert_button = QPushButton("Convert")
        convert_button.clicked.connect(self.convert_images)
        convert_button.setMaximumHeight(100)

        self.setMinimumSize(QSize(700, 250))

        vertical_layout.addLayout(type_layout)
        vertical_layout.addLayout(path_layout)
        vertical_layout.addWidget(convert_button)

        widget = QWidget()
        widget.setLayout(vertical_layout)
        self.setCentralWidget(widget)

    def SetStartType(self, s):
        global start_type, last_path
        start_type = s

    def SetEndType(self, s):
        global end_type, last_path
        end_type = s

    def convert_images(self):
        if directories[0] == "" or directories[1] == "":
            ErrorDialog(self, "One or both directories are invalid.").exec()
            return

        filenames = [name for name in os.listdir(directories[0]) if name.lower().endswith(f'.{start_type}')]

        if len(filenames) == 0:
            ErrorDialog(self, "No valid files in starting directory.").exec()

        for filename in filenames:
            try:
                (ffmpeg
                    .input(os.path.join(directories[0], filename))
                    .output(os.path.join(directories[1], filename.replace(f".{start_type}", f".{end_type}")))
                    .run())
            except:
                ErrorDialog(self, f"Error converting {filename}").exec()
                return


if __name__ == '__main__':
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()
