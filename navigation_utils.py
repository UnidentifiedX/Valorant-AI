import cv2
from cv2 import Mat
import math
import numpy as np
from numpy import ndarray
from PyQt5 import QtGui

class MarkedCircles:
    def __init__(self, mask_marked: Mat, rot: float):
        self.mask_marked = mask_marked
        self.rotation = rot


# https://github.com/TheRabbitProgram/Valorant-AimBot-and-Navigation-Bot/blob/main/Navigation/MapCaptureTest.py
def scan_circle(img, radius, x_offset, y_offset):
    for theta in range(360):
        x = int(radius * math.cos(theta)) + x_offset
        y = int(radius * math.sin(theta)) + y_offset

        if img[y, x] != 0:
            return x, y
    return None

def map_range(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def angle(point_a, point_b):
    deg = math.degrees(math.atan2((point_b[1] - point_a[1]), (point_b[0] - point_a[0])))
    if deg < 0:
        deg = map_range(deg, -0, -180, 0, 180)
    else:
        deg = map_range(deg, 0, 180, 360, 180)
    if deg == 360:
        deg = 0

    return deg

def mark_circles(mask: Mat):
    rot = None

    mask_marked = mask.copy()
    mask = cv2.inRange(cv2.cvtColor(mask, cv2.COLOR_RGB2HSV),
                                np.array([29, 80, 220]),
                                np.array([30, 100, 255]))

    mask = cv2.dilate(mask, np.ones((2, 2), np.uint8), iterations=1)

    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1, 20,
                                param1=1, param2=15, minRadius=0, maxRadius=0)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            # draw the outer circle
            cv2.circle(mask_marked, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(mask_marked, (i[0], i[1]), 2, (0, 0, 255), 3)

        r = 18
        while True:
            largest_offset = scan_circle(mask, r, circles[0][0][0], circles[0][0][1])
            if largest_offset is None:
                r -= 1
            else:
                break

        mask_marked = cv2.circle(mask_marked, largest_offset, 2, (255, 1, 1), 2)

    if circles is not None and largest_offset is not None:
        rot = angle((circles[0][0][0], circles[0][0][1]), largest_offset)

    return MarkedCircles(mask_marked, rot)

# ndarray to qpixmap
# https://gist.github.com/smex/5287589
def nd2qpixmap(nd: ndarray):
    gray_color_table = [QtGui.qRgb(i, i, i) for i in range(256)]

    if nd.dtype == np.uint8:
        nd = cv2.cvtColor(cv2.cvtColor(nd, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2RGB) # don't know why but this line fixes things

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