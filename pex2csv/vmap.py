import numpy as np

# This class is an aggregation of VMList objects which contain all of the data
# for the entire vector map. The public interfaces convert (x, y) coordinate
# data to the vector map format.
class VectorMap:
    def __init__(self):
        self.point      = VMList(Point)
        self.node       = VMList(Node)
        self.line       = VMList(Line)
        self.dtlane     = VMList(DTLane)
        self.lane       = VMList(Lane)
        self.whiteline  = VMList(WhiteLine)
        self.roadedge   = VMList(RoadEdge)

    # Creates a new Point with coordinates (x, y) and its corresponding Node.
    def __new_node(self, x, y):
        self.point.append(x, y)
        self.node.append(len(self.point))

    # Creates a new Line between the last two points. If the connect keyword arg
    # is True, the previous Line will be connected to the new Line.
    def __new_line(self, connect=True):
        self.line.append(   point0 = len(self.point) - 1,
                            point1 = len(self.point),
                            line0  = len(self.line))
        if connect and len(self.line) > 1:
            self.line[-2].line1 = len(self.line)

    # Returns the distance and direction between two Points (by default the two
    # most recent ones).
    def __compute_vector(self, point0=-2, point1=-1):
        magnitude = self.point[point0].distance_to(self.point[point1])
        direction = self.point[point0].direction_to(self.point[point1])
        return (magnitude, direction)

    def make_center(self, xs, ys):
        for (x, y) in zip(xs, ys):
            self.__new_node(x, y)
            if len(self.node) > 1:
                self.__new_line()
                # TODO: make new WhiteLine

    def make_edge(self, xs, ys):
        for (x, y) in zip(xs, ys):
            self.__new_node(x, y)
            if len(self.node) > 1:
                self.__new_line()
                # TODO: make new RoadEdge

    def make_lane(self, xs, ys):
        for (x, y) in zip(xs, ys):
            self.__new_node(x, y)
            if len(self.node) > 1:
                (mag, dir) = self.__compute_vector()
                if len(self.dtlane) > 0:
                    dist = mag + self.dtlane[-1].get_length()
                else: dist = 0.0
                self.dtlane.append( point     = len(self.point) - 1,
                                    length    = dist,
                                    direction = dir)
                self.lane.append(   dtlane    = len(self.dtlane),
                                    node0     = len(self.node) - 1,
                                    node1     = len(self.node),
                                    length    = mag,
                                    lane0     = len(self.lane))
                if len(self.lane) > 1: self.lane[-2].lane1 = len(self.lane)

    def save(self):
        self.point.to_csv('./csv/point.csv')
        self.node.to_csv('./csv/node.csv')
        self.line.to_csv('./csv/line.csv')
        self.dtlane.to_csv('./csv/dtlane.csv')
        self.lane.to_csv('./csv/lane.csv')
        self.whiteline.to_csv('./csv/whiteline.csv')
        self.roadedge.to_csv('./csv/roadedge.csv')

# This class is an ordered list of vector map objects with indexing beginning at
# 1, not 0, to comply with the vector map format. An class must be declared on
# instantiation. The append() method will instantiate objects of this class and
# add them to the end of the list.
class VMList:
    def __init__(self, type):
        self.type = type
        self.data = []

    # Negative value addressing works as it does with the standard List class.
    def __getitem__(self, key):
        if key >= 0: return self.data[key - 1]
        else: return self.data[key]

    def __setitem__(self, key, value):
        if key >= 0: self.data[key - 1] = value
        else: self.data[key] = value

    def __iter__(self):
        self.idx = 0
        return self

    def __next__(self):
        retval = self.data[self.idx]
        self.idx += 1
        return retval

    def __len__(self):
        return len(self.data)

    # Appends an object of the type declared on instantiation of the VMList
    # object. Arguments passed in here will be used to instantiate that object.
    def append(self, *args, **kwargs):
        self.data.append(self.type(*args, **kwargs))

    # Print all data to a file in the vector map CSV format.
    def to_csv(self, path):
        ofile = open(path, 'w')
        for i in range(len(self.data)):
            ofile.write(str(i + 1) + ',' + str(self.data[i]) + '\n')
        ofile.close()

# The following classes hold one line of information for their respective
# vector map files. They each implement a __str__() override which orders the
# fields according to the vector map format. They do not contain an id number
# because they are ultimately stored as an ordered set in VMList.

# NOTE: The attributes of these objects follow the naming conventions used by
# the vector map format, not the standard Python conventions.
class Point:
    def __init__(self, x, y):
        self.B = 0.0        # Latitude
        self.L = 0.0        # Longitude
        self.H = 0.0        # Altitude
        self.Bx = x         # Global X
        self.Ly = y         # Global Y
        self.ReF = 7
        self.MCODE1 = 0
        self.MCODE2 = 0
        self.MCODE3 = 0

    # Compute the distance from this Point to Point p. Needed for Lane.Span and
    # DTLane.Dist.
    def distance_to(self, p):
        return np.sqrt((p.Bx - self.Bx)**2 + (p.Ly - self.Ly)**2)

    # Compute the direction in radians (-pi to pi) from this Point to Point p.
    # Needed for DTLane.Dir.
    def direction_to(self, p):
        return np.arctan2(p.Bx - self.Bx, p.Ly - self.Ly)

    def __str__(self):
        data = [self.B, self.L, self.H, self.Bx, self.Ly, self.ReF,
                self.MCODE1, self.MCODE2, self.MCODE3]
        return ','.join(map(str, data))

class Node:
    def __init__(self, point):
        self.PID = point        # Corresponding Point ID

    def __str__(self):
        return str(self.PID)

class Line:
    def __init__(self, point0=0, point1=0, line0=0, line1=0):
        self.BPID = point0  # Starting Point ID
        self.FPID = point1  # Ending Point ID
        self.BLID = line0   # Preceding Line ID
        self.FLID = line1   # Following Line ID

    def __str__(self):
        data = [self.BPID, self.FPID, self.BLID, self.FLID]
        return ','.join(map(str, data))

class Lane:
    def __init__(self, dtlane=0, node0=0, node1=0, lane0=0, lane1=0,
            junction=0, length=0.0, type=0):
        self.DID = dtlane       # Corresponding DTLane ID
        self.BLID = lane0       # Preceding Lane ID
        self.FLID = lane1       # Following Lane ID
        self.BNID = node0       # Starting Node ID
        self.FNID = node1       # Ending Node ID
        self.JCT = junction     # Road junction type (0-5)
        self.BLID2 = 0
        self.BLID3 = 0
        self.BLID4 = 0
        self.FLID2 = 0
        self.FLID3 = 0
        self.FLID4 = 0
        self.CrossID = 0
        self.Span = length      # Lane lengh (between Nodes)
        self.LCnt = 1
        self.Lno = 1
        self.LaneType = type    # Lane type (0-2)
        self.LimitVel = 40
        self.RefVel = 40
        self.RoadSecID = 0
        self.LaneChgFG = 0

    def __str__(self):
        data = [self.DID, self.BLID, self.FLID, self.BNID, self.FNID,
                self.JCT, self.BLID2, self.BLID3, self.BLID4, self.FLID2,
                self.FLID3, self.FLID4, self.CrossID, self.Span, self.LCnt,
                self.Lno, self.LaneType, self.LimitVel, self.RefVel,
                self.RoadSecID, self.LaneChgFG]
        return ','.join(map(str, data))

class DTLane:
    def __init__(self, point=0, length=0.0, direction=0.0):
        self.PID = point             # Corresponding Point ID
        self.Dist = length           # TOTAL distance to path start
        self.Dir = direction         # Direction in radians
        self.Apara = 0.0
        self.r = 90000000000.0
        self.slope = 0.0
        self.cant = 0.0
        self.LW = 2.0
        self.RW = 2.0

    # DTLane records the cumulative distance to the start of the lane, so each
    # new DTLane must check the previous.
    def get_length(self):
        return self.Dist

    def __str__(self):
        data = [self.Dist, self.PID, self.Dir, self.Apara, self.r, self.slope,
                self.cant, self.LW, self.RW]
        return ','.join(map(str, data))

# NOTE: It is not clear whether the Node associated with the following two
# classes is the start or the end of the WhiteLine/RoadEdge segment.
class WhiteLine:
    def __init__(self, line=0, node=0, color='W'):
        self.LID = line          # Corresponding Line ID
        self.Width = 0.2
        self.Color = color       # 'W' for white, 'Y' for yellow
        self.type = 0
        self.LinkID = node       # Corresponding Node ID

    def __str__(self):
        data = [self.LID, self.Width, self.Color, self.type, self.LinkID]
        return ','.join(map(str, data))

class RoadEdge:
    def __init__(self, line=0, node=0):
        self.LID = line          # Corresponding Line ID
        self.LinkID = node       # Corresponding Node ID

    def __str__(self):
        data = [self.LID, self.LinkID]
        return ','.join(map(str, data))
