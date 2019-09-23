'''This module is a mathematical toolbox
It define functon that will be usefull for representing road like bend, curve etc
'''

import numpy as np

def circles_from_p1p2r(p1, p2, r):
    '''
    Return the position of the center of the circle that passes through point 1 and point2 with a radius of r

    :param p1/p2: coordinate of a point
    :type p1/p2: (x,y)

    :param r: radius of the circle
    :type r: Float

    '''
    #Check if r not 0
    if r == 0.0:
        raise ValueError('radius of zero')

    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2 - x1, y2 - y1
    q = np.sqrt(dx**2 + dy**2)
    x3, y3 = (x1 + x2)/2, (y1 + y2)/2
    d = np.sqrt(r**2 - (q / 2)**2)

    return (x3 + d*dy/q, y3 - d*dx/q)

def radius_of_circle(p1, p2, angle):
    '''
    Return the radius of the circle that passes through point 1 and point2, with the angle between (p1-centerofcircle) and (p2-centerofcircle)
    is the parameter angle.

    :param p1/p2: coordinate of a point
    :type p1/p2: (x,y)

    :param angle: angle between (p1-centerofcircle) and (p2-centerofcircle)
    :type angle: Float

    '''
    (x1, y1), (x2, y2) = p1, p2
    a = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return 0.5 * a / np.sin(0.5 * angle)

def dist(p1, p2):
    '''
    Return the distance between point1 and point2

    :param p1/p2: coordinate of a point
    :type p1/p2: (x,y)

    '''
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
