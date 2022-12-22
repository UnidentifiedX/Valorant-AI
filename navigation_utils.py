import cv2
from cv2 import Mat
from enum import Enum
import math
import numpy as np
from numpy import ndarray
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
import pydirectinput
from PyQt5 import QtGui
import time

class MarkedCircles:
    def __init__(self, mask_marked: Mat, rot: float, pos: tuple):
        self.mask_marked = mask_marked
        self.rotation = rot
        self.position = pos


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
    largest_offset = None

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

    return MarkedCircles(mask_marked, rot, largest_offset)

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

def grid_numpy(self: Grid, start, end, path = None, path_colour = [255, 0, 0]):
    data = []
    for y in range(len(self.nodes)):
        line = []
        for x in range(len(self.nodes[y])):
            node = self.nodes[y][x]
            if path and ((node.x, node.y) in path or node in path):
                line.append([255, 0, 0])
            elif node == start:
                line.append([255, 0, 0])
            elif node == end:
                line.append([0, 0, 255])
            elif node.walkable:
                # empty field
                line.append([255, 255, 255])
            else:
                line.append([0, 0, 0])  # blocked field

        data.append(line)
    
    return np.array(data, dtype=np.uint8)

class NavigationDirection(Enum):
    FORWARDS = 0,
    BACKWARDS = 1,
    LEFT = 2,
    RIGHT = 3

class Waypoint:
    def __init__(self, x, y, direction_to_rotate: NavigationDirection):
        self.x = x
        self.y = y
        self.direction_to_rotate: NavigationDirection = direction_to_rotate
        

def get_waypoints(path: list[tuple]):
    waypoints: list[Waypoint] = []

    for i in range(1, len(path)):
        # ↑
        if path[i - 1][1] > path[i][1] and (len(waypoints) == 0 or waypoints[-1].direction_to_rotate != NavigationDirection.FORWARDS):
            waypoints.append(Waypoint(path[i - 1][0], path[i - 1][1], NavigationDirection.FORWARDS))
        # ↓
        elif path[i - 1][1] < path[i][1] and (len(waypoints) == 0 or waypoints[-1].direction_to_rotate != NavigationDirection.BACKWARDS):
            waypoints.append(Waypoint(path[i - 1][0], path[i - 1][1], NavigationDirection.BACKWARDS))
        # ←
        elif path[i - 1][0] > path[i][0] and (len(waypoints) == 0 or waypoints[-1].direction_to_rotate != NavigationDirection.LEFT):
            waypoints.append(Waypoint(path[i - 1][0], path[i - 1][1], NavigationDirection.LEFT))
        # →
        elif path[i - 1][0] < path[i][0] and (len(waypoints) == 0 or waypoints[-1].direction_to_rotate != NavigationDirection.RIGHT):
            waypoints.append(Waypoint(path[i - 1][0], path[i - 1][1], NavigationDirection.RIGHT))

    return waypoints