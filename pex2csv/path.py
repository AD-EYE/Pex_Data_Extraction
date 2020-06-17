'''This module contains all of the code defining the paths we use to represent
different road segments. Each path is an iterable object so the path can be
'walked' by asking for new x and y coordinates. Path.py is basically
representing the geometry (i.e. points, line, vector) of each roadtype.

The road classes are :class:'Bend', :class:'Curved', and :class:'Straight'.
'''
import numpy as np
import bezier

class Path:
    '''
    Class defining the iterable object use to define each usefull geometry

    :param dt: Step of the iteration
    :type dt: Float

    :param t1: Start of the iteration
    :type t1: Float

    '''

    def __init__(self, dt, t1):
        self.dt = dt
        self.t1 = t1
        self.flag = False
        self.smooth_factor = 1

    def __iter__(self):
        self.t = 0.0
        return self

    def __next__(self):
        if self.t == self.t1:
            self.flag = True
        if self.t > self.t1 and self.flag == False:
            self.flag = True
            ret = self.eval(self.t1*self.smooth_factor)
            self.t += self.dt
            return(ret)
        if self.t > self.t1 and self.flag == True:
            raise StopIteration
        ret = self.eval(self.t)
        self.t += self.dt
        return(ret)

    def getstart(self):
        return self.eval(0.0)

    def getend(self):
        return self.eval(int(self.t1 / self.dt) * self.dt)

class Bend(Path):
    '''
    This path is represented with a part of a circle.

    :param x0: The x coordinate of the starting point of the curve.
    :type x0: Float

    :param y0: The y coordinate of the starting point of the curve
    :type y0: Float

    :param a0: Global heading of the starting point.
    :type a0: Float

    :param da: Heading of the endpoint relative to the curves' heading.
    :type da: Float

    :param r: Distance of the curve from the center of the circle used to represent the curve.
    :type r: Float

    '''
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
    '''
    This path is represented with a bezier curve.

    :param xs: Tab of the x coordinate of the points defining the curve
    :type xs: [Float]

    :param ys: Tab of the y coordinate of the points defining the curve
    :type ys: [Float]

    :param offset: Offeset allowing to move the curve compare to the curve created if offset = 0
    :type offset: Float

    '''
    def __init__(self, xs, ys, offset):
        self.xs, self.ys = xs, ys
        self.offset = offset
        nodes = np.asfortranarray([xs, ys])
        self.c = bezier.Curve(nodes, degree = 3)
        dt = 1.0 / self.c.length
        Path.__init__(self, dt, 1.0)

    def dpdt(self, t):
        dx =   -3 * self.xs[0] * (1 - t) ** 2 + \
                3 * self.xs[1] * (1 - t) ** 2 - \
                6 * self.xs[1] * (1 - t) * t + \
                6 * self.xs[2] * (1 - t) * t - \
                3 * self.xs[2] * t ** 2 + \
                3 * self.xs[3] * t ** 2
        dy =   -3 * self.ys[0] * (1 - t) ** 2 + \
                3 * self.ys[1] * (1 - t) ** 2 - \
                6 * self.ys[1] * (1 - t) * t + \
                6 * self.ys[2] * (1 - t) * t - \
                3 * self.ys[2] * t ** 2 + \
                3 * self.ys[3] * t ** 2
        return (dx, dy)

    def eval(self, t):
        p = self.c.evaluate(t)
        x, y = p[0].item(), p[1].item()
        if self.offset == 0: return (x, y)
        dx, dy = self.dpdt(t)
        dir = np.arctan2(dy, dx)
        x += self.offset * np.sin(dir)
        y -= self.offset * np.cos(dir)
        return (x, y)

class Straight(Path):
    '''
    This path is represented with a straight line.

    :param x0: The x coordinate of the starting point of the line.
    :type x0: Float

    :param y0: The y coordinate of the starting point of the line.
    :type y0: Float

    :param h: Global heading of the starting point.
    :type  h: Float

    :param l: Length of the line.
    :type l: Float

    '''
    def __init__(self, x0, y0, h, l):
        self.x0 = x0
        self.y0 = y0
        self.h = h
        Path.__init__(self, 1.0, l)

    def eval(self, t):
        return (self.x0 + t * np.cos(self.h),
                self.y0 + t * np.sin(self.h))
