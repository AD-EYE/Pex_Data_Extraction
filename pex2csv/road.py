import numpy as np
import bezier, math

class Path:
    def __init__(self, dt, t1):
        self.dt = dt
        self.t1 = t1

    def __iter__(self):
        self.t = 0.0
        return self

    def __next__(self):
        if self.t > self.t1:
            raise StopIteration
        ret = self.eval(self.t)
        self.t += self.dt
        return(ret)

class Curve(Path):
    def __init__(self, xs, ys):
        nodes = np.asfortranarray([xs, ys])
        self.c = bezier.Curve(nodes, degree = 3)
        dt = 1.0 / math.ceil(self.c.length)
        Path.__init__(self, dt, 1.0)

    def eval(self, t):
        p = self.c.evaluate(t)
        return (p[0].item(), p[1].item())
        
class Bend(Path):
    def __init__(self, x0, y0, r, ang):
        self.x0 = x0
        self.y0 = y0
        self.r = r
        len = abs(ang) * r
        dt = ang / math.ceil(len)
        Path.__init__(self, dt, len)

    def eval(self, t):
        if (t > 0):
            return (self.x0 + self.r * math.cos(-math.pi / 2 + t),
                    self.y0 + self.r * (1 + math.sin(-math.pi / 2 + t)))
        else:
            return (self.x0 + self.r * math.cos((math.pi/2) + t),
                    self.y0 - self.r * (1 + math.sin(-math.pi / 2 + t)))

class CurvedRoad:
    def __init__(self, x0, y0, rh, cp1, cp2, h, dx, dy):
        x_ = dx * math.cos(h) - dy * math.sin(h)
        y_ = dx * math.sin(h) + dy * math.cos(h)
        x1 = x0 + cp1 * math.cos(h)
        y1 = y0 + cp1 * math.sin(h)
        x2 = x0 + x_ - cp2 * math.cos(h + rh)
        y2 = y0 + y_ - cp2 * math.sin(h + rh)
        x3 = x0 + dx
        y3 = y0 + dy
        self.center = Curve([x0, x1, x2, x3], [y0, y1, y2, y3])

class BendRoad:
    def __init__(self, x0, y0, clr, rh):
        self.center = Bend(x0, y0, clr, rh)
