from path import *
import numpy as np

class BendRoad:
    def __init__(self, x0, y0, h, rh, clr):
        self.center = Bend(x0, y0, h, rh, clr)

class CurvedRoad:
    def __init__(self, x0, y0, h, rh, cp1, cp2, dx, dy):
        x_ = dx * np.cos(h) - dy * np.sin(h)
        y_ = dx * np.sin(h) + dy * np.cos(h)
        x1 = x0 + cp1 * np.cos(h)
        y1 = y0 + cp1 * np.sin(h)
        x2 = x0 + x_ - cp2 * np.cos(h + rh)
        y2 = y0 + y_ - cp2 * np.sin(h + rh)
        x3 = x0 + dx
        y3 = y0 + dy
        self.center = Curve([x0, x1, x2, x3], [y0, y1, y2, y3])

class RoundaboutRoad:
    def __init__(self, x0, y0, r):
        self.center = Roundabout(x0, y0, r)

class StraightRoad:
    def __init__(self, x0, y0, h, l):
        self.center = Straight(x0, y0, h, l)
