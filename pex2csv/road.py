'''This module contains all of the code defining the structure of different road segments. By taking initial values from the parser the classes calculate a mathematical definition of the road type. So We use the geometry created in path.py to define the different roadtype (ex: we use Bend type to create Roundabout)

The road classes :class:'BendRoad', :class:'CurvedRoad', :class:'StraightRoad', :class:'RoundaboutRoad', and :class:'XCrossing' all have class variables that represent roads.

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

    :param lanes_in_x_dir: Number of lanes in the x direction. Used to reverse the lane that goes in the x direction
    :type lanes_in_x_dir: Integer

    :param Stl: Tab of tabs contening relevant points (3 points per tab) describing a stopline
    :type Stl:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    :param DefinedSpeed: Represent the speed that the road has per default (defined by the speedprofil in the Road Class)
    :type DefinedSpeed: Float

    '''
    def __init__(self, id, x0, y0, h, rh, clr, lw, nbr_of_lanes, lanes_in_x_dir, SpeedL, RefS, Stl):

        # General Initialization

        Road.__init__(self, id)     #Gave the Id linked to BendRoad
        self.SpeedLimit = SpeedL    #Set the different speeds
        self.RefSpeed = RefS
        self.stopline = Stl
        self.DefinedSpeed = self.SpeedProfil[1]


        # Lanes, Center and Edges of the Road

        self.c.append(Bend( x0, y0, h, rh, clr))

        self.e1.append(Bend( x0 - lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2),      #Buggy FIX HERE for Object/Tab PB
                        y0 + lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2),
                        h, rh, clr - np.sign(rh) * lw * lanes_in_x_dir))

        self.e2.append(Bend( x0 - lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2),      #Same
                        y0 - lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2),
                        h, rh, clr + np.sign(rh) * lw * (nbr_of_lanes -lanes_in_x_dir)))

        lwi = (nbr_of_lanes - 1) * lw                                         #This work. To better understand how, i recommand doing this code by hand in a simple case
        for _ in range(nbr_of_lanes):
            self.l.append(Bend( x0 + lwi * np.cos(h + np.pi / 2) / 2,
                                y0 + lwi * np.sin(h + np.pi / 2) / 2,
                               h, rh, clr - np.sign(rh) * lwi / 2))
            lwi -= 2 * lw

        #This changes the direction of the lanes that drive backwards
        if nbr_of_lanes-lanes_in_x_dir>0:
            for i in range(nbr_of_lanes-lanes_in_x_dir):
                l=[]
                for (x, y) in self.l[i]:
                    l.append([x, y])
                l = l[::-1]
                self.l[i] = l


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

    :param lanes_in_x_dir: Number of lanes in the x direction. Used to reverse the lane that goes in the x direction
    :type nbr_of_lanes: Integer

    :param Stl: Tab of tabs contening relevant points (3 points per tab) describing a stopline
    :type Stl:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    :param DefinedSpeed: Represent the speed that the road has per default (defined by the speedprofil in the Road Class)
    :type DefinedSpeed: Float

    '''
    def __init__(self, id, x0, y0, h, rh, cp1, cp2, dx, dy, lw, nbr_of_lanes, lanes_in_x_dir, SpeedL, RefS, Stl): #Same as BendRoad

        # General Initialization

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.stopline = Stl
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
            self.l.append(Curve(xs, ys, lwi))
            lwi += lw

        #This changes the direction of the lanes that drive backwards
        if nbr_of_lanes-lanes_in_x_dir>0:
            for i in range(nbr_of_lanes-lanes_in_x_dir):
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

    '''
    def __init__(self, id, x0, y0, r, lw, cs_h, cs_filletradius, cs_nb_of_lanes, cs_nb_of_lane_x_direction, nbr_of_lanes, SpeedL, RefS, TabConnect):

        # General Initialization

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.TabConnect = TabConnect
        self.DefinedSpeed = self.SpeedProfil[3]

        # Creating every circles

        lwhalf = lw/2
        r1 = r
        for i in range(nbr_of_lanes):
            l1 =Bend( x0, y0 - (r1 - lwhalf), 0, 2 * np.pi, r1 - lwhalf)
            r1 = (r1 - lw)
            Actual_Lane1 = []
            for (x,y) in l1:
                Actual_Lane1.append([x, y])
            self.l.append(Actual_Lane1)



        # Creation of Exit and entry lane

        for j in range(4):

            nb_of_lanes = cs_nb_of_lanes[j]
            nb_of_lanes_x_direction = cs_nb_of_lane_x_direction[j]
            nb_of_lanes_of_interest = nb_of_lanes - nb_of_lanes_x_direction
            fillet_radius = cs_filletradius[j]

            # Creation of the 2 starting points

            starting_point = TabConnect[j]
            print(starting_point)
            starting_point_right = (starting_point[0][0]- (nb_of_lanes/2)*lw*np.sin(cs_h[j]),starting_point[0][1] + (nb_of_lanes/2)*lw*np.cos(cs_h[j]))
            starting_point_left = (starting_point[0][0]+ (nb_of_lanes/2)*lw*np.sin(cs_h[j]),starting_point[0][1] - (nb_of_lanes/2)*lw*np.cos(cs_h[j]))


            # Entry access


            counter =0
            for k in range(nb_of_lanes_of_interest):


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
                Actual_Lane1 = []
                for (x,y) in l1:
                    Actual_Lane1.append([x, y])
                counter +=1
                self.l.append(Actual_Lane1)



            # Exit access

            # Same expect tfor the math
            counter =0
            for p in range(nb_of_lanes_x_direction):


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
                Actual_Lane1 = []
                for (x,y) in l1:
                    Actual_Lane1.append([x, y])


                self.l.append(Actual_Lane1)
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

    '''
    def __init__(self, id, x0, y0, r, lw, ch, nbr_of_lanes, SpeedL, RefS):

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

    :param DefinedSpeed: Represent the speed that the road has per default (defined by the speedprofil in the Road Class)
    :type DefinedSpeed: Float

    '''
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, SpeedL, RefS, Stl):

        # General Init

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.stopline = Stl
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
        if nbr_of_lanes-lanes_in_x_dir>0:
            for i in range(nbr_of_lanes-lanes_in_x_dir):
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

    :param lanes_in_x_dir_start: Number of lanes.
    :type lanes_in_x_dir_start: Integer

    :param lanes_in_x_dir_end: Number of lanes.
    :type lanes_in_x_dir_end: Integer

    :param Stl: Tab of tabs contening relevant points (3 points per tab) describing a stopline
    :type Stl:[ [x1,y1,x2,y2,x3,y3] ] with x and y float

    :param DefinedSpeed: Represent the speed that the road has per default (defined by the speedprofil in the Road Class)
    :type DefinedSpeed: Float

    '''
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes_start, nbr_of_lanes_end, lanes_in_x_dir_start, lanes_in_x_dir_end, SpeedL, RefS, Stl):

        # General Init

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.stopline = Stl
        self.DefinedSpeed = self.SpeedProfil[5]

        # Edges, Center Line and Lanes

        self.c.append(Straight( x0, y0, h, l))

        self.e1.append(Straight( x0 + lw * (nbr_of_lanes_start/2)* np.cos(h + np.pi / 2),
                                y0 + lw * (nbr_of_lanes_start/2)* np.sin(h + np.pi / 2), h, l))

        self.e2.append(Straight( x0 - lw * (nbr_of_lanes_start/2)* np.cos(h + np.pi / 2),
                                y0 - lw * (nbr_of_lanes_start/2)* np.sin(h + np.pi / 2), h, l/2))

        # We first create the lanes that are not concerned by the changes

        lwi = (nbr_of_lanes_start -1) * lw/2
        for _ in range(min(nbr_of_lanes_start, nbr_of_lanes_end)-1):

            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l))
            lwi -= lw

        # Then we create the one remaining lane (cf wiki only one lane at a time)

        if nbr_of_lanes_start>nbr_of_lanes_end:  # If we add a lane

            self.e2.append(Straight( x0 - lw * (nbr_of_lanes_start/2) * np.cos(h + np.pi / 2)+l*np.cos(h)/2 , y0 - lw * (nbr_of_lanes_start/2)* np.sin(h + np.pi / 2) + l*np.sin(h)/2 , h + np.arctan(2*lw/l), np.sqrt((l/2)**2+lw**2) ) )    # This is the "missing part" of the edge going in the x direction

            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l/2))                           # The begining of the "branching" lane
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) + l*np.cos(h)/2,
                                    y0 + lwi * np.sin(h + np.pi / 2) + l*np.sin(h)/2,
                                    h, l/2))                           # This part combine with the previous lane from the lane going straight
            lwi -= lw
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h+np.arctan(2*lw/l), np.sqrt((l/2)**2+lw**2)))   # And this is the branching part

        if nbr_of_lanes_start<nbr_of_lanes_end:   # Same if we substract a lane

            self.e2.append(Straight( x0 - lw * (nbr_of_lanes_start/2) * np.cos(h + np.pi / 2)+l*np.cos(h)/2 , y0 - lw * (nbr_of_lanes_start/2)* np.sin(h + np.pi / 2) + l*np.sin(h)/2 , h - np.arctan(2*lw/l), np.sqrt((l/2)**2+lw**2) ) )

            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l/2))
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) + l*np.cos(h)/2,
                                    y0 + lwi * np.sin(h + np.pi / 2) + l*np.sin(h)/2,
                                    h, l/2))
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) + l*np.cos(h)/2,
                                    y0 + lwi * np.sin(h + np.pi / 2) + l*np.sin(h)/2,
                                    h-np.arctan(2*lw/l), np.sqrt((l/2)**2+lw**2)))

        if nbr_of_lanes_start==nbr_of_lanes_end: # If the simulation contain straight adapater road
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l/2))
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) + l*np.cos(h)/2,
                                    y0 + lwi * np.sin(h + np.pi / 2) + l*np.sin(h)/2,
                                    h, l/2))

        #This changes the direction of the lanes that drive backwards
        if nbr_of_lanes_start-lanes_in_x_dir_start>0:
            for i in range(nbr_of_lanes_start-lanes_in_x_dir_start):
                l=[]
                for (x, y) in self.l[i]:
                    l.append([x, y])
                l = l[::-1]
                self.l[i] = l

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

    :param DefinedSpeed: Represent the speed that the road has per default (defined by the speedprofil in the Road Class)
    :type DefinedSpeed: Float

    '''
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, entry_road_angle, apron_length, side_road_length, SpeedL, RefS, Stl):

        # General Init

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.stopline = Stl
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
        if nbr_of_lanes-lanes_in_x_dir>0:
            for i in range(nbr_of_lanes-lanes_in_x_dir):
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

    :param DefinedSpeed: Represent the speed that the road has per default (defined by the speedprofil in the Road Class)
    :type DefinedSpeed: Float

    '''
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, exit_road_angle, apron_length, side_road_length, SpeedL, RefS, Stl):

        # General Init

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.stopline = Stl
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
        if nbr_of_lanes-lanes_in_x_dir>0:
            for i in range(nbr_of_lanes-lanes_in_x_dir):
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

    '''
    def __init__(self, id, x0, y0, h, lw, cs_h, cs_len_till_stop, cs_nbr_of_lanes, cs_lanes_in_x_dir, cs_l, SpeedL, RefS, Stl):

        # General Init

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.x=x0
        self.y=y0
        self.stopline = Stl
        self.DefinedSpeed = self.SpeedProfil[8]

        # Lanes Creation

        # Creation of each "Starting Lane"

        counter = 0

        for c in range(4):  # For each Branch of the X Crossing


            nb_of_lanes = cs_nbr_of_lanes[c]
            lanes_in_x_dir = cs_lanes_in_x_dir[c]
            lwi=(cs_nbr_of_lanes[c] -1) * lw/2
            next_first_lane = counter             # Allow us the access to the first lane created that need to be reversed
            for lane in range(nb_of_lanes):

                l1 = Straight(x0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.cos(cs_h[c]+h) + (lwi)*np.cos(cs_h[c]+h+ np.pi / 2), y0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.sin(cs_h[c]+h) + (lwi)*np.sin(cs_h[c]+h+ np.pi / 2), cs_h[c]+h, cs_len_till_stop[c]+1) #+1 or doesnt work

                Actual_Lane = []  # This convert the lane from a path obj to a tab of point
                for (x,y) in l1:
                    Actual_Lane.append([x, y])

                self.l.append(Actual_Lane)

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

            if nb_of_lanes-lanes_in_x_dir>0:
                for j in range(nb_of_lanes-lanes_in_x_dir):
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


        compteur_for_lane_interest = 0  # This compteur will grant us access to the lanes going in the opposite of x direction

        compteur_for_right_most_lane = cs_nbr_of_lanes[0] # this counter allow us to access the lanes that are located in the next right crosssection
        compteur_for_lane_in_front = cs_nbr_of_lanes[0]+cs_nbr_of_lanes[1] # this counter allow us to access the lanes that are located in the crosssection in front of the one being compute
        compteur_for_left_most_lane = cs_nbr_of_lanes[0]+cs_nbr_of_lanes[1] + cs_nbr_of_lanes[2] # this counter allow us to access the lanes that are located in the next left crosssection


        total_nb_of_lanes = 0   # This will be usefull to create a counter that can circle back to the beggining of the lane list (see below)
        for y in range(4):
            total_nb_of_lanes += cs_nbr_of_lanes[y]


        for i in range(4):  # For each Branch of the X Crossing
            nb_of_lanes = cs_nbr_of_lanes[i]
            lanes_in_x_dir = cs_lanes_in_x_dir[i]
            compteur_lanes_restantes = nb_of_lanes - lanes_in_x_dir      # This will give plenty of informations : is the road a one way road ? how many lanes are left to create ?
            compteur_for_right_most_lane += cs_nbr_of_lanes[(i+1)%4]
            compteur_for_lane_in_front += cs_nbr_of_lanes[(i+2)%4]
            compteur_for_left_most_lane += cs_nbr_of_lanes[(i+3)%4]

            if nb_of_lanes - lanes_in_x_dir > 0:  # If the road is not a one way road

                Lanes_of_Interest = self.l[compteur_for_lane_interest:compteur_for_lane_interest+nb_of_lanes - lanes_in_x_dir:1]   # Lanes going in the opposite direction of x that we are looking to connect to other lanes

                # Link a droite et devant pour la lane la plus a droite

                (x1,y1) = Lanes_of_Interest[0][len(Lanes_of_Interest[0])-1]  # We take the coordinate of the last point (the point which is on the stopline basically) of the right most lane

                (x2,y2) = self.l[(compteur_for_right_most_lane-1)%total_nb_of_lanes][0]       # And then the coordinate of the first point of the lane to the right
                (x3,y3) = Intersection_Lines(Lanes_of_Interest[0],self.l[(compteur_for_right_most_lane-1)%total_nb_of_lanes])

                xs = [x1, x3, x3, x2]
                ys = [y1, y3, y3, y2]
                #(x4,y4) = ( ((x3+x2)/2)  ,  ((y3+y2)/2)  )
                #(x5,y5) = ( ((x3+x1)/2)  ,  ((y3+y1)/2)  )

                #xs = [x1, x5, x4, x2]
                #ys = [y1, y5, y4, y2]

                # Lane going to the right
                if cs_lanes_in_x_dir[(i+1)%4] != 0:    # Is the right turn possible ?
                    l1 = Curve(xs, ys, 0)
                    Actual_Lane1 = []
                    for (x,y) in l1:
                        Actual_Lane1.append([x, y])
                    self.l.append(Actual_Lane1)


                # Lane going straight


                (x4,y4) = self.l[(compteur_for_lane_in_front-1)%total_nb_of_lanes][0]

                (x5,y5) = Intersection_Lines(Lanes_of_Interest[0],self.l[(compteur_for_lane_in_front-1)%total_nb_of_lanes])


                xs1 = [x1, x5, x5, x4]
                ys1 = [y1, y5, y5, y4]

                l2 = Curve(xs1, ys1, 0)
                Actual_Lane2 = []
                for (x,y) in l2:
                    Actual_Lane2.append([x, y])
                self.l.append(Actual_Lane2)


                compteur_lanes_restantes -= 1


                # "Middle Lane" and lane going to the left


                if compteur_lanes_restantes !=0 :   # This is here in case of x cross having only 1 lane going in opposite x direction
                    compteur_access_lanes = 1 # Help have acces to each lanes in between the right most lane et the left most lane

                    while (compteur_lanes_restantes !=0) :     # while there is lane in between the two most left/right lanes


                        (x6,y6) =  Lanes_of_Interest[compteur_access_lanes][len(Lanes_of_Interest)-1]   # We Take the coordinate of the end point of the lanes in the middle
                        (x7,y7) = self.l[(compteur_for_lane_in_front-1-compteur_access_lanes)%total_nb_of_lanes][0]  # bangbang

                        (x8,y8) = Intersection_Lines(Lanes_of_Interest[compteur_access_lanes],self.l[(compteur_for_lane_in_front-1-compteur_access_lanes)%total_nb_of_lanes])


                        xs2 = [x6, x8, x8, x7]
                        ys2 = [y6, y8, y8, y7]

                        l3 = Curve(xs2, ys2, 0)
                        Actual_Lane3 = []
                        for (x,y) in l3:
                            Actual_Lane3.append([x, y])
                        self.l.append(Actual_Lane3)
                        compteur_access_lanes += 1
                        compteur_lanes_restantes -= 1

                    # Making the left connection

                    (x9,y9) = Lanes_of_Interest[len(Lanes_of_Interest)-1][len(Lanes_of_Interest[len(Lanes_of_Interest)-1])-1]

                    (x10,y10) = self.l[(compteur_for_left_most_lane-1)%total_nb_of_lanes][0]

                    (x11,y11) = Intersection_Lines(Lanes_of_Interest[len(Lanes_of_Interest)-1],self.l[(compteur_for_left_most_lane-1)%total_nb_of_lanes])

                    #(xm,ym) = ( ((x11+x10)/2)  ,  ((y11+y10)/2)  )
                    #(xn,yn) = ( ((x11+x9)/2)  ,  ((y11+y9)/2)  )

                    #xs3 = [x9, xn, xm, x11]
                    #ys3 = [y9, yn, ym, y11]

                    xs3 = [x9, x11, x11, x10]
                    ys3 = [y9, y11, y11, y10]

                    if cs_lanes_in_x_dir[(i+3)%4] != 0:
                        l4 = Curve(xs3, ys3, 0)
                        Actual_Lane4 = []
                        for (x,y) in l4:
                            Actual_Lane4.append([x, y])
                        self.l.append(Actual_Lane4)

                else :    # If compteur_lanes_restantes = 0 then we just have to make the connection to the left for the uniaue lane going in the opposite of x direction

                    (x12,y12) = Lanes_of_Interest[len(Lanes_of_Interest)-1][len(Lanes_of_Interest[len(Lanes_of_Interest)-1])-1]  #bangavng

                    (x13,y13) = self.l[(compteur_for_left_most_lane-1)%total_nb_of_lanes][0]

                    (x14,y14) = Intersection_Lines(Lanes_of_Interest[len(Lanes_of_Interest)-1],self.l[(compteur_for_left_most_lane-1)%total_nb_of_lanes])


                    #(xm,ym) = ( ((x14+x13)/2)  ,  ((y14+y13)/2)  )
                    #(xn,yn) = ( ((x14+x12)/2)  ,  ((y14+y12)/2)  )

                    #xs4 = [x12, xn, xm, x13]
                    #ys4 = [y12, yn, ym, y13]

                    xs4 = [x12, x14, x14, x13]
                    ys4 = [y12, y14, y14, y13]

                    if cs_lanes_in_x_dir[(i+3)%4] != 0:
                        l5 = Curve(xs4, ys4, 0)
                        Actual_Lane5 = []
                        for (x,y) in l5:
                            Actual_Lane5.append([x, y])

                        self.l.append(Actual_Lane5)

            compteur_for_lane_interest += cs_nbr_of_lanes[i]

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

    '''
    def __init__(self, id, x0, y0, h, lw, cs_h, cs_len_till_stop, cs_nbr_of_lanes, cs_lanes_in_x_dir, cs_l, SpeedL, RefS, Stl):

        # General Init

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        self.x=x0
        self.y=y0
        self.stopline = Stl
        self.DefinedSpeed = self.SpeedProfil[9]

        # Lanes Creation

        # Creation of each "Starting Lane"

        counter = 0

        for c in range(3):  # For each Branch of the Y Crossing


            nb_of_lanes = cs_nbr_of_lanes[c]
            lanes_in_x_dir = cs_lanes_in_x_dir[c]
            lwi=(cs_nbr_of_lanes[c] -1) * lw/2
            next_first_lane = counter             # Allow us the access to the first lane created that need to be reversed

            for lane in range(nb_of_lanes):

                l1 = Straight(x0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.cos(cs_h[c]+h) + (lwi)*np.cos(cs_h[c]+h+ np.pi / 2), y0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.sin(cs_h[c]+h) + (lwi)*np.sin(cs_h[c]+h+ np.pi / 2), cs_h[c]+h, (cs_len_till_stop[c]+1))

                Actual_Lane = []  # This convert the lane from a path obj to a tab of point
                for (x,y) in l1:
                    Actual_Lane.append([x, y])

                self.l.append(Actual_Lane[1:])

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

            if nb_of_lanes-lanes_in_x_dir>0:
                for j in range(nb_of_lanes-lanes_in_x_dir):
                    l=[]
                    for (x, y) in self.l[next_first_lane + j]:
                        l.append([x, y])
                    l = l[::-1]
                    self.l[next_first_lane + j] = l

        # Stoplines Creation




        # Creating every connections between each starting lanes

        # We will now link each crossections of the x crossing
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
        Number_of_lanes_of_interest = []
        for i in range(3):
            nb_of_lanes = cs_nbr_of_lanes[i]
            lanes_in_x_dir = cs_lanes_in_x_dir[i]
            total_nb_of_lanes += nb_of_lanes
            Number_of_lanes_of_interest.append(nb_of_lanes - lanes_in_x_dir)

        compteur_for_lane_interest =0
        local_count = cs_nbr_of_lanes[0]

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

            if Number_of_lanes_of_interest[m] !=0 :  # if there are lanes going in the opposite x direction


                nb_of_lanes = cs_nbr_of_lanes[m]
                lanes_in_x_dir = cs_lanes_in_x_dir[m]
                compteur_lanes_restantes = nb_of_lanes - lanes_in_x_dir


                Lanes_of_Interest = self.l[compteur_for_lane_interest:compteur_for_lane_interest+nb_of_lanes - lanes_in_x_dir:1]   # Lanes going in the opposite direction of x that we are looking to connect to other lanes

                Lane_available_for_connection = []
                for p in range(1,3):
                    for k in range(cs_lanes_in_x_dir[(m+p)%3]):
                        Lane_available_for_connection.append(self.l[(local_count+cs_nbr_of_lanes[(m+p)%3]-cs_lanes_in_x_dir[(m+p)%3]+k)%total_nb_of_lanes]) # We had here every lane available for connection (ie the lane going in the x direction)
                    if p != 2:
                        local_count += cs_nbr_of_lanes[(m+1)%3]



                if Number_of_lanes_of_interest[m] == 1 :  # If we have only one lane of interest (going in the opposite of x dir)

                    for r in range(len(Lane_available_for_connection)): # We connect the Only Lane of interest to EVERY lane avaible for conections

                        (x1,y1) = Lanes_of_Interest[0][len(Lanes_of_Interest[0])-1]

                        (x2,y2) = Lane_available_for_connection[r][0]

                        (x3,y3) = Intersection_Lines(Lanes_of_Interest[0],Lane_available_for_connection[r])

                        (x4,y4) = ( ((x3+x2)/2)  ,  ((y3+y2)/2)  )
                        (x5,y5) = ( ((x3+x1)/2)  ,  ((y3+y1)/2)  )  # Those points allow a smoother curve but seems to crash Autoware for some reasons

                        xs = [x1, x3, x3, x2]
                        ys = [y1, y3, y3, y2]


                        l1 = Curve(xs, ys, 0)
                        Actual_Lane1 = []
                        for (x,y) in l1:
                            Actual_Lane1.append([x, y])
                        self.l.append(Actual_Lane1)


                else :

                    Lane_available_for_connection_right = Lane_available_for_connection[0:cs_lanes_in_x_dir[(m+1)%3]]
                    Lane_available_for_connection_left = Lane_available_for_connection[cs_lanes_in_x_dir[(m+1)%3]:cs_lanes_in_x_dir[(m+1)%3]+cs_lanes_in_x_dir[(m+2)%3]]

                    # We will create a more specific list out of list 2 (that contains every lanes available for connections
                    # Lane available for connection left in whih you'll have every lane locatrd on the crossection to the left
                    # And Lane available for connection right will is the same but for the lanes located on the corssection to the right

                    if len(Lanes_of_Interest)%2 !=0: # If there is an odd numbers of lanes then list 2 will be broken into the 2 list right/left and the raminaing lane will be had to the list that have less lanes
                        Lanes_of_Interest_right = Lanes_of_Interest[0:int((len(Lanes_of_Interest)-1)/2)]
                        Lanes_of_Interest_left = Lanes_of_Interest[int((len(Lanes_of_Interest)-1)/2)+1:]

                        if len(Lane_available_for_connection_right) > len(Lane_available_for_connection_left):
                            Lanes_of_Interest_right.append(Lanes_of_Interest[int((len(Lanes_of_Interest)-1)/2)])
                        elif len(Lane_available_for_connection_left) > len(Lane_available_for_connection_right):
                            Lanes_of_Interest_left.append(Lanes_of_Interest[int((len(Lanes_of_Interest)-1)/2)])
                        else :
                            Lanes_of_Interest_right.append(Lanes_of_Interest[int((len(Lanes_of_Interest)-1)/2)])

                    else :
                        Lanes_of_Interest_right = Lanes_of_Interest[0:int((len(Lanes_of_Interest)-1)/2)+1]
                        Lanes_of_Interest_left = Lanes_of_Interest[int((len(Lanes_of_Interest)-1)/2)+1:]



                    for q in range(len(Lanes_of_Interest_right)):  # Right side of Y Crossing

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
                        # As you know list 1 cannot be longer then list 2

                        if q == len(Lanes_of_Interest_right)-1 : # if the lane of interest currently under study is the last lane
                            for j in range(len(Lane_available_for_connection_right)):  # Then we have to do every remaining connections

                                (x1,y1) = Lanes_of_Interest_right[q][len(Lanes_of_Interest_right[q])-1]

                                (x2,y2) = Lane_available_for_connection_right[j][0]

                                (x3,y3) = Intersection_Lines(Lanes_of_Interest_right[q], Lane_available_for_connection_right[j])

                                (x4,y4) = ( ((x3+x2)/2)  ,  ((y3+y2)/2)  )
                                (x5,y5) = ( ((x3+x1)/2)  ,  ((y3+y1)/2)  )

                                xs = [x1, x3, x3, x2]
                                ys = [y1, y3, y3, y2]

                                l1 = Curve(xs, ys, 0)
                                Actual_Lane1 = []
                                for (x,y) in l1:
                                    Actual_Lane1.append([x, y])
                                self.l.append(Actual_Lane1)

                        else:                       # Else we do just one connection :

                            (x1,y1) = Lanes_of_Interest_right[q][len(Lanes_of_Interest_right[q])-1]

                            (x2,y2) = Lane_available_for_connection_right[len(Lane_available_for_connection_right)-1-q][0]

                            (x3,y3) = Intersection_Lines(Lanes_of_Interest_right[q], Lane_available_for_connection_right[len(Lane_available_for_connection_right)-1-q])

                            (x4,y4) = ( ((x3+x2)/2)  ,  ((y3+y2)/2)  )
                            (x5,y5) = ( ((x3+x1)/2)  ,  ((y3+y1)/2)  )

                            xs = [x1, x3, x3, x2]
                            ys = [y1, y3, y3, y2]


                            l1 = Curve(xs, ys, 0)
                            Actual_Lane1 = []
                            for (x,y) in l1:
                                Actual_Lane1.append([x, y])
                            self.l.append(Actual_Lane1)

                            Lane_available_for_connection_right.pop(len(Lane_available_for_connection_right)-1-q)



                    for q in range(len(Lanes_of_Interest_left)):  # Left side of Y Crossing
                        # Same working but for the left
                        if q == len(Lanes_of_Interest_left)-1 :
                            for j in range(len(Lane_available_for_connection_left)):

                                (x1,y1) = Lanes_of_Interest_left[q][len(Lanes_of_Interest_left[q])-1]

                                (x2,y2) = Lane_available_for_connection_left[j][0]

                                (x3,y3) = Intersection_Lines(Lanes_of_Interest_left[q], Lane_available_for_connection_left[j])

                                (x4,y4) = ( ((x3+x2)/2)  ,  ((y3+y2)/2)  )
                                (x5,y5) = ( ((x3+x1)/2)  ,  ((y3+y1)/2)  )

                                xs = [x1, x3, x3, x2]
                                ys = [y1, y3, y3, y2]


                                l1 = Curve(xs, ys, 0)
                                Actual_Lane1 = []
                                for (x,y) in l1:
                                    Actual_Lane1.append([x, y])
                                self.l.append(Actual_Lane1)

                        else:

                            (x1,y1) = Lanes_of_Interest_left[q][len(Lanes_of_Interest_left[q])-1]

                            (x2,y2) = Lane_available_for_connection_left[len(Lane_available_for_connection_left)-1-q][0]

                            (x3,y3) = Intersection_Lines(Lanes_of_Interest_left[q], Lane_available_for_connection_left[len(Lane_available_for_connection_left)-1-q])

                            (x4,y4) = ( ((x3+x2)/2)  ,  ((y3+y2)/2)  )
                            (x5,y5) = ( ((x3+x1)/2)  ,  ((y3+y1)/2)  )

                            xs = [x1, x3, x3, x2]
                            ys = [y1, y3, y3, y2]

                            l1 = Curve(xs, ys, 0)
                            Actual_Lane1 = []
                            for (x,y) in l1:
                                Actual_Lane1.append([x, y])
                            self.l.append(Actual_Lane1)

                            Lane_available_for_connection_left.pop(len(Lane_available_for_connection_left)-1-q)


            compteur_for_lane_interest += cs_nbr_of_lanes[m]



    def getstart(self):
        return (self.x, self.y)

    def getend(self):
        return (self.x, self.y)
