import cv2
import dxcam
import keyboard
import math
import numpy as np
from pathlib import Path
import pydirectinput
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
import sys
from scrolllabel import ScrollLabel
import threading
import time
import torch

import cv2
import torch
import torchvision
import torch.backends.cudnn as cudnn
import yaml

# is_active = False

# def set_active():
#     global is_active

#     is_active = not is_active
#     print("program activated" if is_active else "program deactivated")

# def start_window(x, y, w, h):
#     global window

#     window.setGeometry(x, y, w, h)
#     window.setWindowTitle("Valorant AI")

# # Set up keyboard hotkey
# keyboard.add_hotkey("ctrl+alt+s", set_active)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())