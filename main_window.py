import copy
import cv2
from numpy import ndarray
import numpy as np
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
        self.captured_image = QtWidgets.QLabel()
        self.captured_image.setGeometry(10, 0, 1280, 720)
        self.captured_image.setParent(self)
        self.captured_image.show()

        # Game map display
        self.game_map_image = QtWidgets.QLabel()
        self.game_map_image.setGeometry(1300, 0, 440, 445) # (_, _, w, h) derived from frame[20:465, 10:450] => [y:y+h, x:x+w]
        self.game_map_image.setParent(self)
        self.game_map_image.show()

        # Output textbox
        self.output_textbox = ScrollLabel()
        self.output_textbox.setGeometry(10, 730, 1280, 270)
        self.output_textbox.setParent(self)
        self.output_textbox.show()

        # FPS text
        self.fps_text = QtWidgets.QLabel()
        self.fps_text.setGeometry(1750, 0, 50, 10)
        self.fps_text.setParent(self)
        self.fps_text.show()

        self.screenshot()

    def screenshot(self):
        self.screenshotter = Detector()
        self.thread = QThread()

        self.screenshotter.frame.connect(self.display_results)
        self.screenshotter.fps.connect(self.display_fps)
        
        self.screenshotter.moveToThread(self.thread)
        self.thread.started.connect(self.screenshotter.screenshot)
        self.thread.start() 

    def log_console(self, content):
        self.output_textbox.append(content)

    def display_results(self, frame):
        # display game screen
        resized_frame = cv2.resize(frame, dsize=(1280, 720))
        gamescreen_pixmap = nd2qpixmap(resized_frame)
        self.captured_image.setPixmap(gamescreen_pixmap)
        
        # display game map state
        map_img = frame[20:465, 10:450] # [y:y+h, x:x+w]
        img_gray = cv2.cvtColor(map_img, cv2.COLOR_BGR2GRAY)
        (threshi, img_bw) = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        map_pixmap = nd2qpixmap(img_bw)
        self.game_map_image.setPixmap(map_pixmap)
    
    def display_fps(self, fps):
        self.fps_text.setText(f"{fps} FPS")

# ndarray to qpixmap
def nd2qpixmap(nd: ndarray):
    gray_color_table = [QtGui.qRgb(i, i, i) for i in range(256)]

    if nd.dtype == np.uint8:
        if len(nd.shape) == 2:
            qImg = QtGui.QImage(nd.data, nd.shape[1], nd.shape[0], nd.strides[0], QtGui.QImage.Format.Format_Indexed8)
            qImg.setColorTable(gray_color_table)
            return QtGui.QPixmap.fromImage(qImg)

        elif len(nd.shape) == 3:
            if nd.shape[2] == 3:
                qImg = QtGui.QImage(nd.data, nd.shape[1], nd.shape[0], nd.strides[0], QtGui.QImage.Format.Format_RGB888)
                return QtGui.QPixmap.fromImage(qImg)
            elif nd.shape[2] == 4:
                qImg = QtGui.QImage(nd.data, nd.shape[1], nd.shape[0], nd.strides[0], QtGui.QImage.Format.Format_ARGB32)
                return QtGui.QPixmap.fromImage(qImg)