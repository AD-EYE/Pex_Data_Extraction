from path import *
import numpy as np
from collections import namedtuple

class Road:
    def __init__(self, id):
        self.id = id
        self.previous_road = -1
        self.next_road = -1
        self.isturned = False

    def getstart(self):
        return self.c.getstart()

    def getend(self):
        return self.c.getend()

    def turn_road(self):
        self.isturned = not self.isturned

class BendRoad(Road):
    def __init__(self, id, x0, y0, h, rh, clr, lw, nbr_of_lanes):
        Road.__init__(self, id)
        self.c =  Bend( x0, y0, h, rh, clr)
        self.e1 = Bend( x0 + lw * nbr_of_lanes / 2 * np.cos(h + np.pi / 2),
                        y0 + lw * nbr_of_lanes / 2 * np.sin(h + np.pi / 2),
                        h, rh, clr - np.sign(rh) * lw * nbr_of_lanes / 2)
        self.e2 = Bend( x0 - lw * nbr_of_lanes / 2 * np.cos(h + np.pi / 2),
                        y0 - lw * nbr_of_lanes / 2 * np.sin(h + np.pi / 2),
                        h, rh, clr + np.sign(rh) * lw * nbr_of_lanes / 2)
        self.l = []
        lwi = -(nbr_of_lanes - 1) * lw
        for _ in range(nbr_of_lanes):
            self.l.append(Bend( x0 + lwi * np.cos(h + np.pi / 2) / 2,
                                y0 + lwi * np.sin(h + np.pi / 2) / 2,
                               h, rh, clr - np.sign(rh) * lwi / 2))
            lwi += 2 * lw


class CurvedRoad(Road):
    def __init__(self, id, x0, y0, h, rh, cp1, cp2, dx, dy, lw, nbr_of_lanes):
        Road.__init__(self, id)
        x_ = dx * np.cos(h) - dy * np.sin(h)
        y_ = dx * np.sin(h) + dy * np.cos(h)
        x1 = x0 + cp1 * np.cos(h)
        y1 = y0 + cp1 * np.sin(h)
        x2 = x0 + x_ - cp2 * np.cos(h + rh)
        y2 = y0 + y_ - cp2 * np.sin(h + rh)
        x3 = x0 + x_
        y3 = y0 + y_
        xs = [x0, x1, x2, x3]
        ys = [y0, y1, y2, y3]
        self.c = Curve(xs, ys, 0)
        self.e1 = Curve(xs, ys, lw * nbr_of_lanes / 2)
        self.e2 = Curve(xs, ys, -lw * nbr_of_lanes / 2)

        self.l = []
        lwi = -(nbr_of_lanes - 1) * lw / 2
        for _ in range(nbr_of_lanes):
            self.l.append(Curve(xs, ys, lwi))
            lwi += lw

class RoundaboutRoad(Road):
    def __init__(self, id, x0, y0, r, lw, chs, nbr_of_lanes):
        Road.__init__(self, id)
        self.c  = Bend(x0, y0 - r, 0, 2 * np.pi, r)
        self.e1 = []
        self.e2 = Bend(x0, y0 - (r - lw), 0, 2 * np.pi, (r - lw))
        self.l = []
        lwi = -(nbr_of_lanes / 2) * lw
        for _ in range(nbr_of_lanes):
            self.l.append(Bend( x0,
                                y0 - (r - lwi / 2),
                                0, 2 * np.pi, r - lwi / 2))
            lwi += lw * 2

        offset = np.pi / 8
        h = []
        rh = []
        h.append(chs[0] + offset + np.pi / 2)

        for i in range(1, len(chs)):
            h.append(chs[i] + offset + np.pi / 2)
            rh.append(chs[i] - offset - (chs[i-1] + offset))

        rh.append(chs[0] + np.pi / 2 - offset + 2 * np.pi - h[len(h) - 1])
        for i in range(len(h)):
            x1 = x0 + (r + lw) * np.cos(chs[i] + offset)
            y1 = y0 + (r + lw) * np.sin(chs[i] + offset)
            r1 = r + lw
            self.e1.append(Bend(x1, y1, h[i], rh[i], r1))

        self.exit_lanes = []
        for ch in chs:
            self.exit_lanes.append(ExitLane(id, x0, y0, r, lw, ch, nbr_of_lanes))

class ExitLane(Road):
    def __init__(self, id, x0, y0, r, lw, ch, nbr_of_lanes):
        Road.__init__(self, id)
        self.x = x0
        self.y = y0
        self.r = r
        self.ch = ch
        self.lw = lw
        (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, lw)
        self.e1 = Bend(x, y, h, a, rc)
        (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, -lw)
        self.e2 = Bend(x, y, h, a, rc)

        self.l = []
        (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, lw/2)
        self.l.append(Bend(x, y, h, a, rc))
        (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, -lw/2)
        self.l.append(Bend(x, y, h, a, rc))

        self.c = []

    def getstart(self):
        return (self.x, self.y)

    def getend(self):
        return (self.x + (self.r + 2 * self.lw) * np.cos(self.ch),
                self.y + (self.r + 2 * self.lw) * np.sin(self.ch))

    def circles_from_p1p2r(self, p1, p2, r):
        Circle = Cir = namedtuple('Circle', 'x, y')

        if r == 0.0:
            raise ValueError('radius of zero')
        (x1, y1), (x2, y2) = p1, p2
        dx, dy = x2 - x1, y2 - y1
        q = np.sqrt(dx**2 + dy**2)

        x3, y3 = (x1 + x2)/2, (y1 + y2)/2
        d = np.sqrt(r**2 - (q / 2)**2)
        return Cir(x = x3 + d*dy/q,
                 y = y3 - d*dx/q)

    def get_exit_lane(self, x0, y0, lw, r, ch, ld):
        sign = np.sign(ld)
        ld = abs(ld)

        x1 = x0 + (r + lw + 3.5) * np.cos(ch)
        y1 = y0 + (r + lw + 3.5) * np.sin(ch)

        x2 = x1 + ld * np.cos(ch - sign * np.pi / 2)
        y2 = y1 + ld * np.sin(ch - sign * np.pi / 2)

        xc1 = x0 + (r + ld) * np.cos(ch - sign * np.pi / 8)
        yc1 = y0 + (r + ld) * np.sin(ch - sign * np.pi / 8)

        a = np.sqrt((x2 - xc1)**2 + (y2 - yc1)**2)
        rc = 0.5 * a / np.sin(0.5 * np.pi/3)

        Pt = namedtuple('Pt', 'x, y')
        p1 = Pt(xc1, yc1)
        p2 = Pt(x2, y2)

        cc1 = 0
        if(sign > 0):
            cc1 = self.circles_from_p1p2r(p1, p2, rc)
        else:
            cc1 = self.circles_from_p1p2r(p2, p1, rc)

        (x, y) = cc1
        h = np.arctan2(y - y2, x - x2) - sign * np.pi / 2
        return (x2, y2, h, sign * np.pi / 3, rc)

class StraightRoad(Road):
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes):
        Road.__init__(self)
        self.c =  Straight( x0, y0, h, l)
        self.e1 = Straight( x0 + lw * np.cos(h + np.pi / 2),
                            y0 + lw * np.sin(h + np.pi / 2), h, l)
        self.e2 = Straight( x0 - lw * np.cos(h + np.pi / 2),
                            y0 - lw * np.sin(h + np.pi / 2), h, l)
        self.l = []
        lwi = -(nbr_of_lanes / 2) * lw
        for _ in range(nbr_of_lanes):
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) / 2,
                                    y0 + lwi * np.sin(h + np.pi / 2) / 2,
                                    h, l))
            lwi += lw * 2
