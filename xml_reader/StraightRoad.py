import math
from Road import Road

class StraightRoad(Road):
    def __init__(self, x, y, h_rad, length):
        self.x = x
        self.y = y
        self.h_rad = h_rad
        self.coords = []
        self.length = length

        self.create_road()

    def create_road(self):
        number_of_points = math.ceil(self.length)
        start = 0
        incr = self.length/number_of_points

        for _ in range(number_of_points):
            self.coords.append(self.calculate_coord(start))
            start = start + incr

    def calculate_coord(self, length):
        x1 = self.x + length * math.cos(self.h_rad)
        y1 = self.x + length * math.sin(self.h_rad)

        return [x1, y1]

