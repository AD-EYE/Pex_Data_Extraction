import math

class BendRoad(object):

    def __init__(self, x, y, radius, angle_rad):
        self.x = x
        self.y = y
        self.radius = radius
        self.angle_rad = angle_rad
        self.coords = []

        self.create_bend_road()

    def get_coords(self):
        return self.coords

    def calculate_coords(self, angle_rad):
        'TODO: fix algorithm'
        x2 = 0
        y2 = 0

        if(angle_rad > 0):
            x2 = self.x + self.radius * math.cos(-math.pi/2 + self.angle_rad)
            y2 = self.y + (self.radius + self.radius * math.sin(-math.pi/2 + self.angle_rad))
        else:
            x2 = self.x + self.radius * math.cos((math.pi/2) + self.angle_rad)
            y2 = self.y - (self.radius + self.radius * math.sin(-(math.pi/2) + self.angle_rad))

        return [x2, y2]

    def create_bend_road(self):
        arc_len = abs(self.angle_rad) * self.radius
        point_nbr = math.ceil(arc_len)
        self.coords.append([self.x, self.y])
        angle_incr = self.angle_rad/point_nbr
        angle = 0

        for _ in range(point_nbr):
            angle = angle + angle_incr
            self.coords.append(self.calculate_coords(angle))
