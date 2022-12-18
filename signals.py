from numpy import ndarray
from PyQt5 import QtCore
from PyQt5.QtCore import QObject

class DetectorSignals(QObject):
    frame = QtCore.pyqtSignal(ndarray)
    fps = QtCore.pyqtSignal(int)

class NavigatorSignals(QObject):
    pass