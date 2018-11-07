import numpy as np

# This class is an aggregation of VMList objects which contain all of the data
# for the entire vector map. The public make_* interfaces convert (x, y)
# coordinate data to vector map data.
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
    # Returns ID of new Node.
    def __new_node(self, x, y):
        self.point.append(x, y)
        self.node.append(len(self.point))
        return len(self.node)

    # Creates a new Line between the last two points. If the connect keyword
    # argument is True, the previous Line will be connected to the new Line.
    # Returns ID of new Line.
    def __new_line(self, connect=True):
        self.line.append(   point_start = len(self.point) - 1,
                            point_end   = len(self.point),
                            line_before = len(self.line))
        if connect and len(self.line) > 1:
            self.line[-2].set_line_after(len(self.line))
        return len(self.line)

    # Returns the distance and direction between two Points (by default the two
    # most recent ones).
    def __compute_vector(self, point_start=-2, point_end=-1):
        magnitude = self.point[point_start].distance_to(self.point[point_end])
        direction = self.point[point_start].direction_to(self.point[point_end])
        return (magnitude, direction)

    # Returns the ID of the Point at (x, y).
    def __find_point(self, x, y):
        for point_id in range(1, len(self.point) + 1):
            px, py = self.point[point_id].get_xy()
            if x == px and y == py:
                return point_id
        return None

    # Returns the ID of the Node at (x, y).
    def __find_node(self, x, y):
        point_id = self.__find_point(x, y)
        if point_id is not None:
            for node_id in range(1, len(self.node) + 1):
                if point_id == self.node[node_id].get_point():
                    return node_id
        return None

    # Returns the ID of the Lane beginning at (x, y).
    def __find_lane_after(self, x, y):
        node_id = self.__find_node(x, y)
        if node_id is not None:
            for lane_id in range(1, len(self.lane) + 1):
                if node_id == self.lane[lane_id].get_node_start():
                    return lane_id
        return None

    # Coordinate data ps must be provided as a numpy array in the form:
    # [[x0, y0], [x1, y1], ...]
    def make_lane(self, ps, junction_start='NORMAL', junction_end='NORMAL',
            turn_start='STRAIGHT', turn_end='STRAIGHT', closed_loop=False):

        # Check if Node exists at first coordinate, else make a new one.
        x0, y0 = ps[0]
        node_first = self.__find_node(x0, y0)
        if node_first is None: node_first = self.__new_node(x0, y0)

        # Connect first two Nodes.
        x1, y1 = ps[1]
        self.__new_node(x1, y1)
        (mag, dir) = self.__compute_vector(
            point_start = self.node[node_first].get_point()
        )
        self.dtlane.append(
            point       = len(self.point) - 1,
            direction   = dir
        )
        self.lane.append(
            dtlane      = len(self.dtlane),
            node_start  = node_first,
            node_end    = len(self.node),
            length      = mag,
            junction    = junction_start,
            turn        = turn_start
        )
        lane_first = len(self.lane)

        # Generate Points, Nodes, DTLanes and Lanes except for first, second and
        # last coordinates.
        for (x, y) in ps[2:-1,]:
            self.__new_node(x, y)
            (mag, dir) = self.__compute_vector()
            dist = mag + self.dtlane[-1].get_length()
            self.dtlane.append(
                point       = len(self.point) - 1,
                length      = dist,
                direction   = dir
            )
            self.lane.append(
                dtlane      = len(self.dtlane),
                node_start  = len(self.node) - 1,
                node_end    = len(self.node),
                length      = mag,
                lane_before = len(self.lane)
            )
            self.lane[-2].set_lane_after(len(self.lane))

        # Save current Point and Node IDs, because new Node may or may not be
        # created in next step.
        node_start = len(self.node)
        point_start = self.node[-1].get_point()

        # Closed loop: Lane ends where it started.
        if closed_loop:
            node_last = node_first
        else:
            # Lane merge/turn: Lane ends at existing Node.
            xn, yn = ps[-1]
            node_last = self.__find_node(xn, yn)
            # Dead end: Lane ends where no other Node currently exists.
            if node_last is None: node_last = self.__new_node(xn, yn)

        (mag, dir) = self.__compute_vector(
            point_start = point_start,
            point_end = self.node[node_last].get_point()
        )
        dist = mag + self.dtlane[-1].get_length()
        self.dtlane.append(
            point       = point_start,
            length      = dist,
            direction   = dir
        )
        self.lane.append(
            dtlane      = len(self.dtlane),
            node_start  = node_start,
            node_end    = node_last,
            length      = mag,
            lane_before = len(self.lane),
            junction    = junction_end,
            turn        = turn_end
        )
        self.lane[-2].set_lane_after(len(self.lane))

        # Closed loop: first Lane follows last Lane.
        if closed_loop:
            self.lane[-1].set_lane_after(lane_first)
            self.lane[lane_first].set_lane_before(len(self.lane))

    def make_line(self, ps, type='CENTER', closed_loop=False):

        # Generate the first pair of Nodes and first Line.
        x0, y0 = ps[0][0], ps[0][1]
        x1, y1 = ps[1][0], ps[1][1]
        self.__new_node(x0, y0)
        self.__new_node(x1, y1)
        line_first = self.__new_line(connect=False)

        # WhiteLine used to mark the center line, RoadEdge used to mark edges
        # of the road. Break if invalid option was given.
        if type == 'CENTER':
            self.whiteline.append(
                line = len(self.line),
                node = len(self.node) - 1
            )
        elif type == 'EDGE':
            self.roadedge.append(
                line = len(self.line),
                node = len(self.node) - 1
            )
        else:
            raise ValueError('Line type ' + type + ' not valid.')
            return

        # Generate Points, Nodes and Lines except for first, second and last
        # coordinates.
        for (x, y) in ps[2:,]:
            self.__new_node(x, y)
            self.__new_line()
            if type == 'CENTER':
                self.whiteline.append(
                    line = len(self.line),
                    node = len(self.node) - 1
                )
            elif type == 'EDGE':
                self.roadedge.append(
                    line = len(self.line),
                    node = len(self.node) - 1
                )

        # Closed loop: first Line follows last Line.
        if closed_loop:
            self.line[-1].set_line_after(line_first)
            self.line[line_first].set_line_before(len(self.lane))

    def export(self):
        self.point.export('./csv/point.csv')
        self.node.export('./csv/node.csv')
        self.line.export('./csv/line.csv')
        self.dtlane.export('./csv/dtlane.csv')
        self.lane.export('./csv/lane.csv')
        self.whiteline.export('./csv/whiteline.csv')
        self.roadedge.export('./csv/roadedge.csv')

# This class is an ordered list of vector map objects with indexing beginning at
# 1, not 0, to comply with the vector map format. A type must be declared on
# instantiation. The append() method will instantiate objects of this type and
# add them to the end of the list.
class VMList:
    def __init__(self, type):
        self.__type = type
        self.__data = []

    # Negative value addressing works as it does with the standard List class.
    def __getitem__(self, key):
        if key >= 0: return self.__data[key - 1]
        else: return self.__data[key]

    def __setitem__(self, key, value):
        if key >= 0: self.__data[key - 1] = value
        else: self.__data[key] = value

    def __iter__(self):
        self.__idx = 0
        return self

    def __next__(self):
        retval = self.__data[self.__idx]
        self.__idx += 1
        return retval

    def __len__(self):
        return len(self.__data)

    # Appends an object of the type declared on instantiation of the VMList
    # object. Arguments passed in here will be used to instantiate that object.
    def append(self, *args, **kwargs):
        self.__data.append(self.__type(*args, **kwargs))

    # Print all data to a file in the vector map CSV format.
    def export(self, path):
        ofile = open(path, 'w')
        ofile.write('\n')
        for i in range(len(self.__data)):
            ofile.write(str(i + 1) + ',' + str(self.__data[i]) + '\n')
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

    def get_xy(self):
        return (self.Bx, self.Ly)

    def __str__(self):
        data = [self.B, self.L, self.H, self.Bx, self.Ly, self.ReF,
                self.MCODE1, self.MCODE2, self.MCODE3]
        return ','.join(map(str, data))

class Node:
    def __init__(self, point):
        self.PID = point            # Corresponding Point ID

    def get_point(self):
        return self.PID

    def __str__(self):
        return str(self.PID)

class Line:
    def __init__(self, point_start=0, point_end=0, line_before=0, line_after=0):
        self.BPID = point_start     # Starting Point ID
        self.FPID = point_end       # Ending Point ID
        self.BLID = line_before     # Preceding Line ID
        self.FLID = line_after      # Following Line ID

    def set_line_before(self, line_before):
        self.BLID = line_before

    def set_line_after(self, line_after):
        self.FLID = line_after

    def __str__(self):
        data = [self.BPID, self.FPID, self.BLID, self.FLID]
        return ','.join(map(str, data))

class Lane:
    def __init__(self, dtlane=0, node_start=0, node_end=0, lane_before=0,
            lane_after=0, length=0.0, junction='NORMAL', turn='STRAIGHT'):
        self.DID = dtlane           # Corresponding DTLane ID
        self.BLID = lane_before     # Preceding Lane ID
        self.FLID = lane_after      # Following Lane ID
        self.BNID = node_start      # Starting Node ID
        self.FNID = node_end        # Ending Node ID
        self.BLID2 = 0
        self.BLID3 = 0
        self.BLID4 = 0
        self.FLID2 = 0
        self.FLID3 = 0
        self.FLID4 = 0
        self.CrossID = 0
        self.Span = length          # Lane lengh (between Nodes)
        self.LCnt = 1
        self.Lno = 1
        self.LimitVel = 40
        self.RefVel = 40
        self.RoadSecID = 0
        self.LaneChgFG = 0

        self.set_junction(junction)
        self.set_turn(turn)

    def get_node_start(self):
        return self.BNID

    def get_node_end(self):
        return self.FNID

    def set_lane_before(self, lane_before):
        self.BLID = lane_before

    def set_lane_after(self, lane_after):
        self.FLID = lane_after

    def set_junction(self, type):
        if type == 'NORMAL':                self.JCT = 0
        elif type == 'LEFT_BRANCHING':      self.JCT = 1
        elif type == 'RIGHT_BRANCHING':     self.JCT = 2
        elif type == 'LEFT_MERGING':        self.JCT = 3
        elif type == 'RIGHT_MERGING':       self.JCT = 4
        elif type == 'COMPOSITION':         self.JCT = 5
        else: raise ValueError('Junction type ' + type + ' not valid.')

    def set_turn(self, type):
        if type == 'STRAIGHT':              self.LaneType = 0
        elif type == 'LEFT_TURN':           self.LaneType = 1
        elif type == 'RIGHT_TURN':          self.LaneType = 2
        else: raise ValueError('Turn type ' + type + ' not valid.')

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
