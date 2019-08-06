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

def Intersection_Lines(L1, L2):
    '''
    Return the point of intersection of 2 lines L1 et L2

    :param L1/L2: Tab of a point
    :type L1/L2: [(x,y)]

    '''

    if (L1[1][0]-L1[0][0]==0) and (L2[1][0]-L2[0][0]==0):
        xinter = L1[1][0]
        yinter = (L1[len(L1)][1]+L2[0][1]/2)
    elif ((L1[1][0]-L1[0][0]==0) and (L2[1][0]-L2[0][0]==0)):
        xinter= (L1[len(L1)][1]+L2[0][1])/2
        yinter= L1[1][1]
    elif L2[1][0]-L2[0][0]==0:
        xinter = L2[1][0]
        a1 = (L1[1][1]-L1[0][1])/(L1[1][0]-L1[0][0])
        b1 = L1[1][1]- a1*L1[1][0]
        yinter = a1*xinter+b1
    elif L1[1][0]-L1[0][0]==0:
        xinter = L1[1][0]
        a2 = (L2[1][1]-L2[0][1])/(L2[1][0]-L2[0][0])
        b2 = L2[1][1]- a2*L2[1][0]
    else :

        a1 = (L1[1][1]-L1[0][1])/(L1[1][0]-L1[0][0])
        b1 = L1[1][1]- a1*L1[1][0]

        a2 = (L2[1][1]-L2[0][1])/(L2[1][0]-L2[0][0])
        b2 = L2[1][1]- a2*L2[1][0]


        xinter = (b2-b1)/(a1-a2)
        yinter = a1*xinter+b1


    return (xinter,yinter)
