import math
import bezier
import numpy as np
from Road import Road

class CurvedRoad(Road):

    def __init__(self, x, y, rh_rad, cp1, cp2, h_rad, x_off, y_off):
        self.x = x
        self.y = y
        self.rh_rad = rh_rad
        self.cp1 = cp1
        self.cp2 = cp2
        self.h_rad = h_rad
        self.x_off = x_off
        self.y_off = y_off
        self.points = []
        self.coords = []

        self.create_points()
        self.calculate_coords()

    def calculate_coords(self):
        nodes = np.asfortranarray([
            [self.points[0][0], self.points[1][0], self.points[2][0], self.points[3][0]],
            [self.points[0][1], self.points[1][1], self.points[2][1], self.points[3][1]],
        ])
        curve = bezier.Curve(nodes, degree = 3)
        curve_length = curve.length
        number_of_points = math.ceil(curve_length)
        incr = 1.0/number_of_points
        start = 0.0
        for _ in range(number_of_points):
            c = curve.evaluate(start)
            self.coords.append([c[0].item(),c[1].item()])
            start = start + incr

    def create_points(self):
        x_marked = self.x_off * math.cos(self.h_rad) - self.y_off * math.sin(self.h_rad)
        y_marked = self.x_off * math.sin(self.h_rad) + self.y_off  * math.cos(self.h_rad)

        x1 = self.x + self.cp1 * math.cos(self.h_rad)
        y1 = self.y + self.cp1 * math.sin(self.h_rad)

        x2 = self.x + x_marked - self.cp2 * math.cos(self.h_rad + self.rh_rad)
        y2 = self.y + y_marked - self.cp2 * math.sin(self.h_rad + self.rh_rad)

        x3 = self.x + self.x_off
        y3 = self.y + self.y_off

        self.points.append([self.x,self.y])
        self.points.append([x1,y1])
        self.points.append([x2,y2])
        self.points.append([x3,y3])

