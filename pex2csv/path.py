##@package path
#This module contains all of the code defining the paths we use to represent
#different road segments. Each path is an iterable object so the path can be
#'walked' by asking for new x and y coordinates. Path.py is basically
#representing the geometry (i.e. points, line, vector) of each roadtype.
#The road classes are :class:'Bend', :class:'Curved', and :class:'Straight'.

import numpy as np
import bezier

##Class defining the iterable object used to define each useful geometry
class Path:

    ##The constructor
    #@param self The object pointer
    #@param dt A float. Step of the iteration
    #@param t1 A float. Start of the iteration
    def __init__(self, dt, t1):
        ##A float. Step of the iteration
        self.dt = dt
        ##A float. Start of the iteration
        self.t1 = t1
        ##A boolean. Used to stop the iteration
        self.flag = False
        ##An Integer. A factor that can be used to skip points in the path
        self.smooth_factor = 1

    ##An iterator
    #@param self The object pointer
    def __iter__(self):
        ##The current state of the iteration
        self.t = 0.0
        return self

    ##The method to return the next item in the sequence.
    #@param self The object pointer
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

    ##A method to return the starting point of the path
    #@param self The object pointer
    def getstart(self):
        return self.eval(0.0)

    ##A method to return the end point of the end point
    #@param self The object pointer
    def getend(self):
        return self.eval(int(self.t1 / self.dt) * self.dt)

##This path is represented with a part of a circle.
class Bend(Path):

    ##The constructor
    #@param self The object pointer
    #@param x0 A Float. The x coordinate of the starting point of the curve.
    #@param y0 A Float. The y coordinate of the starting point of the curve
    #@param a0 A Float. Global heading of the starting point.
    #@param da A Float. Heading of the endpoint relative to the curves' heading.
    #@param r A Float. Distance of the curve from the center of the circle used to represent the curve.
    def __init__(self, x0, y0, a0, da, r):
        ##A Float. Global heading of the starting point.
        self.a0 = a0 - np.sign(da) * np.pi / 2
        ##A Float. The x coordinate of the starting point of the curve.
        self.x0 = x0 - r * np.cos(self.a0)
        ##A Float. The y coordinate of the starting point of the curve.
        self.y0 = y0 - r * np.sin(self.a0)
        ##A Float. Heading of the endpoint relative to the curves' heading.
        self.da = da
        ##A Float. Distance of the curve from the center of the circle used to represent the curve.
        self.r = r
        Path.__init__(self, 1 / r, np.abs(da))

    ##A method to obtain the point at the step t.
    #Returns a tuple (x, y) representing the point
    #@param self The object pointer
    #@param t A Float. A step.
    def eval(self, t):
        return (self.x0 + self.r * np.cos(self.a0 + np.sign(self.da) * t),
                self.y0 + self.r * np.sin(self.a0 + np.sign(self.da) * t))

##This path is represented with an Euler Spiral
class Clothoid (Path):

    ##The constructor
    #@param self The object pointer
    #@param x0 A Float. The x coordinate of the starting point of the curve.
    #@param y0 A Float. The y coordinate of the starting point of the curve
    #@param h A Float. The initial heading of the path
    #@param C2 Constant Float describing the spiral. If R the radius of the spiral at the curvilinear abscissa L, R*L =C**2, and C2 = C**2
    #@param dir An integer. 1 if we calculate the spiral in the x direction, -1 if it is the spiral in the reverse x direction
    #@param Lstart A Float. The curvilinear abscissa at the strating point
    #@param Lend A Float. The curvilinear abscissa at the end point
    def __init__(self, x0, y0, h, C2, dir, Lstart, Lend) :
        ##A Float. The x coordinate of the starting point of the curve.
        self.x0 = x0
        ##A Float. The y coordinate of the starting point of the curve.
        self.y0 = y0
        ##A float. The step of the path
        self.dL = 1.0
        ##A Float
        self.h = h
        ##Constant Float describing the spiral. If R the radius of the spiral at the curvilinear abscissa L, R*L =C**2, and C2 = C**2
        self.C2 = C2
        ##The curvilinear abscissa at the strating point
        self.Lstart = Lstart
        ##The curvilinear abscissa at the end point
        self.Lend = Lend
        ##A list of points (float, float) defining the path
        self.values = [(x0,y0)]
        ##An integer. 1 if we calculate the spiral in the x direction, -1 if it is the spiral in the reverse x direction
        self.dir = dir
        Path.__init__(self,self.dL,abs(Lend-Lstart))

    ##A method to obtain the point at the curvilinear abscissa L.
    #Returns a tuple (x, y) representing the point
    #@param self The object pointer
    #@param L A Float. The curvilinear abscissa
    def eval(self, L):
        index = len(self.values) -1
        phi = (self.dir*L+self.Lstart)**2/(2*self.C2)
        x = self.values[index][0] + self.dir*np.cos(phi + self.h)
        y = self.values[index][1] + self.dir*np.sin(phi + self.h)
        self.values.append((x,y))
        return (self.values[index][0], self.values[index][1])


##This path is represented with a bezier curve.
class Curve(Path):

    ##The constructor
    #@param self The object pointer
    #@param xs A list of the x coordinate of the points defining the curve
    #@param ys A list of the y coordinate of the points defining the curve
    #@param offset A Float. Offset allowing to move the curve compared to the curve created if offset = 0
    def __init__(self, xs, ys, offset):
        ##A list of the x coordinate of the points defining the curve
        self.xs = xs
        ##A list of the y coordinate of the points defining the curve
        self.ys = ys
        ##A Float. Offset allowing to move the curve relative to the curve created if offset = 0
        self.offset = offset
        nodes = np.asfortranarray([xs, ys])
        ##A bezier.Curve object created with the points stored in xs and ys
        self.c = bezier.Curve(nodes, degree = 3)
        dt = 1.0 / self.c.length
        Path.__init__(self, dt, 1.0)

    ##This method returns the derivative of the cubic bezier curve with respect to t,
    ##and evaluate it at the value t
    #@param t A Float. parameter of the Bezier curve, which varies between 0 and 1
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

    ##This method returns a tuple representing the point (x, y) on the curve at the step t.
    #Returns a tuple (x, y) representing the point
    #@param self The object pointer
    #@param t A Float
    def eval(self, t):
        p = self.c.evaluate(t)
        x, y = p[0].item(), p[1].item()
        if self.offset == 0: return (x, y)
        dx, dy = self.dpdt(t)
        dir = np.arctan2(dy, dx)
        x += self.offset * np.sin(dir)
        y -= self.offset * np.cos(dir)
        return (x, y)

##This path is represented with a straight line.
class Straight(Path):

    ##The constructor
    #@param self The object pointer
    #@param x0 A Float. The x coordinate of the starting point of the line.
    #@param y0 A Float. The y coordinate of the starting point of the line.
    #@param h A Float. Global heading of the starting point.
    #@param l A Float. The lenght of the line
    def __init__(self, x0, y0, h, l):
        ##A Float. The x coordinate of the starting point of the line.
        self.x0 = x0
        ##A Float. The y coordinate of the starting point of the line.
        self.y0 = y0
        ##A Float. Global heading of the starting point.
        self.h = h
        Path.__init__(self, 1.0, l)

    ##This method returns the point on the curve at the step t.
    #Returns a tuple (x, y) representing the point
    #@param self The object pointer
    #@param t A Float
    def eval(self, t):
        return (self.x0 + t * np.cos(self.h),
                self.y0 + t * np.sin(self.h))
