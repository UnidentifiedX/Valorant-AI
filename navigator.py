import numpy as np
from cv2 import Mat
from PyQt5 import QtCore
from PyQt5.QtCore import QRunnable
import time

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

from navigation_utils import grid_numpy, get_waypoints

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


    def run(self):
        while True:
            print("sussy C:")