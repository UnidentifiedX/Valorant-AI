import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QRunnable
import time

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

from navigation_utils import grid_numpy

class Navigator(QRunnable):
    def __init__(self, coordinates: tuple, map_grid: Grid):
        super(Navigator, self).__init__()

        self.map_grid = map_grid
        self.start_coords = coordinates

    def run(self):
        while True:
            print("sussy C:")