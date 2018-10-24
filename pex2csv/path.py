import numpy as np
import bezier

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

class Bend(Path):
    def __init__(self, x0, y0, a0, da, r):
        self.a0 = a0 - np.sign(da) * np.pi / 2
        self.x0 = x0 - r * np.cos(self.a0)
        self.y0 = y0 - r * np.sin(self.a0)
        self.da = da
        self.r = r
        Path.__init__(self, 1 / r, np.abs(da))

    def eval(self, t):
        return (self.x0 + self.r * np.cos(self.a0 + np.sign(self.da) * t),
                self.y0 + self.r * np.sin(self.a0 + np.sign(self.da) * t))

class Curve(Path):
    def __init__(self, xs, ys):
        nodes = np.asfortranarray([xs, ys])
        self.c = bezier.Curve(nodes, degree = 3)
        dt = 1.0 / np.ceil(self.c.length)
        Path.__init__(self, dt, 1.0)

    def eval(self, t):
        p = self.c.evaluate(t)
        return (p[0].item(), p[1].item())

class Roundabout(Path):
    def __init__(self, x0, y0, r, lw):
        self.x0 = x0
        self.y0 = y0
        self.r = r + lw
        Path.__init__(self, 1 / r, 2 * np.pi)

    def eval(self, t):
        return (self.x0 + self.r * np.cos(t),
                self.y0 + self.r * np.sin(t))

class Straight(Path):
    def __init__(self, x0, y0, h, l):
        self.x0 = x0
        self.y0 = y0
        self.h = h
        Path.__init__(self, 1.0, l)

    def eval(self, t):
        return (self.x0 + t * np.cos(self.h),
                self.y0 + t * np.sin(self.h))
