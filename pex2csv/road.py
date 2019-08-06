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

    '''
    def __init__(self, id):
        self.id = id
        self.c = []
        self.e1 = []
        self.e2 = []
        self.l = []
        self.previous_road = -1
        self.next_road = -1
        self.isturned = False    #Useless !!!
        self.SpeedLimit = 1
        self.RefSpeed = 1

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

    def turn_road(self):    #Useless !!!!!
        '''This method marks the road segment as turned in order for the road processor to know on which endpoint it should start.
        '''
        self.isturned = not self.isturned

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

    '''
    def __init__(self, id, x0, y0, h, rh, clr, lw, nbr_of_lanes, lanes_in_x_dir, SpeedL, RefS):  # Take into account the speed as a parameter

        # General Initialization

        Road.__init__(self, id)     #Gave the Id linked to BendRoad
        self.SpeedLimit = SpeedL    #Set the different speeds
        self.RefSpeed = RefS

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

    '''
    def __init__(self, id, x0, y0, h, rh, cp1, cp2, dx, dy, lw, nbr_of_lanes, lanes_in_x_dir, SpeedL, RefS): #Same as BendRoad

        # General Initialization

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS

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

    '''
    def __init__(self, id, x0, y0, r, lw, chs, nbr_of_lanes, SpeedL, RefS):

        # General Initialization

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS

        # Lanes, Center and Edge2 of the Road

        r = r - lw
        self.c.append(Bend(x0, y0 - r, 0, 2 * np.pi, r))
        self.e2.append(Bend(x0, y0 - (r - lw), 0, 2 * np.pi, (r - lw))) #Only edge2 (edge near the center of the RA) can easily be done, the other is harder because of the exit lane of the RA
        self.l.append(Bend( x0, y0 - (r - lw / 2), 0, 2 * np.pi, r - lw / 2))
        self.l.append(Bend( x0, y0 - (r + lw / 2), 0, 2 * np.pi, r + lw / 2))

        # Creation of edge1 and the exit lanes

        # Preparation for Exit lanes and Edge1

        offset = np.pi / 8
        h = []   #Heading list
        rh = []  #Relative Heading
        h.append(chs[0] + offset + np.pi / 2)   #First exit´s heading

        for i in range(1, len(chs)):     #Creation of Heading and the relative Heading for the rest of the exit lane
            h.append(chs[i] + offset + np.pi / 2)
            rh.append(chs[i] - offset - (chs[i-1] + offset))

        rh.append(chs[0] + np.pi / 2 - offset + 2 * np.pi - h[len(h) - 1])  #Last RH

        # Edge 1

        for i in range(len(h)):
            x1 = x0 + (r + lw) * np.cos(chs[i] + offset)
            y1 = y0 + (r + lw) * np.sin(chs[i] + offset)
            r1 = r + lw
            self.e1.append(Bend(x1, y1, h[i], rh[i], r1))

        # Exit Lanes

        self.exit_lanes = []
        for ch in chs:
            self.exit_lanes.append(ExitLane(id, x0, y0, r, lw, ch, nbr_of_lanes, SpeedL, RefS))

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
        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        r += lw
        self.x = x0
        self.y = y0
        self.r = r
        self.ch = ch
        self.lw = lw

        (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, lw)
        self.e1.append(Bend(x, y, h, a, rc))
        (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, -lw)
        self.e2.append(Bend(x, y, h, a, rc))

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

    '''
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, SpeedL, RefS):

        # General Init

        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS

        # Edges, Center Line and Lanes

        self.c.append(Straight( x0, y0, h, l))    # Fix center line

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

    '''
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes_start, nbr_of_lanes_end, lanes_in_x_dir_start, lanes_in_x_dir_end, SpeedL, RefS): #########
        Road.__init__(self, id)
        self.SpeedLimit = SpeedL       #########
        self.RefSpeed = RefS           #########
        self.c.append(Straight( x0, y0, h, l))



        self.e1.append(Straight( x0 + lw * (nbr_of_lanes_start/2)* np.cos(h + np.pi / 2),
                                y0 + lw * (nbr_of_lanes_start/2)* np.sin(h + np.pi / 2), h, l))    ######



        self.e2.append(Straight( x0 - lw * (nbr_of_lanes_start/2)* np.cos(h + np.pi / 2),
                                y0 - lw * (nbr_of_lanes_start/2)* np.sin(h + np.pi / 2), h, l/2))




        lwi = (nbr_of_lanes_start -1) * lw/2
        for _ in range(min(nbr_of_lanes_start, nbr_of_lanes_end)-1):
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l))
            lwi -= lw

        if nbr_of_lanes_start>nbr_of_lanes_end:

            self.e2.append(Straight( x0 - lw * (nbr_of_lanes_start/2) * np.cos(h + np.pi / 2)+l*np.cos(h)/2 , y0 - lw * (nbr_of_lanes_start/2)* np.sin(h + np.pi / 2) + l*np.sin(h)/2 , h + np.arctan(2*lw/l), np.sqrt((l/2)**2+lw**2) ) )             ###########

            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l/2))
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) + l*np.cos(h)/2,
                                    y0 + lwi * np.sin(h + np.pi / 2) + l*np.sin(h)/2,
                                    h, l/2))
            lwi -= lw
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h+np.arctan(2*lw/l), np.sqrt((l/2)**2+lw**2)))

        if nbr_of_lanes_start<nbr_of_lanes_end:

            self.e2.append(Straight( x0 - lw * (nbr_of_lanes_start/2) * np.cos(h + np.pi / 2)+l*np.cos(h)/2 , y0 - lw * (nbr_of_lanes_start/2)* np.sin(h + np.pi / 2) + l*np.sin(h)/2 , h - np.arctan(2*lw/l), np.sqrt((l/2)**2+lw**2) ) )             ###########

            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l/2))
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) + l*np.cos(h)/2,
                                    y0 + lwi * np.sin(h + np.pi / 2) + l*np.sin(h)/2,
                                    h, l/2))
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) + l*np.cos(h)/2,
                                    y0 + lwi * np.sin(h + np.pi / 2) + l*np.sin(h)/2,
                                    h-np.arctan(2*lw/l), np.sqrt((l/2)**2+lw**2)))

        if nbr_of_lanes_start==nbr_of_lanes_end:
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

    '''
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, entry_road_angle, apron_length, side_road_length, SpeedL, RefS): #########
        Road.__init__(self, id)
        self.SpeedLimit = SpeedL       #########
        self.RefSpeed = RefS           #########
        apron_length2=(apron_length*np.tan(entry_road_angle)+lw/2)/(np.tan(entry_road_angle))
        self.c.append(Straight( x0, y0, h, l))



        self.e1.append(Straight( x0 + lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2),
                                y0 + lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2), h, l))   #############



        self.e2.append(Straight( x0 - lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2),
                                y0 - lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2), h, apron_length2))  #############



        self.e2.append(Straight( x0 -lw * (nbr_of_lanes/2) + (apron_length*np.tan(entry_road_angle)-lw * (nbr_of_lanes/2)+lw/2)*np.sin(h),
                                y0 - lw * (nbr_of_lanes/2) - (apron_length*np.tan(entry_road_angle)-lw * (nbr_of_lanes/2)+lw/2)*np.cos(h), entry_road_angle+h, (apron_length*np.tan(entry_road_angle)+lw/2)/np.sin(entry_road_angle)))         ################



        lwi=(nbr_of_lanes -1) * lw/2
        for _ in range(nbr_of_lanes-1):
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l))
            lwi -= lw

        self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                y0 + lwi * np.sin(h + np.pi / 2),
                                h, apron_length2))
        self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) + apron_length2 * np.cos(h),
                                y0 + lwi * np.sin(h + np.pi / 2) + apron_length2 * np.sin(h),
                                h, l-apron_length2))
        self.l.append(Straight( x0 + (apron_length*np.tan(entry_road_angle)-lwi+lw/2)*np.sin(h),
                                y0 - (apron_length*np.tan(entry_road_angle)-lwi+lw/2)*np.cos(h),
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

    '''
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, exit_road_angle, apron_length, side_road_length, SpeedL, RefS): #########
        Road.__init__(self, id)
        self.SpeedLimit = SpeedL       #########
        self.RefSpeed = RefS           #########
        apron_length2=(apron_length*np.tan(exit_road_angle)+lw/2)/(np.tan(exit_road_angle))
        self.c.append(Straight( x0, y0, h, l))
        self.e1.append(Straight( x0 + lw * np.cos(h + np.pi / 2),
                                y0 + lw * np.sin(h + np.pi / 2), h, l))
        self.e2.append(Straight( x0 - lw * np.cos(h + np.pi / 2),
                                y0 - lw * np.sin(h + np.pi / 2), h, l))
        lwi=(nbr_of_lanes -1) * lw/2
        for _ in range(nbr_of_lanes-1):
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l))
            lwi -= lw
        self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                y0 + lwi * np.sin(h + np.pi / 2),
                                h, l-apron_length2))
        self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) + (l-apron_length2) * np.cos(h),
                                y0 + lwi * np.sin(h + np.pi / 2) + (l-apron_length2) * np.sin(h),
                                h, apron_length2))
        self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) + (l-apron_length2) * np.cos(h),
                                y0 + lwi * np.sin(h + np.pi / 2) + (l-apron_length2) * np.sin(h),
                                h-exit_road_angle, (apron_length*np.tan(exit_road_angle)+lw/2)/np.sin(exit_road_angle)))
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

    :param len_till_stop: Distance from endpoint of the arms to the arms' stop line.
    :type len_till_stop: Float

    :param nbr_of_lanes: Number of lanes.
    :type nbr_of_lanes: Integer

    '''
    def __init__(self, id, x0, y0, h, lw, cs_h, cs_len_till_stop, cs_nbr_of_lanes, cs_lanes_in_x_dir, cs_l, SpeedL, RefS):
        Road.__init__(self, id)
        self.SpeedLimit = SpeedL
        self.RefSpeed = RefS
        p = 0
        self.x=x0
        self.y=y0

        # Lanes and edges Creation

        # Creation of each "Starting Lane"

        compteur = 0

        for c in range(4):  # For each Branch of the X Crossing


            nb_of_lanes = cs_nbr_of_lanes[c]
            lanes_in_x_dir = cs_lanes_in_x_dir[c]
            lwi=(cs_nbr_of_lanes[c] -1) * lw/2
            next_first_lane = compteur             # Allow us the access to the first lane created that need to be reversed

            for lane in range(nb_of_lanes):

                l1 = Straight(x0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.cos(cs_h[c]+h) + (lwi)*np.cos(cs_h[c]+h+ np.pi / 2), y0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.sin(cs_h[c]+h) + (lwi)*np.sin(cs_h[c]+h+ np.pi / 2), cs_h[c]+h, cs_len_till_stop[c]+1) #+1 or doesnt work

                Actual_Lane = []
                for (x,y) in l1:
                    Actual_Lane.append([x, y])

                self.l.append(Actual_Lane)

                lwi -= lw
                compteur += 1

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
        print(len(self.l))
        print()
        print(self.l)

        compteur_for_lane_interest = 0  # This compteur will grant us access to the lanes

        compteur_for_right_most_lane = cs_nbr_of_lanes[0] # this compteyr does stuff
        compteur_for_lane_in_front = cs_nbr_of_lanes[0]+cs_nbr_of_lanes[1] # same
        compteur_for_left_most_lane = cs_nbr_of_lanes[0]+cs_nbr_of_lanes[1] + cs_nbr_of_lanes[2] # same


        total_nb_of_lanes = 0
        for y in range(4):
            total_nb_of_lanes += cs_nbr_of_lanes[y]

        for i in range(4):  # For each Branch of the X Crossing
            nb_of_lanes = cs_nbr_of_lanes[i]
            lanes_in_x_dir = cs_lanes_in_x_dir[i]
            compteur_lanes_restantes = nb_of_lanes - lanes_in_x_dir
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

                # Lane going to the right
                if cs_nbr_of_lanes[(i+1)%4]-cs_lanes_in_x_dir[(i+1)%4] != 0:    # Is the right turn possible ?
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

                    (x9,y9) = Lanes_of_Interest[len(Lanes_of_Interest)-1][len(Lanes_of_Interest[len(Lanes_of_Interest)-1])-1]  #bangavng

                    (x10,y10) = self.l[(compteur_for_left_most_lane-1)%total_nb_of_lanes][0]

                    (x11,y11) = Intersection_Lines(Lanes_of_Interest[len(Lanes_of_Interest)-1],self.l[(compteur_for_left_most_lane-1)%total_nb_of_lanes])

                    xs3 = [x9, x11, x11, x10]
                    ys3 = [y9, y11, y11, y10]

                    l4 = Curve(xs3, ys3, 0)
                    Actual_Lane4 = []
                    for (x,y) in l4:
                        Actual_Lane4.append([x, y])
                    self.l.append(Actual_Lane4)

                else :    # If compteur_lanes_restantes = 0 then we just have to make the connection to the left for the uniaue lane going in the opposite of x direction

                    (x12,y12) = Lanes_of_Interest[len(Lanes_of_Interest)-1][len(Lanes_of_Interest[len(Lanes_of_Interest)-1])-1]  #bangavng

                    (x13,y13) = self.l[(compteur_for_left_most_lane-1)%total_nb_of_lanes][0]

                    (x14,y14) = Intersection_Lines(Lanes_of_Interest[len(Lanes_of_Interest)-1],self.l[(compteur_for_left_most_lane-1)%total_nb_of_lanes])

                    xs4 = [x12, x14, x14, x13]
                    ys4 = [y12, y14, y14, y13]

                    l5 = Curve(xs4, ys4, 0)
                    Actual_Lane5 = []
                    for (x,y) in l5:
                        Actual_Lane5.append([x, y])
                    self.l.append(Actual_Lane5)

            compteur_for_lane_interest += cs_nbr_of_lanes[i]
        print(len(self.l))

    def getstart(self):
        return (self.x, self.y)

    def getend(self):
        return (self.x, self.y)
