from path import *
import numpy as np
from collections import namedtuple

class BendRoad:
    def __init__(self, x0, y0, h, rh, clr, lw):
        self.c =  Bend( x0, y0, h, rh, clr)
        self.e1 = Bend( x0 + lw * np.cos(h + np.pi / 2),
                        y0 + lw * np.sin(h + np.pi / 2),
                        h, rh, clr - np.sign(rh) * lw)
        self.e2 = Bend( x0 - lw * np.cos(h + np.pi / 2),
                        y0 - lw * np.sin(h + np.pi / 2),
                        h, rh, clr + np.sign(rh) * lw)
        self.l1 = Bend( x0 + lw * np.cos(h + np.pi / 2) / 2,
                        y0 + lw * np.sin(h + np.pi / 2) / 2,
                        h, rh, clr - np.sign(rh) * lw / 2)
        self.l2 = Bend( x0 - lw * np.cos(h + np.pi / 2) / 2,
                        y0 - lw * np.sin(h + np.pi / 2) / 2,
                        h, rh, clr + np.sign(rh) * lw / 2)

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
        self.c = Curve([x0, x1, x2, x3], [y0, y1, y2, y3])

class RoundaboutRoad:
    def __init__(self, x0, y0, r, lw, chs):
        self.c  = Bend(x0, y0 - r, 0, 2 * np.pi, r)
        self.e1 = []
        self.e2 = Bend(x0, y0 - (r - lw), 0, 2 * np.pi, (r - lw))
        self.l1 = Bend(x0, y0 - (r - lw / 2), 0, 2 * np.pi, r - lw / 2)
        self.l2 = Bend(x0, y0 - (r + lw / 2), 0, 2 * np.pi, (r + lw / 2))

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

        self.x = []
        self.xl = []
        for ch in chs:
            (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, lw)
            self.x.append(Bend(x, y, h, a, rc))
            (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, -lw)
            self.x.append(Bend(x, y, h, a, rc))

            (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, lw/2)
            self.xl.append(Bend(x, y, h, a, rc))
            (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, -lw/2)
            self.xl.append(Bend(x, y, h, a, rc))

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

class StraightRoad:
    def __init__(self, x0, y0, h, l, lw):
        self.c =  Straight( x0, y0, h, l)
        self.e1 = Straight( x0 + lw * np.cos(h + np.pi / 2),
                            y0 + lw * np.sin(h + np.pi / 2), h, l)
        self.e2 = Straight( x0 - lw * np.cos(h + np.pi / 2),
                            y0 - lw * np.sin(h + np.pi / 2), h, l)
        self.l1 = Straight( x0 + lw * np.cos(h + np.pi / 2) / 2,
                            y0 + lw * np.sin(h + np.pi / 2) / 2, h, l)
        self.l2 = Straight( x0 - lw * np.cos(h + np.pi / 2) / 2,
                            y0 - lw * np.sin(h + np.pi / 2) / 2, h, l)
