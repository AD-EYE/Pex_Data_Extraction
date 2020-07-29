'''This module contains all of the code defining the structure of different
road segments. By taking initial values from the parser the classes calculate a
mathematical definition of the road type. So We use the geometry created in
path.py to define the different roadtype (ex: we use Bend type to create Roundabout)

The road classes :class:'BendRoad', :class:'CurvedRoad', :class:'StraightRoad',
:class:'RoundaboutRoad', and :class:'XCrossing' all have class variables that represent roads.

'''
from path import *
import numpy as np
from utils import *


class Road:
    '''This is the interface class for all the road types. Every road has certain things in common such as a center, edges, lanes and SpeedLimit/RefSpeed.

        :param id: represent the ID of the road (Bendroad, StraightRoad...).The exact ID can be found in the pex file.
        :type ps: string

        :param c: Tab of points defining the center of the road.
        :type c: [(x,t)]

        :param e1/e2: Tab of points defining the edges of the road.
        :type e1/e2: [(x,t)]

        :param l: Tab of points defining a lane of the road.
        :type l: [(x,t)]

        :param SpeedLimit/RefSpeed: Define the speed limit / the speed reference on the road.
        :type SpeedLimit/RefSpeed: Float

        param SpeedProfil: Tab of Float defining the speed profil (Speed Limit per RoadType)
        :type SpeedLimit/RefSpeed: [Float]


    '''
    def __init__(self, id):
        self.id = id
        self.c = []
        self.e1 = []
        self.e2 = []
        self.l = []
        self.stopline = []
        self.crosswalk = []
        self.previous_road = -1
        self.next_road = -1
        self.SpeedLimit = 1
        self.RefSpeed = 1
        self.SpeedProfil = self.SpeedProfil = [70,40,70,70,20,90,20,70,70,50]

    def getstart(self):
        '''This method returns the starting coordinates of the road's center path.
        .. note:: Some road segments might not have a starting point, for example the roundabout road. Those segments will have to override this function accordingly.
        :returns (Float, Float)
        '''
        return self.c[0].getstart()

    def getend(self):
        '''This method returns the last coordinates of the road's center path.
        .. note:: Some road segments might not have an endpoint, for example the roundabout road. Those segments will have to override this function accordingly.
        :returns (Float, Float)
        '''
        return self.c[0].getend()

class BendRoad(Road):
    '''
    This a representation of the bend road in Prescan.

    :param id: Unique id.
    :type id: String

    :param x0: The x coordinate of the starting point of the segment
    :type x0: Float

    :param y0: The y coordinate of the starting point of the segment
    :type y0: Float

    :param h: Global heading of the segment at the starting point
    :type h: Float

    :param rh: Heading of the segment relative to its heading
    :type rh: Float

    :param clr: Center line radius.
    :type clr: Float

    :param lw: Lane width.
    :type lw: Float

    :param nbr_of_lanes: Number of lanes.
    :type nbr_of_lanes: Integer

    :param lanes_going_OUT: Number of lanes going out of the crossroad. Used to reverse the lane that goes out of the crossroad
    :type lanes_going_OUT: Integer

    :param Stl: Tab of tabs contening relevant points (3 points per tab) describing a stopline
    :type Stl:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    :param cw: Tab of tabs contening relevant points (3 points per tab) describing the 3 lines describing a crosswalk
    :type cw:[ [x1,y1,x2,y2] ] with x and y float

    :param DefinedSpeed: Represent the speed that the road has per default (defined by the speedprofil in the Road Class)
    :type DefinedSpeed: Float

    '''
    def __init__(self, id, x0, y0, h, rh, clr, lw, nbr_of_lanes, lanes_going_OUT, SpeedL, RefS, Stl, cw):

        # General Initialization

        Road.__init__(self, id)     #Gave the Id linked to BendRoad
        self.SpeedLimit = SpeedL    #Set the different speeds
        self.RefSpeed = RefS
        self.stopline = Stl
        self.crosswalk = cw
        self.DefinedSpeed = self.SpeedProfil[1]


        # Lanes, Center and Edges of the Road

        self.c.append(Bend( x0, y0, h, rh, clr))

        self.e1.append(Bend( x0 - lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2),      #Buggy FIX HERE for Object/Tab PB
                        y0 + lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2),
                        h, rh, clr - np.sign(rh) * lw * lanes_going_OUT))

        self.e2.append(Bend( x0 - lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2),      #Same
                        y0 - lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2),
                        h, rh, clr + np.sign(rh) * lw * (nbr_of_lanes -lanes_going_OUT)))

        lwi = (nbr_of_lanes - 1) * lw                                         #This work. To better understand how, i recommand doing this code by hand in a simple case
        for _ in range(nbr_of_lanes):
            self.l.append(Bend( x0 + lwi * np.cos(h + np.pi / 2) / 2,
                                y0 + lwi * np.sin(h + np.pi / 2) / 2,
                               h, rh, clr - np.sign(rh) * lwi / 2))
            lwi -= 2 * lw

        #This changes the direction of the lanes that drive backwards
        if nbr_of_lanes-lanes_going_OUT>0:
            for i in range(nbr_of_lanes-lanes_going_OUT):
                l=[]
                for (x, y) in self.l[i]:
                    l.append([x, y])
                l = l[::-1]
                self.l[i] = l

class ClothoidRoads (Road):
    '''
    This is a representation of Spiral roads (Clothoïd) in Prescan. An Euler Spiral is used to represent it

    :param id: Unique id.
    :type id: String

    :param x0: The x coordinate of the starting point of spiral
    :type x0: Float

    :param y0: The y coordinate of the starting point of the spiral
    :type y0: Float

    :param h: Global heading of the bezier curve at its starting point
    :type h: Float

    :param C2 : constant describing the spiral. If R the radius of the spiral at the curvilinear abscissa L, R*L =C**2, and C2 = C**2
    :type C2 = Float

    :Lstart: curvilinear abscissa of the start of the spiral
    :type Lstart: Float

    :Lstart: curvilinear abscissa of the end of the spiral
    :type Lend: Float

    :flipped: boolean that indicates if the orientation of the spiral is flipped
    :type flipped: Boolean

    :param lw: Lane width.
    :type lw: Float

    :param nbr_of_lanes: Number of lanes.
    :type nbr_of_lanes: Integer

    :param lanes_in_x_dir: Number of lanes going out of the crossroad. Used to reverse the lane that goes out of the crossroad
    :type nbr_of_lanes: Integer

    :param Stl: Tab of tabs contening relevant points (3 points per tab) describing a stopline
    :type Stl:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    :param cw: Tab of tabs with relevant points (3 points per tab) describing a crosswalk
    :type cw:[ [x1,y1,x2,y2,x3,y3] ] with x and y float
    '''
    def __init__(self, id, x0, y0, h, C2, Lstart, Lend, flipped, lw, nbr_of_lanes, lanes_in_x_dir, Tabpointcon, SpeedL, RefS, cw, Stl):

        # General Initialization

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.stopline = Stl
        self.crosswalk = cw
        self.DefinedSpeed = self.SpeedProfil[2]


        # we calculate clothoid roads with an integration, so, step by step, the error increases and the last point
        # of the clothoid is one of two meter away of where it shoul be. In order to correct it, we calculate 2
        # spirals : one starting from (x0,y0) going in the x direction, and one starting from the end of the road
        # (xend2, yend2) and going in the reverse x direction. Then we obtain the good spiral by making the average
        # spiral of the 2 spirals calculated. The average is weigh by the curvilinear abscissa of the point we calculate.
        # (xend, yend) is the (x0,y0) of the road attached to the end of the spiral road
        diff = nbr_of_lanes/2
        center1 = Clothoid(x0, y0, h, C2, 1.0, Lstart, Lend)
        cent1 = []
        for (x,y) in center1 :
            cent1.append([x,y])
            xend, yend = x,y

        if flipped == True : # if the spiral road is flipped, (xend,yend) is the axial symmetric of (xend,yend) calculated.  symmetry axis : line with heading = h and going through (x0,y0)
            a1 = np.tan(h)
            b1 = y0 - a1*x0
            a2 = np.tan(h+np.pi/2)
            b2 = cent1[len(cent1)-1][1] - a2*cent1[len(cent1)-1][0]
            xi = (b2-b1)/(a1-a2)
            yi = a1*xi + b1
            cent1[len(cent1)-1][0] = 2*xi - cent1[len(cent1)-1][0]
            cent1[len(cent1)-1][1] = 2*yi - cent1[len(cent1)-1][1]


        xend, yend = cent1[len(cent1)-1][0], cent1[len(cent1)-1][1]
        xend2, yend2 = xend + 1000, yend - 1000
        for k in range (len(Tabpointcon)): # here we find (xend2, yend2)
            if Tabpointcon[k] != []:
                (x, y) = Tabpointcon[k][0]
                if dist((x,y),(xend,yend)) < dist((xend2,yend2),(xend,yend)) :
                    xend2, yend2 = x,y
        if dist((xend2,yend2),(xend,yend))>5 : # if the end of the spiral road is not connected to the start of an other road
            print ("The rules of the wiki aren't followed : you should connect the end of a spiral road to the start of an other road (except crossroads/roundabouts)")

        center2 =  Clothoid(xend2, yend2, h, C2, -1.0, Lend, Lstart) # spiral driving backwards
        cent2 = []
        for (x,y) in center2 :
            cent2.append([x,y])

        if flipped == True : # reverses the spiral (cf line 215)
            c =[cent1,cent2]
            a1 = np.tan(h)
            a2 = np.tan(h+np.pi/2)
            for elem in c :
                b1 = elem[0][1] - a1*elem[0][0]
                for k in range (len(elem)):
                    b2 = elem[k][1] - a2*elem[k][0]
                    xi = (b2-b1)/(a1-a2)
                    yi = a1*xi + b1
                    elem[k][0] = 2*xi - elem[k][0]
                    elem[k][1] = 2*yi - elem[k][1]

        cent = []
        nbr = min(len(cent1),len(cent2))
        for k in range(nbr): # average of the two spirals
            x1, y1 = cent1[k]
            x2, y2 = cent2[nbr-1-k]
            x = (x1*(nbr-k-1) + x2*k)/(nbr-1)
            y = (y1*(nbr-k-1) + y2*k)/(nbr-1)
            cent.append([x,y])

        if (h>np.pi/2) and (h<3*np.pi/2) :
            cent.reverse()


        for i in range (nbr_of_lanes): # now we add the lanes
            lane = []
            count = 0
            angle = h
            for (x,y) in cent :
                if count>0:
                    pt0 = (cent[count-1])
                    pt1 = (cent[count])

                else :
                    pt0 = cent[0]
                    pt1 = cent[1]
                H = dist(pt0,pt1)
                A = abs(pt0[0]-pt1[0])
                if H != 0:
                    angle = np.arccos( A / H )
                    if pt0[0]< pt1[0]:
                        if pt1[1]< pt0[1]:
                            angle = -angle
                        x1 = x - lw*(i+0.5-diff)*np.sin(angle)
                        y1 = y + lw*(i+0.5-diff)*np.cos(angle)

                    else:
                        if pt1[1]> pt0[1]:
                            angle = -angle
                        x1 = x + lw*(i+0.5-diff)*np.sin(angle)
                        y1 = y - lw*(i+0.5-diff)*np.cos(angle)
                    lane.append([x1,y1])
                count += 1

            p1 = lane[0]
            interval_lane = [p1]
            k = 1
            while k+1< len(lane):  # we replace the points so that each lane will have a length as close as possible of 1
                p2 = lane[k]
                if (dist(p1,p2)>0.99) and (dist(p1,p2)<1.01):
                    p1 = p2
                    if p1 != interval_lane[len(interval_lane)-1]:
                        interval_lane.append(p1)
                else :
                    if dist(p1,p2)< 0.99 : # if p1 and p2 are too close, the new point is outside [p1,p2]
                        p3 = lane[k+1]
                        poly = polynom (p1,p2,p3)
                        if poly != None : # if poly == None, p1 = p2
                            p1 = offset_point(poly,p1,p3)
                        if p1 != interval_lane[len(interval_lane)-1]:
                            interval_lane.append(p1)
                    else : # if the distance between p1 and p2 >1, then the point is in [p1,p2]
                        while dist(p1,p2)>1.01:
                            p12 = ( (p1[0]+p2[0])/2, (p1[1]+p2[1])/2 )
                            if (dist(p1,p12)>0.99) and (dist(p1,p12)<1.01):
                                p1 = p12
                            else :
                                poly = polynom(p1,p12,p2)
                                if poly != None :
                                    p1 = offset_point(poly,p1,p2)
                            if p1 != interval_lane[len(interval_lane)-1]:
                                interval_lane.append(p1)
                k += 1
            p2 = lane[len(lane)-1]
            while dist(p1,p2)>1.01:
                p12 = ( (p1[0]+p2[0])/2, (p1[1]+p2[1])/2 )
                if (dist(p1,p12)>0.99) and (dist(p1,p12)<1.01):
                    p1 = p12
                else :
                    poly = polynom(p1,p12,p2)
                    if poly != None :
                        p1 = offset_point(poly,p1,p2)
                if p1 != interval_lane[len(interval_lane)-1]:
                    interval_lane.append(p1)

            if p2 != interval_lane[len(interval_lane)-1]:
                interval_lane.append(p2)

            self.l.append(interval_lane)


        if nbr_of_lanes-lanes_in_x_dir>0: # reverse the lanes driving backwards
            for j in range(nbr_of_lanes-lanes_in_x_dir):
                lane=[]
                for (x, y) in self.l[j+lanes_in_x_dir]:
                    lane.append([x, y])
                lane = lane[::-1]
                self.l[j+lanes_in_x_dir] = lane









class CurvedRoad(Road):
    '''
    This a representation of the curved road in Prescan. A beezier curve is used to represent it.

    :param id: Unique id.
    :type id: String

    :param x0: The x coordinate of the starting point of the bezier curve
    :type x0: Float

    :param y0: The y coordinate of the starting point of the bezier curve
    :type y0: Float

    :param h: Global heading of the bezier curve at its starting point
    :type h: Float

    :param rh: Heading of the bezier curve relative to its starting point
    :type rh: Float

    :param cp1: Represents the distance between the first control point and the starting point at an angle that's equal to the heading.
    :type cp1: Float

    :param cp2: Represents the distance between the second control point and the endpoint at an angle that's equal to the heading plus the relative heading.
    :type cp2: Float

    :param dx: Relative x offset of the endpoint from the starting point
    :type dx: Float

    :param dy: Relative y offset of the endpoint from the starting point
    :type dy: Float

    :param lw: Lane width.
    :type lw: Float

    :param nbr_of_lanes: Number of lanes.
    :type nbr_of_lanes: Integer

    :param lanes_going_OUT: Number of lanes going out of the crossroad. Used to reverse the lane that goes out of the crossroad
    :type nbr_of_lanes: Integer

    :param Stl: Tab of tabs contening relevant points (3 points per tab) describing a stopline
    :type Stl:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    :param cw: Tab of tabs contening relevant points (3 points per tab) describing the 3 lines describing a crosswalk
    :type cw:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    :param DefinedSpeed: Represent the speed that the road has per default (defined by the speedprofil in the Road Class)
    :type DefinedSpeed: Float

    '''
    def __init__(self, id, x0, y0, h, rh, cp1, cp2, dx, dy, lw, nbr_of_lanes, lanes_going_OUT, SpeedL, RefS, Stl, cw): #Same as BendRoad

        # General Initialization

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.stopline = Stl
        self.crosswalk = cw
        self.DefinedSpeed = self.SpeedProfil[2]

        # Creation of the points needed for the Bezier Curve

        x_ = dx * np.cos(h) - dy * np.sin(h)
        y_ = dx * np.sin(h) + dy * np.cos(h)
        x1 = x0 + cp1 * np.cos(h)
        y1 = y0 + cp1 * np.sin(h)
        x2 = x0 + x_ - cp2 * np.cos(h + rh)
        y2 = y0 + y_ - cp2 * np.sin(h + rh)
        x3 = x0 + x_
        y3 = y0 + y_

        xs = [x0, x1, x2, x3]   # Those two lists are used to define a Bezier Curve cf Path.py
        ys = [y0, y1, y2, y3]

        # Lanes, Center and Edges of the Road

        self.c.append(Curve(xs, ys, 0))
        self.e1.append(Curve(xs, ys, lw * nbr_of_lanes / 2))
        self.e2.append(Curve(xs, ys, -lw * nbr_of_lanes / 2))

        lwi = -(nbr_of_lanes - 1) * lw / 2
        for _ in range(nbr_of_lanes):
            lane = Curve(xs,ys,lwi)
            lane1 = []
            for (x,y) in lane :
                lane1.append([x,y])
            p1 = lane1[0]
            interval_lane = [p1]
            k = 1
            while k+1< len(lane1):  # we replace the points so that each lane will have a length as close as possible of 1
                p2 = lane1[k]
                if (dist(p1,p2)>0.99) and (dist(p1,p2)<1.01):
                    p1 = p2
                    if p1 != interval_lane[len(interval_lane)-1]:
                        interval_lane.append(p1)
                else :
                    if dist(p1,p2)< 0.99 : # if p1 and p2 are too close, the new point is outside [p1,p2]
                        p3 = lane1[k+1]
                        poly = polynom (p1,p2,p3)
                        if poly != None : # if poly == None, p1 = p2
                            p1 = offset_point(poly,p1,p3)
                        if p1 != interval_lane[len(interval_lane)-1]:
                            interval_lane.append(p1)
                    else : # if the distance between p1 and p2 >1, then the point is in [p1,p2]
                        while dist(p1,p2)>1.01:
                            p12 = ( (p1[0]+p2[0])/2, (p1[1]+p2[1])/2 )
                            if (dist(p1,p12)>0.99) and (dist(p1,p12)<1.01):
                                p1 = p12
                            else :
                                poly = polynom(p1,p12,p2)
                                if poly != None :
                                    p1 = offset_point(poly,p1,p2)
                            if p1 != interval_lane[len(interval_lane)-1]:
                                interval_lane.append(p1)
                k += 1
            p2 = lane1[len(lane1)-1]
            while dist(p1,p2)>1.01:
                p12 = ( (p1[0]+p2[0])/2, (p1[1]+p2[1])/2 )
                if (dist(p1,p12)>0.99) and (dist(p1,p12)<1.01):
                    p1 = p12
                else :
                    poly = polynom(p1,p12,p2)
                    if poly != None :
                        p1 = offset_point(poly,p1,p2)
                if p1 != interval_lane[len(interval_lane)-1]:
                    interval_lane.append(p1)

            if p2 != interval_lane[len(interval_lane)-1]:
                interval_lane.append(p2)

            self.l.append(interval_lane)
            lwi += lw

        #This changes the direction of the lanes that drive backwards
        if nbr_of_lanes-lanes_going_OUT>0:
            for i in range(nbr_of_lanes-lanes_going_OUT):
                l=[]
                for (x, y) in self.l[i]:
                    l.append([x, y])
                l = l[::-1]
                self.l[i] = l

class RoundaboutRoad(Road):
    '''
    This a representation of the roundabout. Each roundabout contains road cross sections that represent the exits and entries to the segment.

    :param id: Unique id.
    :type id: String

    :param x0: The x coordinate of the center of the roundabout.
    :type x0: Float

    :param y0: The y coordinate of the center of the roundabout.
    :type y0: Float

    :param r: Distance from the center of the roundabout to the center lane.
    :type r: Float

    :param lw: Lane width.
    :type lw: Float

    :param chs: List of headings for each road cross section (the exit and entrance of the RA).
    :type chs: [Float]

    :param nbr_of_lanes: Number of lanes.
    :type nbr_of_lanes: Integer

    :param DefinedSpeed: Represent the speed that the road has per default (defined by the speedprofil in the Road Class)
    :type DefinedSpeed: Float

    :param cw: Tab of tabs contening relevant points (3 points per tab) describing the 3 lines describing a crosswalk
    :type cw:[ [x1,y1,x2,y2] ] with x and y float

    '''
    def __init__(self, id, x0, y0, r, lw, cs_h, cs_filletradius, cs_nb_of_lanes, cs_nb_of_lane_x_direction, nbr_of_lanes, SpeedL, RefS, TabConnect, cw):

        # General Initialization

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.TabConnect = TabConnect
        self.DefinedSpeed = self.SpeedProfil[3]
        self.crosswalk = cw

        # Creating every circles

        lwhalf = lw/2
        r1 = r
        for i in range(nbr_of_lanes):
            l1 =Bend( x0, y0 - (r1 - lwhalf), 0, 2 * np.pi, r1 - lwhalf)
            r1 = (r1 - lw)
            Current_Lane1 = []
            for (x,y) in l1:
                Current_Lane1.append([x, y])
            self.l.append(Current_Lane1)



        # Creation of Exit and entry lane

        for j in range(4):

            nb_of_lanes = cs_nb_of_lanes[j]
            nb_lanes_going_out = cs_nb_of_lane_x_direction[j]
            nb_of_lanes_going_IN = nb_of_lanes - nb_lanes_going_out
            fillet_radius = cs_filletradius[j]

            # Creation of the 2 starting points

            starting_point = TabConnect[j]
            print(starting_point)
            starting_point_right = (starting_point[0][0]- (nb_of_lanes/2)*lw*np.sin(cs_h[j]),starting_point[0][1] + (nb_of_lanes/2)*lw*np.cos(cs_h[j]))
            starting_point_left = (starting_point[0][0]+ (nb_of_lanes/2)*lw*np.sin(cs_h[j]),starting_point[0][1] - (nb_of_lanes/2)*lw*np.cos(cs_h[j]))


            # Entry access


            counter =0
            for k in range(nb_of_lanes_going_IN):


                center_of_the_circle_right = ( starting_point_right[0]-r*(fillet_radius/100)*np.sin(cs_h[j]), starting_point_right[1]+(r*(fillet_radius/100))*np.cos(cs_h[j]))


                circle1 = [center_of_the_circle_right[0], center_of_the_circle_right[1], r*(fillet_radius/100) + (k+1)*lw] # Circle describe by the entry access
                circle2 = [x0, y0, (r-lw/2)] # main circle


                (x1,y1) = (starting_point_right[0]+ (k+1+counter)*(lw/2)*np.sin(cs_h[j]),starting_point_right[1] - (k+1+counter)*(lw/2)*np.cos(cs_h[j])) # Staring point of the Lane




                (x2,y2) = Intersection_Circle(circle1,circle2)[1]     # Point that of instersection betwenn main circle and circle descibe by the entry access

                # We find here the closest point on the circle to (x2,y2)
                min= 100
                index_min = 0
                for n in range(len(self.l[0])):

                    if dist(self.l[0][n],(x2,y2)) < min:
                        min = dist(self.l[0][n],(x2,y2))
                        index_min = n

                # And then create a curve

                (xs, ys) = self.l[0][index_min+5]
                (xs1,ys1) = self.l[0][index_min+3]
                (xs2,ys2) = self.l[0][index_min]



                xs = [x1, xs2, xs1, xs]
                ys = [y1, ys2, ys1, ys]


                l1 = Curve(xs, ys, 0)
                Current_Lane1 = []
                for (x,y) in l1:
                    Current_Lane1.append([x, y])
                counter +=1
                self.l.append(Current_Lane1)



            # Exit access

            # Same expect tfor the math
            counter =0
            for p in range(nb_lanes_going_out):


                center_of_the_circle_left = ( starting_point_left[0]+r*(fillet_radius/100)*np.sin(cs_h[j]), starting_point_left[1]-(r*(fillet_radius/100))*np.cos(cs_h[j]))


                circle1 = [center_of_the_circle_left[0], center_of_the_circle_left[1], r*(fillet_radius/100) + (p+1)*lw]
                circle2 = [x0, y0, (r-lw/2)]


                (x1,y1) = (starting_point_left[0]- (p+1+counter)*(lw/2)*np.sin(cs_h[j]),starting_point_left[1] + (p+1+counter)*(lw/2)*np.cos(cs_h[j]))

                (x2,y2) = Intersection_Circle(circle1,circle2)[0]


                min= 100
                index_min = 0
                for n in range(len(self.l[0])):

                    if dist(self.l[0][n],(x2,y2)) < min:
                        min = dist(self.l[0][n],(x2,y2))
                        index_min = n


                (xs, ys) = self.l[0][index_min-5]
                (xs1,ys1) = self.l[0][index_min-3]
                (xs2,ys2) = self.l[0][index_min+1]



                xs = [xs, xs1, xs2, x1]
                ys = [ys, ys1, ys2, y1]
                l1 = Curve(xs, ys, 0)
                Current_Lane1 = []
                for (x,y) in l1:
                    Current_Lane1.append([x, y])


                self.l.append(Current_Lane1)
                counter +=1



class ExitLane(Road):
    '''
    This a representation of a roundabout cross section.

    :param id: Unique id.
    :type id: String

    :param x0: The x coordinate of the center of the endpoint of the exit lane.
    :type x0: Float

    :param y0: The y coordinate of the center of the endpoint of the exit lane.
    :type y0: Float
    :param r: Distance from the center of the roundabout to the center lane.
    :type r: Float

    :param lw: Lane width.
    :type lw: Float

    :param ch: Heading of the road end relative to the heading of the roundabout.
    :type ch: Float

    :param nbr_of_lanes: Number of lanes.
    :type nbr_of_lanes: Integer

    :param cw: Tab of tabs contening relevant points (3 points per tab) describing the 3 lines describing a crosswalk
    :type cw:[ [x1,y1,x2,y2] ] with x and y float

    '''
    def __init__(self, id, x0, y0, r, lw, ch, nbr_of_lanes, SpeedL, RefS, cw):

        # General Init

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.DefinedSpeed = self.SpeedProfil[4]
        r += lw
        self.x = x0
        self.y = y0
        self.r = r
        self.ch = ch
        self.lw = lw
        self.crosswalk = cw

        # Get exit lanes

        # For edges
        (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, lw)
        self.e1.append(Bend(x, y, h, a, rc))
        (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, -lw)
        self.e2.append(Bend(x, y, h, a, rc))

        # For lanes
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

        xc1 = x0 + (r - lw + ld) * np.cos(ch - sign * np.pi / 8)
        yc1 = y0 + (r - lw + ld) * np.sin(ch - sign * np.pi / 8)

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
    '''
    This a representation of a straight road in Prescan.

    :param id: Unique id.
    :type id: String

    :param x0: The x coordinate of the center of the start of the road segment.
    :type x0: Float

    :param y0: The y coordinate of the center of the start of the road segment.
    :type y0: Float

    :param h: Global heading of the road segment at the start point.
    :type h: Float

    :param l: Length of the road segment
    :type l: Float

    :param lw: Lane width.
    :type lw: Float

    :param nbr_of_lanes: Number of lanes.
    :type nbr_of_lanes: Integer

    :param Stl: Tab of tabs contening relevant points (3 points per tab) describing a stopline
    :type Stl:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    :param cw: Tab of tabs contening relevant points (3 points per tab) describing the 3 lines describing a crosswalk
    :type cw:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    :param DefinedSpeed: Represent the speed that the road has per default (defined by the speedprofil in the Road Class)
    :type DefinedSpeed: Float

    '''
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes, lanes_going_OUT, SpeedL, RefS, Stl, cw):

        # General Init

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.stopline = Stl
        self.crosswalk = cw
        self.DefinedSpeed = self.SpeedProfil[0]

        # Edges, Center Line and Lanes

        self.c.append(Straight( x0, y0, h, l))

        self.e1.append(Straight( x0 - (nbr_of_lanes/2)*lw * np.cos(h + np.pi / 2),
                                y0 - (nbr_of_lanes/2) * lw * np.sin(h + np.pi / 2), h, l))

        self.e2.append(Straight( x0 + (nbr_of_lanes/2)*lw * np.cos(h + np.pi / 2),
                                y0 + lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2), h, l))

        lwi = (nbr_of_lanes -1) * lw/2
        for _ in range(nbr_of_lanes):
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l))
            lwi -= lw

        #This changes the direction of the lanes that drive backwards
        if nbr_of_lanes-lanes_going_OUT>0:
            for i in range(nbr_of_lanes-lanes_going_OUT):
                l=[]
                for (x, y) in self.l[i]:
                    l.append([x, y])
                l = l[::-1]
                self.l[i] = l

class Crosswalkr(Road):
    '''
    This a representation of a crosswalk road in Prescan.

    :param id: Unique id.
    :type id: String

    :param x0: The x coordinate of the center of the start of the road segment.
    :type x0: Float

    :param y0: The y coordinate of the center of the start of the road segment.
    :type y0: Float

    :param h: Global heading of the road segment at the start point.
    :type h: Float

    :param l: Length of the road segment
    :type l: Float

    :param lw: Lane width.
    :type lw: Float

    :param nbr_of_lanes: Number of lanes.
    :type nbr_of_lanes: Integer

    :param cw: Tab of tabs contening relevant points (3 points per tab) describing the 3 lines describing a crosswalk
    :type cw:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    :param DefinedSpeed: Represent the speed that the road has per default (defined by the speedprofil in the Road Class)
    :type DefinedSpeed: Float

    '''
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes, lanes_going_OUT, SpeedL, RefS, cw):

        # General Init

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.crosswalk = cw
        self.DefinedSpeed = self.SpeedProfil[0]

        # Edges, Center Line and Lanes

        self.c.append(Straight( x0, y0, h, l))

        self.e1.append(Straight( x0 - (nbr_of_lanes/2)*lw * np.cos(h + np.pi / 2),
                                y0 - (nbr_of_lanes/2) * lw * np.sin(h + np.pi / 2), h, l))

        self.e2.append(Straight( x0 + (nbr_of_lanes/2)*lw * np.cos(h + np.pi / 2),
                                y0 + lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2), h, l))

        lwi = (nbr_of_lanes -1) * lw/2
        for _ in range(nbr_of_lanes):
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l))
            lwi -= lw

        #This changes the direction of the lanes that drive backwards
        if nbr_of_lanes-lanes_going_OUT>0:
            for i in range(nbr_of_lanes-lanes_going_OUT):
                l=[]
                for (x, y) in self.l[i]:
                    l.append([x, y])
                l = l[::-1]
                self.l[i] = l

class AdapterRoad(Road):
    '''
    This a representation of an adapter road in Prescan.

    :param id: Unique id.
    :type id: String

    :param x0: The x coordinate of the center of the start of the road segment.
    :type x0: Float

    :param y0: The y coordinate of the center of the start of the road segment.
    :type y0: Float

    :param h: Global heading of the road segment at the start point.
    :type h: Float

    :param l: Length of the road segment
    :type l: Float

    :param lw: Lane width.
    :type lw: Float

    :param nbr_of_lanes_start: Number of lanes.
    :type nbr_of_lanes_start: Integer

    :param nbr_of_lanes_end: Number of lanes.
    :type nbr_of_lanes_end: Integer

    :param lanes_going_OUT_start: Number of lanes.
    :type lanes_going_OUT_start: Integer

    :param lanes_going_OUT_end: Number of lanes.
    :type lanes_going_OUT_end: Integer

    :param Stl: Tab of tabs contening relevant points (3 points per tab) describing a stopline
    :type Stl:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    :param cw: Tab of tabs contening relevant points (3 points per tab) describing the 3 lines describing a crosswalk
    :type cw:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    :param DefinedSpeed: Represent the speed that the road has per default (defined by the speedprofil in the Road Class)
    :type DefinedSpeed: Float

    :param lane_offset: represent the lane offset of the adapter (>0 if we remove lanes, <0 if we add lanes)
    :type lane_offset: int

    '''
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes_start, nbr_of_lanes_end, lanes_in_x_dir_start, lanes_in_x_dir_end, SpeedL, RefS, Stl, cw, lane_offset):

        # General Init

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.stopline = Stl
        self.crosswalk = cw
        self.DefinedSpeed = self.SpeedProfil[5]

        # Edges, Center Line and Lanes

        self.c.append(Straight( x0, y0, h, l))

        self.e1.append(Straight( x0 + lw * (nbr_of_lanes_start/2)* np.cos(h + np.pi / 2),
                                y0 + lw * (nbr_of_lanes_start/2)* np.sin(h + np.pi / 2), h, l))

        self.e2.append(Straight( x0 - lw * (nbr_of_lanes_start/2)* np.cos(h + np.pi / 2),
                                y0 - lw * (nbr_of_lanes_start/2)* np.sin(h + np.pi / 2), h, l/2))

        difference = abs(nbr_of_lanes_start - nbr_of_lanes_end)
        lo_right = abs(lane_offset)
        lo_left = abs(difference - lo_right)

        if nbr_of_lanes_start%2 == 0 : #if there is an odd number of lanes, then x0 and y0 are on the center of a lane
            offset_center = 0
        else :
            offset_center = 0.5

        if nbr_of_lanes_start>nbr_of_lanes_end:  # If we remove lanes


            self.e1.append(Straight( x0 - lw*(nbr_of_lanes_start/2)*np.sin(h),
                                    y0 + lw*(nbr_of_lanes_start/2)*np.cos(h), h, l/2))

            self.e1.append(Straight( x0 + (l/2)*np.cos(h) - lw*(offset_center-lo_left+nbr_of_lanes_end)*np.sin(h),
                                    y0 + (l/2)*np.sin(h) + lw*(offset_center-lo_left+nbr_of_lanes_end)*np.cos(h), h, l/2))

            self.e2.append(Straight( x0 + lw*(nbr_of_lanes_start/2)*np.sin(h),
                                    y0 - lw*(nbr_of_lanes_start/2)*np.cos(h), h, l/2))

            self.e2.append(Straight( x0 + (l/2)*np.cos(h) + lw*(offset_center-lo_left)*np.sin(h),
                                    y0 + (l/2)*np.sin(h) - lw*(offset_center-lo_left)*np.cos(h), h, l/2))


            lanes_before=[]
            lanes_after=[]
            counter_s = nbr_of_lanes_start -1

            # here we create the lanes juste before the change

            while counter_s > -1 :
                lane = Straight( x0 + lw*(nbr_of_lanes_start/2 -0.5 - counter_s)*np.sin(h),
                                y0 - lw*(nbr_of_lanes_start/2 -0.5 - counter_s)*np.cos(h), h, 3)
                laneBis = []
                for (x,y) in lane :
                    laneBis.append([x,y])

                lanes_before.append(laneBis)
                counter_s -= 1


            # now we reverse the lanes driving backwards
            for k in range (nbr_of_lanes_start-lanes_in_x_dir_start) :
                lanes_before[k]=lanes_before[k][::-1]


            # then we create the lanes just after the change

            counter = 0

            while counter < nbr_of_lanes_end :
                lane = Straight( x0 + (l-3)*np.cos(h) - lw*(nbr_of_lanes_start/2 -0.5 -counter-lo_left)*np.sin(h),
                                y0 + (l-3)*np.sin(h) + lw*(nbr_of_lanes_start/2 -0.5 -counter-lo_left)*np.cos(h), h, 3)
                counter += 1

                laneBis = []
                for (x,y) in lane :
                    laneBis.append([x,y])

                lanes_after.append(laneBis)

            # now we reverse the lanes driving backwards

            for k in range (nbr_of_lanes_end-lanes_in_x_dir_end) :
                lanes_after[k]=lanes_after[k][::-1]




        elif nbr_of_lanes_start<nbr_of_lanes_end:   # Same if we add a lane

            self.e1.append(Straight( x0 - lw*(nbr_of_lanes_start/2)*np.sin(h),
                                    y0 + lw*(nbr_of_lanes_start/2)*np.cos(h), h, l/2))

            self.e1.append(Straight( x0 + (l/2)*np.cos(h) - lw*(-offset_center-lo_right-1+nbr_of_lanes_end)*np.sin(h),
                                    y0 + (l/2)*np.sin(h) + lw*(-offset_center-lo_right-1+nbr_of_lanes_end)*np.cos(h), h, l/2))

            self.e2.append(Straight( x0 + lw*(nbr_of_lanes_start/2)*np.sin(h),
                                    y0 - lw*(nbr_of_lanes_start/2)*np.cos(h), h, l/2))

            self.e2.append(Straight( x0 + (l/2)*np.cos(h) + lw*(-offset_center+lo_right-1)*np.sin(h),
                                    y0 + (l/2)*np.sin(h) - lw*(-offset_center+lo_right-1)*np.cos(h), h, l/2))


            lanes_before=[]
            lanes_after=[]
            counter_s = nbr_of_lanes_start -1

            # here we create the lanes juste before the change

            while counter_s > -1 :
                lane = Straight( x0 + lw*(nbr_of_lanes_start/2 -0.5 - counter_s)*np.sin(h),
                                y0 - lw*(nbr_of_lanes_start/2 -0.5 - counter_s)*np.cos(h), h, 3)
                laneBis = []
                for (x,y) in lane :
                    laneBis.append([x,y])

                lanes_before.append(laneBis)
                counter_s -= 1


            # now we reverse the lanes driving backwards

            for k in range (nbr_of_lanes_start - lanes_in_x_dir_start) :
                lanes_before[k]=lanes_before[k][::-1]


            # then we create the lanes just after the change

            counter = 0

            while counter < nbr_of_lanes_end :
                lane = Straight( x0 + (l-3)*np.cos(h) - lw*(nbr_of_lanes_start/2 -0.5 -counter+lo_left)*np.sin(h),
                                y0 + (l-3)*np.sin(h) + lw*(nbr_of_lanes_start/2 -0.5 -counter+lo_left)*np.cos(h), h, 3)
                counter += 1

                laneBis = []
                for (x,y) in lane :
                    laneBis.append([x,y])

                lanes_after.append(laneBis)

            # now we reverse the lanes driving backwards
            for k in range (nbr_of_lanes_end-lanes_in_x_dir_end) :
                lanes_after[k]=lanes_after[k][::-1]

        else : #if there are the same number of lanes before and after the adapter road
            self.e1.append(Straight( x0 - lw*(nbr_of_lanes_start/2)*np.sin(h),
                                    y0 + lw*(nbr_of_lanes_start/2)*np.cos(h), h, l))
            self.e2.append(Straight( x0 + lw*(nbr_of_lanes_start/2)*np.sin(h),
                                    y0 - lw*(nbr_of_lanes_start/2)*np.cos(h), h, l))

            lanes_total=[]
            counter_s = nbr_of_lanes_start -1

            while counter_s > -1 :
                lane = Straight( x0 + lw*(nbr_of_lanes_start/2 -0.5 - counter_s)*np.sin(h),
                                y0 - lw*(nbr_of_lanes_start/2 -0.5 - counter_s)*np.cos(h), h, l)
                laneBis = []
                for (x,y) in lane :
                    laneBis.append([x,y])

                lanes_total.append(laneBis)
                counter_s -= 1

            for k in range (nbr_of_lanes_start - lanes_in_x_dir_start) :
                lanes_total[k]=lanes_total[k][::-1]

            for k in range (nbr_of_lanes_start):
                self.l.append(lanes_total[k])

            return None



        if len(lanes_before)>len(lanes_after) : # here we store data in lanes_max, lanes_min, lanes_max_x and lanes_min_x to use the same programm section if we add or remove a lane
            lanes_max = lanes_before
            lanes_min = lanes_after
            lanes_max_x = lanes_in_x_dir_start
            lanes_min_x = lanes_in_x_dir_end
        else :
            lanes_max = lanes_after
            lanes_min = lanes_before
            lanes_max_x = lanes_in_x_dir_end
            lanes_min_x = lanes_in_x_dir_start


        # First we connect the lanes in the x direction

        if (lanes_min_x) == 1 :

            (x2,y2) = (lanes_min[len(lanes_min)-lanes_min_x][3][0] , lanes_min[len(lanes_min)-lanes_min_x][3][1])
            (x4,y4) = (lanes_min[len(lanes_min)-lanes_min_x][0][0] , lanes_min[len(lanes_min)-lanes_min_x][0][1])

            for k in range (lanes_max_x):
                (x1,y1) = (lanes_max[len(lanes_max)-k-1][3][0] , lanes_max[len(lanes_max)-k-1][3][1])
                (x3,y3) = Intersection_Lines(lanes_min[len(lanes_min)-lanes_min_x],lanes_max[len(lanes_max)-k-1])
                (x5,y5) = (lanes_max[len(lanes_max)-k-1][0][0] , lanes_max[len(lanes_max)-k-1][0][1])

                if len(lanes_before)>len(lanes_after) :
                    xs1 = [x5, x1, x1, x3]
                    ys1 = [y5, y1, y1, y3]
                    xs2 = [x3, x4, x4, x2]
                    ys2 = [y3, y4, y4, y2]

                else :
                    xs1 = [x4, x2, x2, x3]
                    ys1 = [y4, y2, y2, y3]
                    xs2 = [x3, x5, x5, x1]
                    ys2 = [y3, y5, y5, y1]

                # we create 2 curves to have a smoother shape (a S shape) : x2,x4 and x3 forms (for example) the first curve of the S, and x1,x5 and x3 the second one
                l1 = Curve(xs1, ys1, 0)
                l2 = Curve(xs2, ys2, 0)
                Current_Lane1 = []
                counter_addLine = -1
                for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                    if counter_addLine>-1 :
                        if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    else :
                        Current_Lane1.append([x, y])
                        counter_addLine+=1
                self.l.append(Current_Lane1)

                Current_Lane1 = []
                counter_addLine = -1
                for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                    if counter_addLine>-1 :
                        if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    else :
                        Current_Lane1.append([x, y])
                        counter_addLine+=1
                self.l.append(Current_Lane1)


        else :
            # For example (with a road going only in the x direction)
            #
            #_______________
            #       1            ______________
            #       2                 I
            #       3                 II
            #       4                 III
            #       5            ______________
            #_______________
            #
            # We connect 1 and 2 to I, 3 to II and 4 and 5 to III


            a =np.tan(h)
            k = 0
            i = 0
            if lanes_min_x < lanes_max_x :
                while (k < lanes_max_x) and (i<lanes_min_x-1): # for example, we connect 1,2 and 3 to I and II. When it will inly remain III, we will connect to it the remaining lanes
                    (x4,y4) = (lanes_min[len(lanes_min)-lanes_min_x+i][0][0] , lanes_min[len(lanes_min)-lanes_min_x+i][0][1])
                    (x2,y2) = (lanes_min[len(lanes_min)-lanes_min_x+i][3][0] , lanes_min[len(lanes_min)-lanes_min_x+i][3][1])

                    (x1,y1) = (lanes_max[len(lanes_max)-lanes_max_x + k][3][0] , lanes_max[len(lanes_max)-lanes_max_x + k][3][1])
                    (x5,y5) = (lanes_max[len(lanes_max)-lanes_max_x + k][0][0] , lanes_max[len(lanes_max)-lanes_max_x + k][0][1])

                    (x3,y3) = Intersection_Lines(lanes_min[len(lanes_min)-lanes_min_x+i],lanes_max[len(lanes_max)-lanes_max_x + k])

                    b = y1 - a*x1 # here we find the straight line equation of the lane going through (x1,y1) with an angle of h
                    y2bis = a*x2 + b  # if (x2,y2) is on the same lane than (x1,y1) (ie if the 2 lanes are in front of each other), then y2bis = y2

                    if round(y2,2) == round(y2bis,2): # if the 2 lanes are in front of each other, then i = i+1
                        i+=1


                    if len(lanes_before)>len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]


                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    k +=1
                (x4,y4) = (lanes_min[len(lanes_min)-lanes_min_x+i][0][0] , lanes_min[len(lanes_min)-lanes_min_x+i][0][1])
                (x2,y2) = (lanes_min[len(lanes_min)-lanes_min_x+i][3][0] , lanes_min[len(lanes_min)-lanes_min_x+i][3][1])
                while k<lanes_max_x :
                    (x1,y1) = (lanes_max[len(lanes_max)-lanes_max_x + k][3][0] , lanes_max[len(lanes_max)-lanes_max_x + k][3][1])
                    (x5,y5) = (lanes_max[len(lanes_max)-lanes_max_x + k][0][0] , lanes_max[len(lanes_max)-lanes_max_x + k][0][1])

                    (x3,y3) = Intersection_Lines(lanes_min[len(lanes_min)-lanes_min_x+i],lanes_max[len(lanes_max)-lanes_max_x + k])

                    if len(lanes_before)>len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]


                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    k +=1
            else :
                # This happens for example in this case :
                #
                #________________ __________________
                # 1 ->             I  ->
                # 2 <-             II ->
                # 3 <-             III <-
                # 4 <-             _________________
                #_________________
                #
                # here we globally remove lanes (there are less lanes after than before) but we add lanes in the x direction
                #
                while (k < lanes_max_x-1) and (i<lanes_min_x):
                    (x4,y4) = (lanes_min[len(lanes_min)-lanes_min_x+i][0][0] , lanes_min[len(lanes_min)-lanes_min_x+i][0][1])
                    (x2,y2) = (lanes_min[len(lanes_min)-lanes_min_x+i][3][0] , lanes_min[len(lanes_min)-lanes_min_x+i][3][1])

                    (x1,y1) = (lanes_max[len(lanes_max)-lanes_max_x + k][3][0] , lanes_max[len(lanes_max)-lanes_max_x + k][3][1])
                    (x5,y5) = (lanes_max[len(lanes_max)-lanes_max_x + k][0][0] , lanes_max[len(lanes_max)-lanes_max_x + k][0][1])

                    (x3,y3) = Intersection_Lines(lanes_min[len(lanes_min)-lanes_min_x+i],lanes_max[len(lanes_max)-lanes_max_x + k])

                    b = y1 - a*x1 # here we find the straight line equation of the lane going through (x1,y1) with an angle of h
                    y2bis = a*x2 + b  # if (x2,y2) is on the same lane than (x1,y1) (ie if the 2 lanes are in front of each other), then y2bis = y2

                    if round(y2,2) == round(y2bis,2): # if the 2 lanes are in front of each other, then i = i+1
                        i+=1


                    if len(lanes_before)>len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]


                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    k +=1

                (x1,y1) = (lanes_max[len(lanes_max)-lanes_max_x + k][3][0] , lanes_max[len(lanes_max)-lanes_max_x + k][3][1])
                (x5,y5) = (lanes_max[len(lanes_max)-lanes_max_x + k][0][0] , lanes_max[len(lanes_max)-lanes_max_x + k][0][1])
                while i<lanes_min_x :

                    (x4,y4) = (lanes_min[len(lanes_min)-lanes_min_x+i][0][0] , lanes_min[len(lanes_min)-lanes_min_x+i][0][1])
                    (x2,y2) = (lanes_min[len(lanes_min)-lanes_min_x+i][3][0] , lanes_min[len(lanes_min)-lanes_min_x+i][3][1])

                    (x3,y3) = Intersection_Lines(lanes_min[len(lanes_min)-lanes_min_x+i],lanes_max[len(lanes_max)-lanes_max_x + k])

                    if len(lanes_before)>len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]


                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    i +=1


        # Now we connect the lanes going in the opposite x direction (same as the x direction but we reverse everything)
        if (len(lanes_min) - lanes_min_x)== 1 :
            (x2,y2) = (lanes_min[0][3][0] , lanes_min[0][3][1])
            (x4,y4) = (lanes_min[0][0][0] , lanes_min[0][0][1])
            for k in range (len(lanes_max) - lanes_max_x):
                (x1,y1) = (lanes_max[k][3][0] , lanes_max[k][3][1])
                (x5,y5) = (lanes_max[k][0][0] , lanes_max[k][0][1])
                (x3,y3) = Intersection_Lines(lanes_min[0],lanes_max[k])

                if len(lanes_before)<len(lanes_after) :
                    xs1 = [x5, x1, x1, x3]
                    ys1 = [y5, y1, y1, y3]
                    xs2 = [x3, x4, x4, x2]
                    ys2 = [y3, y4, y4, y2]

                else :
                    xs1 = [x4, x2, x2, x3]
                    ys1 = [y4, y2, y2, y3]
                    xs2 = [x3, x5, x5, x1]
                    ys2 = [y3, y5, y5, y1]

                l1 = Curve(xs1, ys1, 0)
                l2 = Curve(xs2, ys2, 0)
                Current_Lane1 = []
                counter_addLine = -1
                for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                    if counter_addLine>-1 :
                        if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    else :
                        Current_Lane1.append([x, y])
                        counter_addLine+=1
                self.l.append(Current_Lane1)

                Current_Lane1 = []
                counter_addLine = -1
                for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                    if counter_addLine>-1 :
                        if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    else :
                        Current_Lane1.append([x, y])
                        counter_addLine+=1
                self.l.append(Current_Lane1)


        else :
            a =np.tan(h)
            k = len(lanes_max) - lanes_max_x-1
            i = len(lanes_min) - lanes_min_x-1
            if i <= k :
                while (k >-1) and (i>0):
                    (x2,y2) = (lanes_min[i][3][0] , lanes_min[i][3][1])
                    (x4,y4) = (lanes_min[i][0][0] , lanes_min[i][0][1])

                    (x1,y1) = (lanes_max[k][3][0] , lanes_max[k][3][1])
                    (x5,y5) = (lanes_max[k][0][0] , lanes_max[k][0][1])

                    (x3,y3) = Intersection_Lines(lanes_min[i],lanes_max[k])

                    b = y1 - a*x1
                    y2bis = a*x2 + b

                    if round(y2,4) == round(y2bis,4): # if the 2 lanes are in front of each other, then i = i+1
                        i-=1


                    if len(lanes_before)<len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]

                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    k -=1

                (x2,y2) = (lanes_min[i][3][0] , lanes_min[i][3][1])
                (x4,y4) = (lanes_min[i][0][0] , lanes_min[i][0][1])

                while k >-1:
                    (x1,y1) = (lanes_max[k][3][0] , lanes_max[k][3][1])
                    (x5,y5) = (lanes_max[k][0][0] , lanes_max[k][0][1])

                    (x3,y3) = Intersection_Lines(lanes_min[i],lanes_max[k])


                    if len(lanes_before)<len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]

                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    k -=1

            else :
                while (k >0) and (i>-1):
                    (x2,y2) = (lanes_min[i][3][0] , lanes_min[i][3][1])
                    (x4,y4) = (lanes_min[i][0][0] , lanes_min[i][0][1])

                    (x1,y1) = (lanes_max[k][3][0] , lanes_max[k][3][1])
                    (x5,y5) = (lanes_max[k][0][0] , lanes_max[k][0][1])

                    (x3,y3) = Intersection_Lines(lanes_min[i],lanes_max[k])

                    b = y1 - a*x1
                    y2bis = a*x2 + b

                    if round(y2,4) == round(y2bis,4): # if the 2 lanes are in front of each other, then i = i+1
                        i-=1


                    if len(lanes_before)<len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]

                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    k -=1

                (x1,y1) = (lanes_max[k][3][0] , lanes_max[k][3][1])
                (x5,y5) = (lanes_max[k][0][0] , lanes_max[k][0][1])

                while i >-1:

                    (x2,y2) = (lanes_min[i][3][0] , lanes_min[i][3][1])
                    (x4,y4) = (lanes_min[i][0][0] , lanes_min[i][0][1])

                    (x3,y3) = Intersection_Lines(lanes_min[i],lanes_max[k])


                    if len(lanes_before)<len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]

                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    i -=1



class EntryRoad(Road):
    '''
    This a representation of a entry road in Prescan.

    :param id: Unique id.
    :type id: String

    :param x0: The x coordinate of the center of the start of the road segment.
    :type x0: Float

    :param y0: The y coordinate of the center of the start of the road segment.
    :type y0: Float

    :param h: Global heading of the road segment at the start point.
    :type h: Float

    :param l: Length of the road segment
    :type l: Float

    :param lw: Lane width.
    :type lw: Float

    :param nbr_of_lanes: Number of lanes.
    :type nbr_of_lanes: Integer

    :param entry_road_angle: Entry Road Angle.
    :type entry_road_angle: Float

    :param apron_length: Apron Length.
    :type apron_length: Float

    :param side_road_length: Side Road Length.
    :type side_road_length: Float

    :param Stl: Tab of tabs contening relevant points (3 points per tab) describing a stopline
    :type Stl:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    :param cw: Tab of tabs contening relevant points (3 points per tab) describing the 3 lines describing a crosswalk
    :type cw:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    :param DefinedSpeed: Represent the speed that the road has per default (defined by the speedprofil in the Road Class)
    :type DefinedSpeed: Float

    '''
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes, lanes_going_OUT, entry_road_angle, apron_length, side_road_length, SpeedL, RefS, Stl, cw):

        # General Init

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.stopline = Stl
        self.crosswalk = cw
        self.DefinedSpeed = self.SpeedProfil[6]
        apron_length2=(apron_length*np.tan(entry_road_angle)+lw/2)/(np.tan(entry_road_angle))

        # Edges, Center Line and Lanes

        self.c.append(Straight( x0, y0, h, l))

        self.e1.append(Straight( x0 + lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2),
                                y0 + lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2), h, l))

        self.e2.append(Straight( x0 - lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2)+ (l-apron_length2) * np.cos(h),
                                y0 - lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2)+ (l-apron_length2) * np.sin(h), h-entry_road_angle, apron_length2))    # Entry part of edge 2

        self.e2.append(Straight( x0 - lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2),
                                y0 - lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2), h-entry_road_angle,l-apron_length2 ))  # Strainght part of edge 2

            # We are creating here every straight lanes that are not influenced by the new entry portion
            #
            #              _______________________  e1
            #              <---------------------
            #              <---------------------
            #              --------------------->
            #              --------------------->
            #
            #                     ________________  e2
            #                 __ /
            #              _/

        lwi=(nbr_of_lanes -1) * lw/2
        for _ in range(nbr_of_lanes-1):
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l))
            lwi -= lw



        # And after that we can create the last lane, which is the entry lane
        #
        #              ___________________________  e1
        #              <--------------------------
        #              <--------------------------
        #              -------------------------->
        #              -------------------------->
        #              --(1)-----------(2)------->
        #                 -- / ____________________  e2
        #           (3) -/ __ /
        #              ___/

        self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                y0 + lwi * np.sin(h + np.pi / 2),
                                h, apron_length2))              # Here we create (1)
        self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) + apron_length2 * np.cos(h),
                                y0 + lwi * np.sin(h + np.pi / 2) + apron_length2 * np.sin(h),
                                h, l-apron_length2))   # Then (2)

        self.l.append(Straight( x0 + (apron_length*np.tan(entry_road_angle)-lwi+lw/2)*np.sin(h),
                                y0 - (apron_length*np.tan(entry_road_angle)-lwi+lw/2)*np.cos(h),   # And finally (3)
                                entry_road_angle+h, (apron_length*np.tan(entry_road_angle)+lw/2)/np.sin(entry_road_angle)))

        #This changes the direction of the lanes that drive backwards
        if nbr_of_lanes-lanes_going_OUT>0:
            for i in range(nbr_of_lanes-lanes_going_OUT):
                l=[]
                for (x, y) in self.l[i]:
                    l.append([x, y])
                l = l[::-1]
                self.l[i] = l

class ExitRoad(Road):
    '''
    This a representation of a entry road in Prescan.

    :param id: Unique id.
    :type id: String

    :param x0: The x coordinate of the center of the start of the road segment.
    :type x0: Float

    :param y0: The y coordinate of the center of the start of the road segment.
    :type y0: Float

    :param h: Global heading of the road segment at the start point.
    :type h: Float

    :param l: Length of the road segment
    :type l: Float

    :param lw: Lane width.
    :type lw: Float

    :param nbr_of_lanes: Number of lanes.
    :type nbr_of_lanes: Integer

    :param exit_road_angle: Exit Road Angle.
    :type exit_road_angle: Float

    :param apron_length: Apron Length.
    :type apron_length: Float

    :param side_road_length: Side Road Length.
    :type side_road_length: Float

    :param Stl: Tab of tabs contening relevant points (3 points per tab) describing a stopline
    :type Stl:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    :param cw: Tab of tabs contening relevant points (3 points per tab) describing the 3 lines describing a crosswalk
    :type cw:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    :param DefinedSpeed: Represent the speed that the road has per default (defined by the speedprofil in the Road Class)
    :type DefinedSpeed: Float

    '''
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes, lanes_going_OUT, exit_road_angle, apron_length, side_road_length, SpeedL, RefS, Stl, cw):

        # General Init

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.stopline = Stl
        self.crosswalk = cw
        self.DefinedSpeed = self.SpeedProfil[7]
        apron_length2=(apron_length*np.tan(exit_road_angle)+lw/2)/(np.tan(exit_road_angle))

        # Edges, Center Line and Lanes

        self.c.append(Straight( x0, y0, h, l))

        self.e1.append(Straight( x0 + lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2),
                                y0 + lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2), h, l))

        self.e2.append(Straight( x0 - lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2),
                                y0 - lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2), h,apron_length2))   # Straight part of edge 2

        self.e2.append(Straight( x0 - lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2)+ (l-apron_length2) * np.cos(h),
                                y0 - lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2)+ (l-apron_length2) * np.sin(h), h-exit_road_angle,(l-apron_length2-1)*np.cos(h-exit_road_angle) ))    # Exit part of edge 2


        # We are creating here every straight lanes that are not influenced by the new exit portion
        #
        #              _______________________  e1
        #              <---------------------
        #              <---------------------
        #              --------------------->
        #              --------------------->
        #
        #              ________________
        #                              \__
        #                                 \___  e2


        lwi=(nbr_of_lanes -1) * lw/2
        for _ in range(nbr_of_lanes-1):
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l))
            lwi -= lw


        # And after that we can create the last lane, which is the exit lane
        #
        #              _______________________  e1
        #              <---------------------
        #              <---------------------
        #              --------------------->
        #              --------------------->
        #              -----(1)-------------> (2)
        #              ________________  \ (3)
        #                              \__ -->
        #                                 \___  e2

        self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                y0 + lwi * np.sin(h + np.pi / 2),
                                h, l-apron_length2))        # We create (1) here
        self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) + (l-apron_length2) * np.cos(h),
                                y0 + lwi * np.sin(h + np.pi / 2) + (l-apron_length2) * np.sin(h),
                                h, apron_length2))    # Then (2)
        self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) + (l-apron_length2) * np.cos(h),
                                y0 + lwi * np.sin(h + np.pi / 2) + (l-apron_length2) * np.sin(h),
                                h-exit_road_angle, (apron_length*np.tan(exit_road_angle)+lw/2)/np.sin(exit_road_angle)))  # And finally (3)

        #This changes the direction of the lanes that drive backwards
        if nbr_of_lanes-lanes_going_OUT>0:
            for i in range(nbr_of_lanes-lanes_going_OUT):
                l=[]
                for (x, y) in self.l[i]:
                    l.append([x, y])
                l = l[::-1]
                self.l[i] = l



class XCrossRoad(Road):
    '''
    This a representation of an xcrossing road in Prescan. Each road contains one segment for each arm of the xcrossing.

    :param id: Unique id.
    :type id: String

    :param x0: The x coordinate of the center of the road segment.
    :type x0: Float

    :param y0: The y coordinate of the center of the road segment.
    :type y0: Float

    :param h: Global heading of the road segment at the starting point.
    :type h: Float

    :param r: Distance from the starting point to furthest center point of one of the lanes.
    :type r: Float

    :param lw: Lane width.
    :type lw: Float

    :param chs: List of headings for each arm of the xcrossing.
    :type chs: [Float]

    :param len_till_stop: Distance from endpoint of the arms to the arms' stopline.
    :type len_till_stop: Float

    :param nbr_of_lanes: Number of lanes.
    :type nbr_of_lanes: Integer

    :param cw: Tab of tabs contening relevant points (3 points per tab) describing the 3 lines describing a crosswalk
    :type cw:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    '''
    def __init__(self, id, x0, y0, h, lw, cs_h, cs_len_till_stop, cs_nbr_of_lanes, cs_lanes_going_OUT, cs_l, SpeedL, RefS, Stl, cw):

        # General Init

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.x=x0
        self.y=y0
        self.stopline = Stl
        self.DefinedSpeed = self.SpeedProfil[8]
        self.crosswalk = cw

        # Lanes Creation

        # Creation of each "Starting Lane"

        counter = 0

        for c in range(4):  # For each Branch of the X Crossing


            nb_of_lanes = cs_nbr_of_lanes[c]
            lanes_going_OUT = cs_lanes_going_OUT[c]
            lwi=(cs_nbr_of_lanes[c] -1) * lw/2
            next_first_lane = counter             # Allow us the access to the first lane created that need to be reversed

            for lane in range(nb_of_lanes):

                l1 = Straight(x0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.cos(cs_h[c]+h) + (lwi)*np.cos(cs_h[c]+h+ np.pi / 2), y0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.sin(cs_h[c]+h) + (lwi)*np.sin(cs_h[c]+h+ np.pi / 2), cs_h[c]+h, (cs_len_till_stop[c]+1))

                Current_Lane = []  # This convert the lane from a path obj to a tab of point
                for (x,y) in l1:
                    Current_Lane.append([x, y])

                self.l.append(Current_Lane[1:])

                lwi -= lw
                counter += 1

            # We are creating here the straight part of the lane at the beginning of each crosssection from the stopline to
            # the beggining of the road in the following order (1 : a -> b then 2->3->4)
            #
            #                     #        #
            #                     #    2   #
            #                     #        #
            #                ######        #######
            #                             a) |---->
            #                   3               1
            #                             b)  ---->
            #                #######       ########
            #                      #       #
            #                      #   4   #
            #                      #       #
            #
            # We need now to change the direction of the lanes that drive backwards


            # Changing the direction of the lanes that drive backwards

            if nb_of_lanes-lanes_going_OUT>0:
                for j in range(nb_of_lanes-lanes_going_OUT):
                    l=[]
                    for (x, y) in self.l[next_first_lane + j]:
                        l.append([x, y])
                    l = l[::-1]
                    self.l[next_first_lane + j] = l



        # Creating every connections between each starting lanes

        # We will now link each crossections of the x crossing
        #
        #                     #      | #
        #                     #    2 | #
        #                     #      | #
        #                ######      | #######
        #                <----------------|----
        #                   3    |          1
        #                        |    b)  ---->
        #                ####### |     ########
        #                      # |     #
        #                      # | 4   #
        #                      # |     #
        #
        #
        # In order to understand the implentation of this next part, please read the comment AND the wiki dedicated to this RT


        total_nb_of_lanes = 0   # This will be usefull to create a counter that can circle back to the beggining of the lane list (see below)
        Number_of_lanes_going_IN = [] #lanes heading towards the center of the crossroad
        Index_lanes_going_out = []
        Index_lanes_going_in = []

        for i in range(4):
            Index_lanes_going_out_local = []
            Index_lanes_going_in_local = []
            nb_of_lanes = cs_nbr_of_lanes[i]
            lanes_going_OUT = cs_lanes_going_OUT[i]

            if lanes_going_OUT > 0 : # here we save the index in self.l of the lanes driving out of the crossroad
                if nb_of_lanes == lanes_going_OUT :
                    for k in range (nb_of_lanes):
                        Index_lanes_going_out_local.append(total_nb_of_lanes+k)
                else :
                    for k in range (lanes_going_OUT) :
                        Index_lanes_going_out_local.append(total_nb_of_lanes+k + (nb_of_lanes-lanes_going_OUT))

            for k in range (nb_of_lanes): # here we save the index in self.l of the lanes going in the crossroad
                if (k+total_nb_of_lanes) not in Index_lanes_going_out_local :
                    Index_lanes_going_in_local.append(k + total_nb_of_lanes)

            total_nb_of_lanes += nb_of_lanes

            Number_of_lanes_going_IN.append(nb_of_lanes - lanes_going_OUT)
            Index_lanes_going_in.append(Index_lanes_going_in_local)
            Index_lanes_going_out.append(Index_lanes_going_out_local)

        count_lanes_going_IN =0


        for m in range(4):  # For each Branch of the X Crossing
            if Number_of_lanes_going_IN[m] !=0 :  # if there are lanes going in the opposite x direction


                nb_of_lanes = cs_nbr_of_lanes[m]
                lanes_going_OUT = cs_lanes_going_OUT[m]
                counter_remaining_lanes = nb_of_lanes - lanes_going_OUT

                lanes_going_IN = []
                for k in range (len(Index_lanes_going_in[m])):
                    lanes_going_IN.append(self.l[Index_lanes_going_in[m][k]])  # Lanes going in the crossroad that we will link to the roads going out of the crossroad


                Lane_available_for_connection = []
                Lane_available_for_connection_right = []
                Lane_available_for_connection_left = []
                for p in range(4):
                    if p != m :
                        for k in range (len(Index_lanes_going_out[p])) :
                            Lane_available_for_connection.append(self.l[Index_lanes_going_out[p][k]])




                if Number_of_lanes_going_IN[m] == 1 :  # If we have only one lane going in the crossroad

                    for r in range(len(Lane_available_for_connection)): # We connect the Only Lane of interest to EVERY lane avaible for conections

                        (x1,y1) = lanes_going_IN[0][len(lanes_going_IN[0])-1]

                        (x2,y2) = Lane_available_for_connection[r][0]

                        (x3,y3) = Intersection_Lines(lanes_going_IN[0],Lane_available_for_connection[r])

                        # here we check if (x3,y3) is on lanes_going_IN[0] (or Lane_available_for_connection[r])
                        # if it is, (x1,y1) (or (x3,y3)) will be the point after (respectively the point before) on the lanes
                        # so that the curve created will be smoother

                        k2=0
                        while k2<len(Lane_available_for_connection[r]) :
                            p2 = Lane_available_for_connection[r][k2]
                            if dist(p2,(x3,y3))<0.5 :
                                (x2,y2) = Lane_available_for_connection[r][k2+1]
                                k2=len(Lane_available_for_connection[r])
                            k2+=1

                        k1=len(lanes_going_IN[0])-1
                        while k1>0 :
                            p1 = lanes_going_IN[0][k1]
                            if dist(p1,(x3,y3))<0.5 :
                                (x1,y1) = lanes_going_IN[0][k1-1]
                                k1=-1
                            k1=k1-1


                        xs = [x1, x3, x3, x2]
                        ys = [y1, y3, y3, y2]

                        l1 = Curve(xs, ys, 0)
                        Current_Lane1 = []
                        counter_addLine = -1
                        for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                            if counter_addLine>-1 :
                                if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                    Current_Lane1.append([x, y])
                                    counter_addLine+=1
                            else :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        self.l.append(Current_Lane1)


                else :

                    Lane_available_for_connection_right = Lane_available_for_connection[0:cs_lanes_going_OUT[(m+1)%3]]
                    Lane_available_for_connection_left = Lane_available_for_connection[cs_lanes_going_OUT[(m+1)%3]:cs_lanes_going_OUT[(m+1)%3]+cs_lanes_going_OUT[(m+2)%3]]

                    if Lane_available_for_connection_left == [] : #If one of the lists is empty then the lanes of interest will be connected to the samme lanes
                        Lane_available_for_connection_left = Lane_available_for_connection_right
                    elif Lane_available_for_connection_right == [] :
                        Lane_available_for_connection_right = Lane_available_for_connection_left

                    # We will create a more specific list out of list 2 (that contains every lanes available for connections
                    # Lane available for connection left in whih you'll have every lane locatrd on the crossection to the left
                    # And Lane available for connection right will is the same but for the lanes located on the corssection to the right

                    if len(lanes_going_IN)%2 !=0: # If there is an odd numbers of lanes then list 2 will be broken into the 2 list right/left and the raminaing lane will be had to the list that have less lanes
                        lanes_going_IN_right = lanes_going_IN[0:(len(lanes_going_IN)//2)+1]
                        lanes_going_IN_left = lanes_going_IN[(len(lanes_going_IN)//2)+1:]

                        if len(Lane_available_for_connection_right) > len(Lane_available_for_connection_left):
                            lanes_going_IN_right.append(lanes_going_IN[int((len(lanes_going_IN)-1)//2)])
                        elif len(Lane_available_for_connection_left) > len(Lane_available_for_connection_right):
                            lanes_going_IN_left.append(lanes_going_IN[int((len(lanes_going_IN)-1)//2)])
                        else :
                            lanes_going_IN_right.append(lanes_going_IN[int((len(lanes_going_IN)-1)//2)])

                    else :
                        lanes_going_IN_right = lanes_going_IN[0:int((len(lanes_going_IN)-1)//2)+1]
                        lanes_going_IN_left = lanes_going_IN[int((len(lanes_going_IN)-1)//2)+1:]



                    for q in range(len(lanes_going_IN_right)):  # Right side of X Crossing

                        # The list now created we make every connections
                        # And we will proceed that way
                        #
                        #                     |      |       |
                        #                     |      |       |
                        # Lanes in list 2 :   |      |       |
                        #                     |      |       |
                        #                    (a2)   (b2)    (c2)
                        #                        |       |
                        #                        |       |
                        # Lanes in list 1 :      |       |
                        #                        |       |
                        #                       (a1)    (b1)
                        #
                        # a1 to a2, and b1 to b2 and c2
                        # If List 1 had three lanes then a1 to a2, b1 to b2, c1 to c2

                        for j in range(len(Lane_available_for_connection_right)):

                            (x1,y1) = lanes_going_IN_right[q][len(lanes_going_IN_right[q])-1]

                            (x2,y2) = Lane_available_for_connection_right[j][0]

                            (x3,y3) = Intersection_Lines(lanes_going_IN_right[q], Lane_available_for_connection_right[j])

                            k2=0
                            while k2<len(Lane_available_for_connection_right[j]) :
                                p2 = Lane_available_for_connection_right[j][k2]
                                if dist(p2,(x3,y3))<0.5 :
                                    (x2,y2) = Lane_available_for_connection_right[j][k2+1]
                                    k2=len(Lane_available_for_connection_right[j])
                                k2+=1

                            k1=len(lanes_going_IN_right[0])-1
                            while k1>0 :
                                p1 = lanes_going_IN_right[q][k1]
                                if dist(p1,(x3,y3))<0.5 :
                                    (x1,y1) = lanes_going_IN_right[q][k1-1]
                                    k1=-1
                                k1=k1-1

                            xs = [x1, x3, x3, x2]
                            ys = [y1, y3, y3, y2]

                            l1 = Curve(xs, ys, 0)
                            Current_Lane1 = []
                            counter_addLine = -1
                            for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                                if counter_addLine>-1 :
                                    if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                        Current_Lane1.append([x, y])
                                        counter_addLine+=1
                                else :
                                    Current_Lane1.append([x, y])
                                    counter_addLine+=1
                            self.l.append(Current_Lane1)





                    for q in range(len(lanes_going_IN_left)):  # Left side of X Crossing
                        # Same working but for the left
                        for j in range(len(Lane_available_for_connection_left)):

                            (x1,y1) = lanes_going_IN_left[q][len(lanes_going_IN_left[q])-1]

                            (x2,y2) = Lane_available_for_connection_left[j][0]

                            (x3,y3) = Intersection_Lines(lanes_going_IN_left[q], Lane_available_for_connection_left[j])

                            k2=0
                            while k2<len(Lane_available_for_connection_left[j]) :
                                p2 = Lane_available_for_connection_left[j][k2]
                                if dist(p2,(x3,y3))<0.5 :
                                    (x2,y2) = Lane_available_for_connection_left[j][k2+1]
                                    k2=len(Lane_available_for_connection_left[j])
                                k2+=1

                            k1=len(lanes_going_IN_left[0])-1
                            while k1>0 :
                                p1 = lanes_going_IN_left[q][k1]
                                if dist(p1,(x3,y3))<0.5 :
                                    (x1,y1) = lanes_going_IN_left[q][k1-1]
                                    k1=-1
                                k1=k1-1

                            xs = [x1, x3, x3, x2]
                            ys = [y1, y3, y3, y2]


                            l1 = Curve(xs, ys, 0)
                            Current_Lane1 = []
                            counter_addLine = -1
                            for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                                if counter_addLine>-1 :
                                    if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                        Current_Lane1.append([x, y])
                                        counter_addLine+=1
                                else :
                                    Current_Lane1.append([x, y])
                                    counter_addLine+=1
                            self.l.append(Current_Lane1)




            count_lanes_going_IN += cs_nbr_of_lanes[m]

        # Edges

        # TO DO


    def getstart(self):
        return (self.x, self.y)

    def getend(self):
        return (self.x, self.y)


class YCrossRoad(Road):
    '''
    This a representation of an ycrossing road in Prescan. Each road contains one segment for each arm of the ycrossing.

    :param id: Unique id.
    :type id: String

    :param x0: The x coordinate of the center of the road segment.
    :type x0: Float

    :param y0: The y coordinate of the center of the road segment.
    :type y0: Float

    :param h: Global heading of the road segment at the starting point.
    :type h: Float

    :param r: Distance from the starting point to furthest center point of one of the lanes.
    :type r: Float

    :param lw: Lane width.
    :type lw: Float

    :param chs: List of headings for each arm of the xcrossing.
    :type chs: [Float]

    :param len_till_stop: Distance from endpoint of the arms to the arms' stopline.
    :type len_till_stop: Float

    :param nbr_of_lanes: Number of lanes.
    :type nbr_of_lanes: Integer

    :param cw: Tab of tabs contening relevant points (3 points per tab) describing the 3 lines describing a crosswalk
    :type cw:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    '''
    def __init__(self, id, x0, y0, h, lw, cs_h, cs_len_till_stop, cs_nbr_of_lanes, cs_lanes_going_OUT, cs_l, SpeedL, RefS, Stl, cw):

        # General Init

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.x=x0
        self.y=y0
        self.stopline = Stl
        self.DefinedSpeed = self.SpeedProfil[9]
        self.crosswalk = cw

        # Lanes Creation

        # Creation of each "Starting Lane"

        counter = 0

        for c in range(3):  # For each Branch of the Y Crossing


            nb_of_lanes = cs_nbr_of_lanes[c]
            lanes_going_OUT = cs_lanes_going_OUT[c]
            lwi=(cs_nbr_of_lanes[c] -1) * lw/2
            next_first_lane = counter             # Allow us the access to the first lane created that need to be reversed

            for lane in range(nb_of_lanes):

                l1 = Straight(x0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.cos(cs_h[c]+h) + (lwi)*np.cos(cs_h[c]+h+ np.pi / 2), y0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.sin(cs_h[c]+h) + (lwi)*np.sin(cs_h[c]+h+ np.pi / 2), cs_h[c]+h, (cs_len_till_stop[c]+1))

                Current_Lane = []  # This convert the lane from a path obj to a tab of point
                for (x,y) in l1:
                    Current_Lane.append([x, y])

                self.l.append(Current_Lane[1:])

                lwi -= lw
                counter += 1

            # We are creating here the straight part of the lane at the beginning of each crosssection from the stopline to
            # the beggining of the road in the following order (1 : a -> b then 2->3)
            #
            #
            #                ######################
            #                             a) |---->
            #                   2               1
            #                             b)  ---->
            #                #######       ########
            #                      #       #
            #                      #   3   #
            #                      #       #
            #
            # We need now to change the direction of the lanes that drive backwards


            # Changing the direction of the lanes that drive backwards

            if nb_of_lanes-lanes_going_OUT>0:
                for j in range(nb_of_lanes-lanes_going_OUT):
                    l=[]
                    for (x, y) in self.l[next_first_lane + j]:
                        l.append([x, y])
                    l = l[::-1]
                    self.l[next_first_lane + j] = l

        # Stoplines Creation




        # Creating every connections between each starting lanes

        # We will now link each crossections of the y crossing
        #
        #                ######################
        #                <----------------|----
        #                   2    |          1
        #                        |    b)  ---->
        #                ####### |     ########
        #                      # |     #
        #                      # | 3   #
        #                      # |     #
        #
        #
        # In order to understand the implentation of this next part, please read the comment AND the wiki dedicated to this RT



        total_nb_of_lanes = 0   # This will be usefull to create a counter that can circle back to the beggining of the lane list (see below)
        Number_of_lanes_going_IN = [] #lanes heading towards the center of the crossroad
        Index_lanes_going_out = []
        Index_lanes_going_in = []
        for i in range(3):
            Index_lanes_going_out_local = []
            Index_lanes_going_in_local = []
            nb_of_lanes = cs_nbr_of_lanes[i]
            lanes_going_OUT = cs_lanes_going_OUT[i]

            if lanes_going_OUT > 0 : # here we save the index in self.l of the lanes driving in the x dir
                if nb_of_lanes == lanes_going_OUT :
                    for k in range (nb_of_lanes):
                        Index_lanes_going_out_local.append(total_nb_of_lanes+k)
                else :
                    for k in range (lanes_going_OUT) :
                        Index_lanes_going_out_local.append(total_nb_of_lanes+k + (nb_of_lanes-lanes_going_OUT))

            for k in range (nb_of_lanes):
                if (k+total_nb_of_lanes) not in Index_lanes_going_out_local :
                    Index_lanes_going_in_local.append(k + total_nb_of_lanes)

            total_nb_of_lanes += nb_of_lanes

            Number_of_lanes_going_IN.append(nb_of_lanes - lanes_going_OUT)
            Index_lanes_going_in.append(Index_lanes_going_in_local)
            Index_lanes_going_out.append(Index_lanes_going_out_local)

        count_lanes_going_IN =0

        for m in range(3): # For each corssections

            # We will proceed by doing two list for each crossection :
            # The first list will list every lanes going in the right direction on the current crossections
            # The second list will contain every relevant lanes that can be linked to the lane that are in the first list
            #
            #
            #                ######################
            #                ----- (c)        ----- (a)
            #                   2               1
            #                ----- (d)        ----- (b)
            #                #######       ########
            #                      # |   | #
            #                      # | 3 | #
            #                      # |   | #
            #                       (e) (f)
            #
            # So here for instance for crossection one , list 1 = [Lane a]
            # and List 2 = [Lane c,Lane e]
            #

            if Number_of_lanes_going_IN[m] !=0 :  # if there are lanes going in the opposite x direction


                nb_of_lanes = cs_nbr_of_lanes[m]
                lanes_going_OUT = cs_lanes_going_OUT[m]
                counter_remaining_lanes = nb_of_lanes - lanes_going_OUT

                lanes_going_IN = []
                for k in range (len(Index_lanes_going_in[m])):
                    lanes_going_IN.append(self.l[Index_lanes_going_in[m][k]])  # Lanes going in the crossroad that we will link to the roads going out of the crossroad


                Lane_available_for_connection = []
                Lane_available_for_connection_right = []
                Lane_available_for_connection_left = []
                for p in range(3):
                    if p != m :
                        for k in range (len(Index_lanes_going_out[p])) :
                            Lane_available_for_connection.append(self.l[Index_lanes_going_out[p][k]])




                if Number_of_lanes_going_IN[m] == 1 :  # If we have only one lane going in the crossroad

                    for r in range(len(Lane_available_for_connection)): # We connect the Only Lane of interest to EVERY lane avaible for conections

                        (x1,y1) = lanes_going_IN[0][len(lanes_going_IN[0])-1]

                        (x2,y2) = Lane_available_for_connection[r][0]

                        (x3,y3) = Intersection_Lines(lanes_going_IN[0],Lane_available_for_connection[r])

                        # here we check if (x3,y3) is on lanes_going_IN[0] or Lane_available_for_connection[r]
                        # if it is, (x1,y1) (or (x3,y3)) will be the point after (respectively the point before) on the lanes
                        # so that the curve created will be smoother

                        k2=0
                        while k2<len(Lane_available_for_connection[r]) :
                            p2 = Lane_available_for_connection[r][k2]
                            if dist(p2,(x3,y3))<0.5 :
                                (x2,y2) = Lane_available_for_connection[r][k2+1]
                                k2=len(Lane_available_for_connection[r])
                            k2+=1

                        k1=len(lanes_going_IN[0])-1
                        while k1>0 :
                            p1 = lanes_going_IN[0][k1]
                            if dist(p1,(x3,y3))<0.5 :
                                (x1,y1) = lanes_going_IN[0][k1-1]
                                k1=-1
                            k1=k1-1


                        xs = [x1, x3, x3, x2]
                        ys = [y1, y3, y3, y2]

                        l1 = Curve(xs, ys, 0)
                        Current_Lane1 = []
                        counter_addLine = -1
                        for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                            if counter_addLine>-1 :
                                if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                    Current_Lane1.append([x, y])
                                    counter_addLine+=1
                            else :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        self.l.append(Current_Lane1)


                else :

                    Lane_available_for_connection_right = Lane_available_for_connection[0:cs_lanes_going_OUT[(m+1)%3]]
                    Lane_available_for_connection_left = Lane_available_for_connection[cs_lanes_going_OUT[(m+1)%3]:cs_lanes_going_OUT[(m+1)%3]+cs_lanes_going_OUT[(m+2)%3]]

                    if Lane_available_for_connection_left == [] : #If one of the lists is empty then the lanes of interest will be connected to the samme lanes
                        Lane_available_for_connection_left = Lane_available_for_connection_right
                    elif Lane_available_for_connection_right == [] :
                        Lane_available_for_connection_right = Lane_available_for_connection_left

                    # We will create a more specific list out of list 2 (that contains every lanes available for connections
                    # Lane available for connection left in whih you'll have every lane locatrd on the crossection to the left
                    # And Lane available for connection right will is the same but for the lanes located on the corssection to the right

                    if len(lanes_going_IN)%2 !=0: # If there is an odd numbers of lanes then list 2 will be broken into the 2 list right/left and the raminaing lane will be had to the list that have less lanes
                        lanes_going_IN_right = lanes_going_IN[0:(len(lanes_going_IN)//2)+1]
                        lanes_going_IN_left = lanes_going_IN[(len(lanes_going_IN)//2)+1:]

                        if len(Lane_available_for_connection_right) > len(Lane_available_for_connection_left):
                            lanes_going_IN_right.append(lanes_going_IN[int((len(lanes_going_IN)-1)//2)])
                        elif len(Lane_available_for_connection_left) > len(Lane_available_for_connection_right):
                            lanes_going_IN_left.append(lanes_going_IN[int((len(lanes_going_IN)-1)//2)])
                        else :
                            lanes_going_IN_right.append(lanes_going_IN[int((len(lanes_going_IN)-1)//2)])

                    else :
                        lanes_going_IN_right = lanes_going_IN[0:int((len(lanes_going_IN)-1)//2)+1]
                        lanes_going_IN_left = lanes_going_IN[int((len(lanes_going_IN)-1)//2)+1:]



                    for q in range(len(lanes_going_IN_right)):  # Right side of Y Crossing

                        # The list now created we make every connections
                        # And we will proceed that way
                        #
                        #                     |      |       |
                        #                     |      |       |
                        # Lanes in list 2 :   |      |       |
                        #                     |      |       |
                        #                    (a2)   (b2)    (c2)
                        #                        |       |
                        #                        |       |
                        # Lanes in list 1 :      |       |
                        #                        |       |
                        #                       (a1)    (b1)
                        #
                        # a1 to a2, and b1 to b2 and c2
                        # If List 1 had three lanes then a1 to a2, b1 to b2, c1 to c2

                        for j in range(len(Lane_available_for_connection_right)):

                            (x1,y1) = lanes_going_IN_right[q][len(lanes_going_IN_right[q])-1]

                            (x2,y2) = Lane_available_for_connection_right[j][0]

                            (x3,y3) = Intersection_Lines(lanes_going_IN_right[q], Lane_available_for_connection_right[j])

                            k2=0
                            while k2<len(Lane_available_for_connection_right[j]) :
                                p2 = Lane_available_for_connection_right[j][k2]
                                if dist(p2,(x3,y3))<0.5 :
                                    (x2,y2) = Lane_available_for_connection_right[j][k2+1]
                                    k2=len(Lane_available_for_connection_right[j])
                                k2+=1

                            k1=len(lanes_going_IN_right[0])-1
                            while k1>0 :
                                p1 = lanes_going_IN_right[q][k1]
                                if dist(p1,(x3,y3))<0.5 :
                                    (x1,y1) = lanes_going_IN_right[q][k1-1]
                                    k1=-1
                                k1=k1-1

                            xs = [x1, x3, x3, x2]
                            ys = [y1, y3, y3, y2]

                            l1 = Curve(xs, ys, 0)
                            Current_Lane1 = []
                            counter_addLine = -1
                            for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                                if counter_addLine>-1 :
                                    if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                        Current_Lane1.append([x, y])
                                        counter_addLine+=1
                                else :
                                    Current_Lane1.append([x, y])
                                    counter_addLine+=1
                            self.l.append(Current_Lane1)





                    for q in range(len(lanes_going_IN_left)):  # Left side of Y Crossing
                        # Same working but for the left
                        for j in range(len(Lane_available_for_connection_left)):

                            (x1,y1) = lanes_going_IN_left[q][len(lanes_going_IN_left[q])-1]

                            (x2,y2) = Lane_available_for_connection_left[j][0]

                            (x3,y3) = Intersection_Lines(lanes_going_IN_left[q], Lane_available_for_connection_left[j])

                            k2=0
                            while k2<len(Lane_available_for_connection_left[j]) :
                                p2 = Lane_available_for_connection_left[j][k2]
                                if dist(p2,(x3,y3))<0.5 :
                                    (x2,y2) = Lane_available_for_connection_left[j][k2+1]
                                    k2=len(Lane_available_for_connection_left[j])
                                k2+=1

                            k1=len(lanes_going_IN_left[0])-1
                            while k1>0 :
                                p1 = lanes_going_IN_left[q][k1]
                                if dist(p1,(x3,y3))<0.5 :
                                    (x1,y1) = lanes_going_IN_left[q][k1-1]
                                    k1=-1
                                k1=k1-1

                            xs = [x1, x3, x3, x2]
                            ys = [y1, y3, y3, y2]


                            l1 = Curve(xs, ys, 0)
                            Current_Lane1 = []
                            counter_addLine = -1
                            for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                                if counter_addLine>-1 :
                                    if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                        Current_Lane1.append([x, y])
                                        counter_addLine+=1
                                else :
                                    Current_Lane1.append([x, y])
                                    counter_addLine+=1
                            self.l.append(Current_Lane1)




            count_lanes_going_IN += cs_nbr_of_lanes[m]



    def getstart(self):
        return (self.x, self.y)

    def getend(self):
        return (self.x, self.y)
