import cv2
import time

from detector import Detector
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QMainWindow
from scrolllabel import ScrollLabel

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Screen capture display
        self.captured_image = QtWidgets.QLabel(self)
        self.captured_image.setAlignment(QtCore.Qt.AlignTop) 

        # Output textbox
        self.output_textbox = ScrollLabel(self)
        self.output_textbox.setFixedSize(1280, 300)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.captured_image)
        layout.addWidget(self.output_textbox)
        self.setLayout(layout)
        self.screenshot()

    def screenshot(self):
        self.screenshotter = Detector()
        self.thread = QThread()

        self.screenshotter.frame.connect(self.display_results)
        self.screenshotter.moveToThread(self.thread)
        self.thread.started.connect(self.screenshotter.screenshot)
        self.thread.start()

    def log_console(self, content):
        self.output_textbox.append(content)

    def display_results(self, frame):
        now = time.time()
        # ndarray to qpixmap
        frame = cv2.resize(frame, dsize=(1280, 720))
        h, w, _ = frame.shape
        qImg = QtGui.QImage(frame.data, w, h, 3 * w, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qImg)

        self.captured_image.setPixmap(pixmap)