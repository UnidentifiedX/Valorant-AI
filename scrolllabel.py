from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QMainWindow

class ScrollLabel(QtWidgets.QScrollArea):
    # constructor
    def __init__(self, *args, **kwargs):
        QtWidgets.QScrollArea.__init__(self, *args, **kwargs)

        # making widget resizable
        self.setWidgetResizable(True)

        # making qwidget object
        content = QtWidgets.QWidget(self)
        self.setWidget(content)

        # vertical box layout
        lay = QtWidgets.QVBoxLayout(content)

        # creating label
        self.label = QtWidgets.QLabel(content)

        # setting alignment to the text
        self.label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        # making label multi-line
        self.label.setWordWrap(True)

        # adding label to the layout
        lay.addWidget(self.label)

    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)

    def text(self):
        return self.label.text()

    def append(self, text):
        self.label.setText(self.text() + "\n" + text)