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


    if L1[1][0] == L1[0][0]:    # x cst for L1

        if L2[1][1] == L2[0][1]:  #perpen
            xinter = L1[1][0]
            yinter = L2[1][1]

        elif L2[1][0] == L2[0][0]: # para
            xinter = (L1[len(L1)-1][0]+L2[0][0])/2
            yinter = (L1[len(L1)-1][1]+L2[0][1])/2
        else:

            a2 = (L2[1][1]-L2[0][1])/(L2[1][0]-L2[0][0])
            b2 = L2[1][1]- a2*L2[1][0]
            xinter = L1[1][0]
            yinter = a2*xinter+b2

    elif L2[1][0] == L2[0][0]:    # x cst for L2

        if L1[1][1] == L1[0][1]:  #perpen
            xinter = L2[1][0]
            yinter = L1[1][1]
        elif L1[1][0] == L1[0][0]:  # para
            xinter = (L1[len(L1)-1][0]+L2[0][0])/2
            yinter = (L1[len(L1)-1][1]+L2[0][1])/2
        else:
            a1 = (L1[1][1]-L1[0][1])/(L1[1][0]-L1[0][0])
            b1 = L1[1][1]- a1*L1[1][0]

            xinter = L2[1][0]
            yinter = a1*xinter+b1

    elif L1[1][1] == L1[0][1] : # y cst for L1

        if L2[1][1] == L2[0][1]:
            xinter = (L1[len(L1)-1][0]+L2[0][0])/2
            yinter = (L1[len(L1)-1][1]+L2[0][1])/2
        else :
            a2 = (L2[1][1]-L2[0][1])/(L2[1][0]-L2[0][0])
            b2 = L2[1][1]- a2*L2[1][0]
            yinter = L1[1][1]
            xinter = (yinter -b2)/a2

    elif L2[1][1] == L2[0][1] : # y cst for L1
        a1 = (L1[1][1]-L1[0][1])/(L1[1][0]-L1[0][0])
        b1 = L1[1][1]- a1*L1[1][0]
        yinter = L2[1][1]
        xinter = (yinter -b1)/a1

    else:

        a1 = (L1[1][1]-L1[0][1])/(L1[1][0]-L1[0][0])
        b1 = L1[1][1]- a1*L1[1][0]


        a2 = (L2[1][1]-L2[0][1])/(L2[1][0]-L2[0][0])
        b2 = L2[1][1]- a2*L2[1][0]


        if round(a1,1) == round(a2,1):
            xinter = (L1[-1][0]+L2[0][0])/2
            yinter = (L1[-1][1]+L2[0][1])/2
        else:
            xinter = (b2-b1)/(a1-a2)
            yinter = a1*xinter+b1


    return (xinter,yinter)


def Intersection_Circle(C1, C2):
    '''
    Return the point of intersection of 2 circles C1 et C2

    :param C1/C2: List containing the coordinate of the center of the circle and its radius
    :type C1/C2: [(xc,yc,r)]

    '''

    x1 = C1[0]
    y1 = C1[1]
    r1 = C1[2]
    x2 = C2[0]
    y2 = C2[1]
    r2 = C2[2]

    dx,dy = x2-x1,y2-y1
    d = np.sqrt(dx*dx+dy*dy)
    if d > r1+r2:
        print (1)
        return None # no solutions, the circles are separate
    if d < abs(r1-r2):
        print (2)
        return None # no solutions because one circle is contained within the other
    if d == 0 and r1 == r2:
        print (3)
        return None # circles are coincident and there are an infinite number of solutions

    a = (r1*r1-r2*r2+d*d)/(2*d)
    h = np.sqrt(r1*r1-a*a)
    xm = x1 + a*dx/d
    ym = y1 + a*dy/d
    xs1 = xm + h*dy/d
    xs2 = xm - h*dy/d
    ys1 = ym - h*dx/d
    ys2 = ym + h*dx/d

    return (xs1,ys1),(xs2,ys2)
