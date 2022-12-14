import copy
import cv2
import keyboard
from numpy import ndarray
import numpy as np
import os
import time

from detector import Detector
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QMainWindow
from scrolllabel import ScrollLabel

from navigation_utils import nd2qpixmap, mark_circles

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Set up keyboard hotkeys
        keyboard.add_hotkey("ctrl+alt+g", self.initialise_game)
        keyboard.add_hotkey("ctrl+alt+s", self.start_game)

        # Set map initialisation to false
        self.is_map_initialised = False

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

        # Initialise new game
        self.initialise_game_button = QtWidgets.QPushButton("Initialise new game (Ctrl+Alt+G)")
        self.initialise_game_button.setGeometry(1300, 450, 440, 30)
        self.initialise_game_button.setParent(self)
        self.initialise_game_button.setToolTip("Initialise new game")
        self.initialise_game_button.clicked.connect(self.initialise_game)
        self.initialise_game_button.show()

        # Start game
        self.start_game_button = QtWidgets.QPushButton("Start game (Ctrl+Alt+S)")
        self.start_game_button.setGeometry(1300, 490, 440, 30)
        self.start_game_button.setParent(self)
        self.start_game_button.setToolTip("Start game")
        self.start_game_button.clicked.connect(self.start_game)
        self.start_game_button.show()

        # FPS text
        self.fps_text = QtWidgets.QLabel()
        self.fps_text.setGeometry(1750, 0, 100, 15)
        self.fps_text.setParent(self)
        self.fps_text.show()

        # Map text
        self.map_text = QtWidgets.QLabel("MAP UNKNOWN")
        self.map_text.setGeometry(1750, 15, 200, 20)
        self.map_text.setParent(self)
        self.map_text.show()

        # Coordinates text
        self.coordinates_text = QtWidgets.QLabel("COORDS UNKNOWN")
        self.coordinates_text.setGeometry(1750, 30, 500, 20)
        self.coordinates_text.setParent(self)
        self.coordinates_text.show()

        # View angle text
        self.rotation_text = QtWidgets.QLabel("ROTATION UNKNOWN")
        self.rotation_text.setGeometry(1750, 45, 500, 20)
        self.rotation_text.setParent(self)
        self.rotation_text.show()

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

    def start_game(self):
        if not self.is_map_initialised:
            error = QtWidgets.QMessageBox()
            error.setIcon(QtWidgets.QMessageBox.Critical)
            error.setText("Error")
            error.setInformativeText('Game is not initialised. Please initialise game before starting it.')
            error.setWindowTitle("Game not initialised")
            error.exec_()
            
            return

        print("Game started")

    def initialise_game(self):
        self.initialise_map()
        self.log_console("Initlialised")

    def initialise_map(self):
        map_img = self.current_game_frame[20:465, 10:450] # [y:y+h, x:x+w]
        retrieved_map_img = None

        # Get map name
        with os.scandir("./Maps") as maps:
            lowest = None
            map_file_name = None
            for game_map in maps:    
                if game_map.is_file():
                    image = cv2.imread(game_map.path)

                    diff = cv2.absdiff(map_img, image)
                    mean_diff = np.mean(diff)
                    self.output_textbox.append(f"{game_map.name} {mean_diff}")
                    
                    if lowest == None or mean_diff < lowest:
                        map_file_name = game_map.name
                        lowest = mean_diff
            
            self.map_text.setText(map_file_name.replace(".png", ""))
            retrieved_map_img = cv2.cvtColor(cv2.imread(f"./Maps/{map_file_name}"), cv2.COLOR_BGR2RGB)

        # Make all pixels that are not black white
        # retrieved_map_img[retrieved_map_img != 0] = 255


        self.is_map_initialised = True

    def display_results(self, frame):
        self.current_game_frame = frame # make the frame accessible for other methods such as initialising the map

        # display game screen
        resized_frame = cv2.resize(frame, dsize=(1280, 720))
        gamescreen_pixmap = nd2qpixmap(resized_frame)
        self.captured_image.setPixmap(gamescreen_pixmap)
        
        # display game map state
        map_img = frame[20:465, 10:450] # [y:y+h, x:x+w]

        # calculate coordinates and view angle if the map as been initialised
        if self.is_map_initialised:
            # mark player circle
            marked_circle = mark_circles(map_img)

            rotation = marked_circle.rotation
            mask = marked_circle.mask_marked

            self.rotation_text.setText(f"{rotation:.2f} deg" if rotation != None else "ROTATION UNKNOWN")

            map_pixmap = nd2qpixmap(mask)
            self.game_map_image.setPixmap(map_pixmap)

            return
        
        # else, display the plain captured map
        map_pixmap = nd2qpixmap(map_img)
        self.game_map_image.setPixmap(map_pixmap)
    
    def display_fps(self, fps):
        self.fps_text.setText(f"{fps} FPS")