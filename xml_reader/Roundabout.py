import math
from Road import Road

class Roundabout(Road):
    def __init__(self, x, y, lane_width, radius, h_rad):
        self.x = x
        self.y = y
        self.lane_width = lane_width
        self.radius = radius
        self.h_rad = h_rad
        self.coords = []

        self.create_road()

    def create_road(self):
        road_length = self.radius * 2 * math.pi
        number_of_points = math.ceil(road_length)

        angle = 0
        angle_incr = 2 * math.pi/number_of_points

        for _ in range(number_of_points):
            self.coords.append(self.calculate_coords(angle))
            angle = angle + angle_incr

    def calculate_coords(self, angle):
        x1 = self.x * math.cos(angle)
        y1 = self.y * math.sin(angle)

        return [x1, y1]
