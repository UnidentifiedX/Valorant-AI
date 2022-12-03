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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())