'''This module contains all of the code defining the structure of different road segments. By taking initial values from the parser the classes calculate a mathematical definition of the road type.

The road classes :class:'BendRoad', :class:'CurvedRoad', :class:'StraightRoad', :class:'RoundaboutRoad', and :class:'XCrossing' all have class variables that represent roads.

'''
from path import *
import numpy as np
from utils import *

class Road:
    '''This is the interface class for all the road types. Every road has certain things in common such as a center, edges and lanes.

    '''
    def __init__(self, id):
        self.id = id
        self.c = []
        self.e1 = []
        self.e2 = []
        self.l = []
        self.previous_road = -1
        self.next_road = -1
        self.isturned = False

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

    def turn_road(self):
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

    '''
    def __init__(self, id, x0, y0, h, rh, clr, lw, nbr_of_lanes, lanes_in_x_dir):
        Road.__init__(self, id)
        self.c.append(Bend( x0, y0, h, rh, clr))
        self.e1.append(Bend( x0 + lw * nbr_of_lanes / 2 * np.cos(h + np.pi / 2),
                        y0 + lw * nbr_of_lanes / 2 * np.sin(h + np.pi / 2),
                        h, rh, clr - np.sign(rh) * lw * nbr_of_lanes / 2))
        self.e2.append(Bend( x0 - lw * nbr_of_lanes / 2 * np.cos(h + np.pi / 2),
                        y0 - lw * nbr_of_lanes / 2 * np.sin(h + np.pi / 2),
                        h, rh, clr + np.sign(rh) * lw * nbr_of_lanes / 2))
        lwi = (nbr_of_lanes - 1) * lw
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

    '''
    def __init__(self, id, x0, y0, h, rh, cp1, cp2, dx, dy, lw, nbr_of_lanes, lanes_in_x_dir):
        Road.__init__(self, id)
        x_ = dx * np.cos(h) - dy * np.sin(h)
        y_ = dx * np.sin(h) + dy * np.cos(h)
        x1 = x0 + cp1 * np.cos(h)
        y1 = y0 + cp1 * np.sin(h)
        x2 = x0 + x_ - cp2 * np.cos(h + rh)
        y2 = y0 + y_ - cp2 * np.sin(h + rh)
        x3 = x0 + x_
        y3 = y0 + y_
        xs = [x0, x1, x2, x3]
        ys = [y0, y1, y2, y3]
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
    :param chs: List of headings for each road cross section.
    :type chs: [Float]
    :param nbr_of_lanes: Number of lanes.
    :type nbr_of_lanes: Integer

    '''
    def __init__(self, id, x0, y0, r, lw, chs, nbr_of_lanes):
        Road.__init__(self, id)
        r = r - lw
        self.c.append(Bend(x0, y0 - r, 0, 2 * np.pi, r))
        self.e2.append(Bend(x0, y0 - (r - lw), 0, 2 * np.pi, (r - lw)))

        self.l.append(Bend( x0, y0 - (r - lw / 2), 0, 2 * np.pi, r - lw / 2))
        self.l.append(Bend( x0, y0 - (r + lw / 2), 0, 2 * np.pi, r + lw / 2))

        offset = np.pi / 8
        h = []
        rh = []
        h.append(chs[0] + offset + np.pi / 2)

        for i in range(1, len(chs)):
            h.append(chs[i] + offset + np.pi / 2)
            rh.append(chs[i] - offset - (chs[i-1] + offset))

        rh.append(chs[0] + np.pi / 2 - offset + 2 * np.pi - h[len(h) - 1])
        for i in range(len(h)):
            x1 = x0 + (r + lw) * np.cos(chs[i] + offset)
            y1 = y0 + (r + lw) * np.sin(chs[i] + offset)
            r1 = r + lw
            self.e1.append(Bend(x1, y1, h[i], rh[i], r1))

        self.exit_lanes = []
        for ch in chs:
            self.exit_lanes.append(ExitLane(id, x0, y0, r, lw, ch, nbr_of_lanes))

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
    def __init__(self, id, x0, y0, r, lw, ch, nbr_of_lanes):
        Road.__init__(self, id)
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
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir):
        Road.__init__(self, id)
        self.c.append(Straight( x0, y0, h, l))
        self.e1.append(Straight( x0 + lw * np.cos(h + np.pi / 2),
                                y0 + lw * np.sin(h + np.pi / 2), h, l))
        self.e2.append(Straight( x0 - lw * np.cos(h + np.pi / 2),
                                y0 - lw * np.sin(h + np.pi / 2), h, l))
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
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes_start, nbr_of_lanes_end, lanes_in_x_dir_start, lanes_in_x_dir_end):
        Road.__init__(self, id)
        self.c.append(Straight( x0, y0, h, l))
        self.e1.append(Straight( x0 + lw * np.cos(h + np.pi / 2),
                                y0 + lw * np.sin(h + np.pi / 2), h, l))
        self.e2.append(Straight( x0 - lw * np.cos(h + np.pi / 2),
                                y0 - lw * np.sin(h + np.pi / 2), h, l))
        lwi = (nbr_of_lanes_start -1) * lw/2
        for _ in range(min(nbr_of_lanes_start, nbr_of_lanes_end)-1):
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l))
            lwi -= lw

        if nbr_of_lanes_start>nbr_of_lanes_end:
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
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, entry_road_angle, apron_length, side_road_length):
        Road.__init__(self, id)
        apron_length2=(apron_length*np.tan(entry_road_angle)+lw/2)/(np.tan(entry_road_angle))
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
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, exit_road_angle, apron_length, side_road_length):
        Road.__init__(self, id)
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
    def __init__(self, id, x0, y0, h, lw, cs_h, cs_len_till_stop, cs_nbr_of_lanes, cs_lanes_in_x_dir, cs_l):
        Road.__init__(self, id)
        p = 0
        self.x=x0
        self.y=y0
        for c in range(4):
            lwi=(cs_nbr_of_lanes[c] -1) * lw/2
            for lane in range(2): #cs_nbr_of_lanes[c]
                self.l.append(Straight( x0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.cos(cs_h[c]+h) + (lwi)*np.cos(cs_h[c]+h+ np.pi / 2),
                                        y0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.sin(cs_h[c]+h) + (lwi)*np.sin(cs_h[c]+h+ np.pi / 2),
                                        cs_h[c]+h, cs_len_till_stop[c]+1))
                lwi -= lw


			#This changes the direction of the lanes that drive backwards
            if cs_nbr_of_lanes[c]-cs_lanes_in_x_dir[c]>0:
                for i in range(cs_nbr_of_lanes[c]-cs_lanes_in_x_dir[c]):
                    l=[]
                    for (x, y) in self.l[len(self.l)-cs_nbr_of_lanes[c]+i]: #This has to be rethought
                        l.append([x, y])
                    l = l[::-1]
                    self.l[len(self.l)-cs_nbr_of_lanes[c]+i] = l


            #l=[]
            #for (x, y) in self.l[4*c]: #This has to be rethought
            #    l.append([x, y])
            #l = l[::-1]
            #self.l[4*c] = l

            self.l.append(Straight( x0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.cos(cs_h[c]+h) + ((cs_nbr_of_lanes[c] -1) * lw/2)*np.cos(cs_h[c]+h+ np.pi / 2),
                                    y0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.sin(cs_h[c]+h) + ((cs_nbr_of_lanes[c] -1) * lw/2)*np.sin(cs_h[c]+h+ np.pi / 2),
                                    cs_h[c]+h + 6/8*np.pi, (cs_l[c]-cs_len_till_stop[c]-1-lw/2)*np.sqrt(2)))

            #self.l.append(Bend( x0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.cos(cs_h[c]) + ((cs_nbr_of_lanes[c] -1) * lw/2)*np.cos(cs_h[c]+ np.pi / 2),
            #                    y0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.sin(cs_h[c]) + ((cs_nbr_of_lanes[c] -1) * lw/2)*np.sin(cs_h[c]+ np.pi / 2),
            #                    cs_h[c] + np.pi, cs_h[c] + np.pi/2, cs_l[c]-cs_len_till_stop[c]-lw-1))

            self.l.append(Straight( x0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.cos(cs_h[c]+h) + ((cs_nbr_of_lanes[c] -1) * lw/2)*np.cos(cs_h[c]+h+ np.pi / 2),
                                    y0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.sin(cs_h[c]+h) + ((cs_nbr_of_lanes[c] -1) * lw/2)*np.sin(cs_h[c]+h+ np.pi / 2),
                                    cs_h[c]+h + 10/8*np.pi, (cs_l[c]-cs_len_till_stop[c]-1+lw/2)*np.sqrt(2)))

            self.l.append(Straight( x0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.cos(cs_h[c]+h) + ((cs_nbr_of_lanes[c] -1) * lw/2)*np.cos(cs_h[c]+h+ np.pi / 2),
                                    y0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.sin(cs_h[c]+h) + ((cs_nbr_of_lanes[c] -1) * lw/2)*np.sin(cs_h[c]+h+ np.pi / 2),
                                    cs_h[c]+h + np.pi, 2*(cs_l[c]-cs_len_till_stop[c]-1)))


    def getstart(self):
        return (self.x, self.y)

    def getend(self):
        return (self.x, self.y)
