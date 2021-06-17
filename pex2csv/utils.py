##@package utils
#This module is a mathematical toolbox
#It defines functions that will be useful for representing road types like bend, curve etc


import numpy as np

##A function that returns the position of the center of the circle that passes through point1 and point2 with a radius of r
#@param p1 A Tuple representing the point's coordinates
#@param p2 A Tuple representing the point's coordinates
#@param r A Float
def circles_from_p1p2r(p1, p2, r):
    #Check if r not 0
    if r == 0.0:
        raise ValueError('radius of zero')

    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2 - x1, y2 - y1
    q = np.sqrt(dx**2 + dy**2)
    x3, y3 = (x1 + x2)/2, (y1 + y2)/2
    d = np.sqrt(r**2 - (q / 2)**2)

    return (x3 + d*dy/q, y3 - d*dx/q)

##A function that returns the radius of the circle that passes through point 1 and point2, where the angle between (p1-centerofcircle) and (p2-centerofcircle) is the parameter angle.
#@param p1 A Tuple representing the point's coordinates
#@param p2 A Tuple representing the point's coordinates
#@param angle A Float
def radius_of_circle(p1, p2, angle):

    (x1, y1), (x2, y2) = p1, p2
    a = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return 0.5 * a / np.sin(0.5 * angle)

##A function that returns the distance between point1 and point2
#@param p1 A Tuple representing the point's coordinates
#@param p2 A Tuple representing the point's coordinates
def dist(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

##A function that returns the point of intersection of 2 lines L1 et L2
#@param L1 A list of 2 points representing the line
#@param L2 A list of 2 points representing the line
def Intersection_Lines(L1, L2):


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


        if round(a1,0) == round(a2,0):
            xinter = (L1[-1][0]+L2[0][0])/2
            yinter = (L1[-1][1]+L2[0][1])/2
        else:
            xinter = (b2-b1)/(a1-a2)
            yinter = a1*xinter+b1


    return (xinter,yinter)

##A function that returns the point of intersection of 2 circles C1 et C2
#@param C1 A list containing the coordinate of the center of the circle and its radius
#@param C2 A list containing the coordinate of the center of the circle and its radius
def Intersection_Circle(C1, C2):

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

##if a*x**2 + b*x + c is the polynom going through p1, p2 and p3, This function returns a, b and c
#@param p1 A Tuple representing the point's coordinates
#@param p2 A Tuple representing the point's coordinates
#@param p3 A Tuple representing the point's coordinates
def polynom(p1,p2,p3):

    if (p1==p2) or (p2==p3) or (p1==p3):
        return None
    else :
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]
        x3, y3 = p3[0], p3[1]
        A = np.array( [ [x1**2, x1, 1], [x2**2, x2, 1], [x3**2, x3, 1] ] )
        B = np.array( [ [y1], [y2], [y3] ] )
        Ainv = np.linalg.inv(A)
        Res = np.dot(Ainv,B)
        return (Res[0][0], Res[1][0], Res[2][0])

##A function that takes a polynom and 2 points. Returns the point on the polynom at a distance of 1 meter from p1
#@param poly A list of coefficients
#@param p1 A Tuple representing the point's coordinates
#@param p2 A Tuple representing the point's coordinates
def offset_point(poly,p1,p2):

    a, b, c = poly[0], poly[1], poly[2]
    x1 = p1[0]
    x2 = p2[0]
    p3 = p2
    if dist(p1,p2)<0.99 :
        return (p2)
    else :
        while (dist(p1,p3)<0.99) or (dist(p1,p3)>1.01):
            x3 = (x1+x2)/2
            y3 = a*x3**2 + b*x3 + c
            p3 = (x3,y3)
            if dist(p1,p3) > 1 :
                x2 = x3
            else :
                x1 = x3
    return(p3)
