from path import *
import numpy as np
from utils import *

class Road:
    def __init__(self, id):
        self.id = id
        self.previous_road = -1
        self.next_road = -1
        self.isturned = False

    def getstart(self):
        return self.c[0].getstart()

    def getend(self):
        return self.c[0].getend()

    def turn_road(self):
        self.isturned = not self.isturned

class BendRoad(Road):
    def __init__(self, id, x0, y0, h, rh, clr, lw, nbr_of_lanes):
        Road.__init__(self, id)
        self.c = [Bend( x0, y0, h, rh, clr)]
        self.e1 = []
        self.e2 = []
        self.e1.append(Bend( x0 + lw * nbr_of_lanes / 2 * np.cos(h + np.pi / 2),
                        y0 + lw * nbr_of_lanes / 2 * np.sin(h + np.pi / 2),
                        h, rh, clr - np.sign(rh) * lw * nbr_of_lanes / 2))
        self.e2.append(Bend( x0 - lw * nbr_of_lanes / 2 * np.cos(h + np.pi / 2),
                        y0 - lw * nbr_of_lanes / 2 * np.sin(h + np.pi / 2),
                        h, rh, clr + np.sign(rh) * lw * nbr_of_lanes / 2))
        self.l = []
        lwi = (nbr_of_lanes - 1) * lw
        for _ in range(nbr_of_lanes):
            self.l.append(Bend( x0 + lwi * np.cos(h + np.pi / 2) / 2,
                                y0 + lwi * np.sin(h + np.pi / 2) / 2,
                               h, rh, clr - np.sign(rh) * lwi / 2))
            lwi -= 2 * lw


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
        self.c = [Curve(xs, ys, 0)]
        self.e1 = []
        self.e2 = []
        self.e1.append(Curve(xs, ys, lw * nbr_of_lanes / 2))
        self.e2.append(Curve(xs, ys, -lw * nbr_of_lanes / 2))

        self.l = []
        lwi = -(nbr_of_lanes - 1) * lw / 2
        for _ in range(nbr_of_lanes):
            self.l.append(Curve(xs, ys, lwi))
            lwi += lw

class RoundaboutRoad(Road):
    def __init__(self, id, x0, y0, r, lw, chs, nbr_of_lanes):
        Road.__init__(self, id)
        self.c  = [Bend(x0, y0 - r, 0, 2 * np.pi, r)]
        self.e1 = []
        self.e2 = []
        self.e2.append(Bend(x0, y0 - (r - lw), 0, 2 * np.pi, (r - lw)))
        self.l = []
        lwi = (nbr_of_lanes / 2) * lw
        for _ in range(nbr_of_lanes):
            self.l.append(Bend( x0,
                                y0 - (r - lwi / 2),
                                0, 2 * np.pi, r - lwi / 2))
            lwi -= lw * 2

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
        self.c = []
        self.e1 = []
        self.e2 = []
        self.l = []

        (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, lw)
        self.e1.append(Bend(x, y, h, a, rc))
        (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, -lw)
        self.e2.append(Bend(x, y, h, a, rc))

        (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, lw/2)
        self.l.append(Bend(x, y, h, a, rc))
        (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, -lw/2)
        self.l.append(Bend(x, y, h, a, rc))

    def getstart(self):
        return (self.x, self.y)

    def getend(self):
        return (self.x + (self.r + 2 * self.lw) * np.cos(self.ch),
                self.y + (self.r + 2 * self.lw) * np.sin(self.ch))

    def get_exit_lane(self, x0, y0, lw, r, ch, ld):
        sign = np.sign(ld)
        ld = abs(ld)

        x1 = x0 + (r + lw + 3.5) * np.cos(ch)
        y1 = y0 + (r + lw + 3.5) * np.sin(ch)

        x2 = x1 + ld * np.cos(ch - sign * np.pi / 2)
        y2 = y1 + ld * np.sin(ch - sign * np.pi / 2)

        xc1 = x0 + (r + ld) * np.cos(ch - sign * np.pi / 8)
        yc1 = y0 + (r + ld) * np.sin(ch - sign * np.pi / 8)

        rc = radius_of_circle((x2, y2), (xc1, yc1), np.pi/3)

        p1 = (xc1, yc1)
        p2 = (x2, y2)

        if(sign > 0):
            cc1 = circles_from_p1p2r(p1, p2, rc)
        else:
            cc1 = circles_from_p1p2r(p2, p1, rc)

        (x, y) = cc1
        h = np.arctan2(y - y2, x - x2) - sign * np.pi / 2
        return (x2, y2, h, sign * np.pi / 3, rc)

class StraightRoad(Road):
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes):
        Road.__init__(self, id)
        self.c = []
        self.e1 = []
        self.e2 = []
        self.l = []
        self.c.append(Straight( x0, y0, h, l))
        self.e1.append(Straight( x0 + lw * np.cos(h + np.pi / 2),
                                y0 + lw * np.sin(h + np.pi / 2), h, l))
        self.e2.append(Straight( x0 - lw * np.cos(h + np.pi / 2),
                                y0 - lw * np.sin(h + np.pi / 2), h, l))
        self.l = []
        lwi = (nbr_of_lanes / 2) * lw
        for _ in range(nbr_of_lanes):
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) / 2,
                                    y0 + lwi * np.sin(h + np.pi / 2) / 2,
                                    h, l))
            lwi -= lw * 2

class XCrossRoad(Road):
    def __init__(self, id, x0, y0, h, r, lw, chs, len_till_stop, nbr_of_lanes):
        Road.__init__(self, id)
        self.c = []
        self.e1 = []
        self.e2 = []
        self.l = []
        self.segments = []
        self.x = x0
        self.y = y0

        for ch in chs:
            self.segments.append(XSegment(id, x0, y0, h, r, lw, ch, len_till_stop, nbr_of_lanes))

    def getstart(self):
        return (self.x, self.y)

    def getend(self):
        return (self.x, self.y)

class XSegment(Road):
    def __init__(self, id, x0, y0, h, r, lw, ch, len_till_stop, nbr_of_lanes):
        Road.__init__(self, id)
        self.c = []
        self.e1 = []
        self.e2 = []
        self.l = []
        self.lturn = []
        self.rturn = []
        self.straight = []

        self.__create_center(x0, y0, r, ch + h)
        self.__create_edges(x0, y0, r, lw, ch + h, len_till_stop)
        self.__create_turns(x0, y0, lw, r - len_till_stop, ch + h, nbr_of_lanes)
        self.__create_lanes(x0, y0, r, lw, ch + h, nbr_of_lanes)

    def __create_lanes(self, x0, y0, r, lw, h, nbr_of_lanes):
        x = x0 + r * np.cos(h)
        y = y0 + r * np.sin(h)
        lwi = -(nbr_of_lanes / 2) * lw

        for _ in range(nbr_of_lanes):
            x1 = x + lwi * np.cos(h + np.pi / 2) / 2
            y1 = y + lwi * np.sin(h + np.pi / 2) / 2
            self.l.append(Straight(x1, y1, h - np.pi, r))
            lwi += lw * 2

    def __create_edges(self, x0, y0, r, lw, h, len_till_stop):
        x = x0 + r * np.cos(h)
        y = y0 + r * np.sin(h)

        self.e1.append(Straight(x + lw * np.cos(h + np.pi / 2),
                              y + lw * np.sin(h + np.pi / 2),
                              h - np.pi,
                              len_till_stop))
        self.e2.append(Straight(x - lw * np.cos(h + np.pi / 2),
                               y - lw * np.sin(h + np.pi / 2),
                               h - np.pi,
                               len_till_stop))

        x2 = x + lw * np.cos(h + np.pi / 2)
        y2 = y + lw * np.sin(h + np.pi / 2)
        x3 = x2 + len_till_stop * np.cos(h + np.pi)
        y3 = y2 + len_till_stop * np.sin(h + np.pi)
        self.e1.append(Bend(x3, y3, h + np.pi, -np.pi / 2, 2))

    def __create_turns(self, x0, y0, lw, r, h, nbr_of_lanes):
        lwi = -(nbr_of_lanes / 2) * lw
        lturn = self.__get_left_turn(x0, y0, lwi, r, h)
        rturn = self.__get_right_turn(x0, y0, lwi, r, h)
        self.lturn.append(lturn)
        self.rturn.append(rturn)

    def __create_center(self, x0, y0, r, h):
        x = x0 + r * np.cos(h)
        y = y0 + r * np.sin(h)
        self.c.append(Straight(x, y, h - np.pi, r))

    def __get_right_turn(self, x0, y0, lw, l, h):
        x = x0 - lw * np.cos(h + np.pi / 2) / 2
        y = y0 - lw * np.sin(h + np.pi / 2) / 2

        x1 = x + l * np.cos(h)
        y1 = y + l * np.sin(h)

        x = x0 - lw * np.cos(h) / 2
        y = y0 - lw * np.sin(h) / 2

        x2 = x + l * np.cos(h + np.pi / 2)
        y2 = y + l * np.sin(h + np.pi / 2)

        p1 = (x1, y1)
        p2 = (x2, y2)
        rc = radius_of_circle(p1, p2, np.pi / 2)
        return Bend(x1, y1, h + np.pi, -np.pi / 2, rc)

    def __get_left_turn(self, x0, y0, lw, l, h):
        # middle of road
        x = x0 - lw * np.cos(h + np.pi / 2) / 2
        y = y0 - lw * np.sin(h + np.pi / 2) / 2
        # start of turn
        x1 = x + l * np.cos(h)
        y1 = y + l * np.sin(h)

        x = x0 + lw * np.cos(h) / 2
        y = y0 + lw * np.sin(h) / 2

        x2 = x + l * np.cos(h - np.pi / 2)
        y2 = y + l * np.sin(h - np.pi / 2)

        p1 = (x1, y1)
        p2 = (x2, y2)
        rc = radius_of_circle(p1, p2, np.pi / 2)
        return Bend(x1, y1, h + np.pi, np.pi / 2, rc)

    def getstart(self):
        return self.c[0].getend()

    def getend(self):
        return self.c[0].getstart()
