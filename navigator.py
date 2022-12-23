import numpy as np
import cv2
from cv2 import Mat
import math
from PyQt5 import QtCore
from PyQt5.QtCore import QRunnable
import time

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

from navigation_utils import grid_numpy, get_waypoints, MarkedCircles

class Navigator(QRunnable):
    def __init__(self, coordinates: tuple, map_img: Mat):
        super(Navigator, self).__init__()

        self.map_img = map_img
        self.start_coords = coordinates

        self.set_movements_and_waypoints()

    def set_movements_and_waypoints(self):
        matrix = self.map_img
        grid = Grid(matrix=matrix)

        a = np.array(matrix, dtype=bool)
        avail_spaces = np.argwhere(a)

        end_rand = avail_spaces[np.random.choice(avail_spaces.shape[0], 1, replace=False)][0] # [y, x]

        start = grid.node(self.start_coords[0], self.start_coords[1])
        end = grid.node(end_rand[1], end_rand[0])

        finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
        path, runs = finder.find_path(start, end, grid)

        self.waypoints = get_waypoints(path)

    # https://github.com/TheRabbitProgram/Valorant-AimBot-and-Navigation-Bot/blob/main/Navigation/MapCaptureTest.py
    @classmethod
    def scan_circle(self, img, radius, x_offset, y_offset):
        for theta in range(360):
            x = int(radius * math.cos(theta)) + x_offset
            y = int(radius * math.sin(theta)) + y_offset

            if img[y, x] != 0:
                return x, y
        return None

    @classmethod
    def map_range(self, value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)

    @classmethod
    def angle(self, point_a, point_b):
        deg = math.degrees(math.atan2((point_b[1] - point_a[1]), (point_b[0] - point_a[0])))
        if deg < 0:
            deg = self.map_range(deg, -0, -180, 0, 180)
        else:
            deg = self.map_range(deg, 0, 180, 360, 180)
        if deg == 360:
            deg = 0

        return deg

    @classmethod
    def mark_circles(self, mask: Mat):
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
                largest_offset = Navigator.scan_circle(mask, r, circles[0][0][0], circles[0][0][1])
                if largest_offset is None:
                    r -= 1
                else:
                    break

            mask_marked = cv2.circle(mask_marked, largest_offset, 2, (255, 1, 1), 2)

        if circles is not None and largest_offset is not None:
            rot = self.angle((circles[0][0][0], circles[0][0][1]), largest_offset)

        self.rotation = rot
        self.position = largest_offset
        
        return MarkedCircles(mask_marked, rot, largest_offset)


    def run(self):
        while True:
            # print(f"{self.position[0]}X {self.position[1]}Y")
            print(self.position)