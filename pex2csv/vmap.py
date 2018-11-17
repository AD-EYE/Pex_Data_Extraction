'''
Samuel Tanner Lindemer
KTH Royal Institute of Technology
Stockholm, Sweden 2018

The VectorMap class in this file is used as an interface to translate Cartesian
coordinate data into the vector map format used in autonomous driving
applications like Autoware.

make_lane:  Translates coordinate data into drivable lanes (i.e., vectors).
make_line:  Translates coordinate data into center lines and road edges.
plot:       Generates a visual display of the vector map using matplotlib.
export:     Saves the vector map data to the appropriate .csv files.
'''

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

        # Mapping of (x, y) coordinate values to Node IDs.
        self.__xy_node_map = {}

    # Creates a new Point with coordinates (x, y) and its corresponding Node.
    # Returns the Node ID of the new Node.
    def __new_node(self, x, y):
        # Create a new Point and corresponding Node.
        self.point.append(x, y)
        self.node.append(len(self.point))
        node_id = len(self.node)
        # Add entry to Node map.
        self.__xy_node_map[(x, y)] = node_id
        return node_id

    # Checks if a Node already exists at (x, y). Returns Node ID if one exists,
    # otherwise returns None.
    def __find_node(self, x, y):
        try: return self.__xy_node_map[(x, y)]
        except KeyError: return None

    # Returns the Node ID of the Node at (x, y) if one exists, otherwise makes
    # a new Node and returns its Node ID.
    def __get_node(self, x, y):
        node_id = self.__find_node(x, y)
        if node_id is None: node_id = self.__new_node(x, y)
        return node_id

    # Creates a new Lane between the last two points. Returns ID of Lane and
    # DTLane as a Tuple.
    def __new_lane(self, node_start=0, node_end=0, lane_before=None,
            dtlane_before=None):
        mag, dir = self.__compute_vector(
            node_start  = node_start,
            node_end    = node_end
        )
        if dtlane_before is not None:
            distance = self.dtlane[dtlane_before].get_length() + mag
        else: distance = mag
        self.dtlane.append(
            point       = self.node[node_end].get_point(),
            length      = distance,
            direction   = dir
        )
        self.lane.append(
            dtlane      = len(self.dtlane),
            node_start  = node_start,
            node_end    = node_end,
            length      = mag
        )
        lane_id = len(self.lane)
        dtlane_id = len(self.dtlane)
        if lane_before is not None:
            self.lane[lane_id].set_lane_before(lane_before)
            self.lane[lane_before].set_lane_after(lane_id)
        return (lane_id, dtlane_id)

    # Creates a new Line between the last two points. Returns ID of new Line.
    def __new_line(self, node_start=0, node_end=0, line_before=None,
            line_type='EDGE'):
        self.line.append(   point_start = self.node[node_start].get_point(),
                            point_end   = self.node[node_end].get_point())
        if line_type == 'CENTER':
            self.whiteline.append(line = len(self.line), node = node_start)
        elif line_type == 'EDGE':
            self.roadedge.append(line = len(self.line), node = node_start)
        else: raise ValueError('__new_line: line_type=' + str(line_type))
        if line_before is not None:
            self.line[-1].set_line_before(line_before)
            self.line[line_before].set_line_after(len(self.line))
        line_id = len(self.line)
        return line_id

    # Returns the distance and direction between two Nodes.
    def __compute_vector(self, node_start=0, node_end=0):
        point_start = self.node[node_start].get_point()
        point_end = self.node[node_end].get_point()
        magnitude = self.point[point_start].distance_to(self.point[point_end])
        direction = self.point[point_start].direction_to(self.point[point_end])
        return (magnitude, direction)

    # Coordinate data ps must be provided as a numpy array in the form:
    # [[x0, y0], [x1, y1], ...]
    def make_lane(self, ps, junction_start='NORMAL', junction_end='NORMAL',
            turn_start='STRAIGHT', turn_end='STRAIGHT'):

        # Create or find the first Node.
        node_first = self.__get_node(ps[0][0], ps[0][1])
        lane_first = None

        # Generate vector map objects.
        node_previous = node_first
        lane_previous = None
        dtlane_previous = None
        for (x, y) in ps[1:,]:
            node_current = self.__get_node(x, y)
            lane_previous, dtlane_previous = self.__new_lane(
                node_start = node_previous,
                node_end = node_current,
                lane_before = lane_previous,
                dtlane_before = dtlane_previous
            )

            # If this is the first Lane, remember the ID. Else, link the
            # previous Lane to the new one.
            if lane_first is None: lane_first = lane_previous
            node_previous = node_current

        # Mark junctions and turns provided by caller.
        self.lane[lane_first].set_junction(junction_start)
        self.lane[lane_first].set_turn(turn_start)
        self.lane[lane_previous].set_junction(junction_end)
        self.lane[lane_previous].set_turn(turn_end)

    # Coordinate data ps must be provided as a numpy array in the form:
    # [[x0, y0], [x1, y1], ...]
    # Valid opitions for line_type: 'EDGE' or 'CENTER'.
    def make_line(self, ps, line_type='EDGE'):
        node_previous = self.__get_node(ps[0][0], ps[0][1])
        line_previous = None

        # Generate remaining Points, Nodes and Lines.
        for (x, y) in ps[1:,]:
            node_current = self.__get_node(x, y)
            line_current = self.__new_line(
                node_start = node_previous,
                node_end = node_current,
                line_before = line_previous,
                line_type = line_type
            )
            node_previous = node_current
            line_previous = line_current

    # Returns the drivable lane data in the format:
    # [ [x0, y0, mag0, dir0, edge_color0, face_color0],
    #   [x1, y1, mag1, dir1, edge_color1, face_color1], ...]
    # Colors are used in the plot() method to generate graphical arrows.
    def __aggregate_lanes(self):
        data = []
        for l in self.lane:
            x, y = self.point[self.node[l.get_node_start()].get_point()].get_xy()
            magnitude = l.get_length()
            direction = self.dtlane[l.get_dtlane()].get_direction()
            if l.get_turn() == 'RIGHT_TURN':
                edge_color = 'r'
                face_color = 'r'
            elif l.get_turn() == 'LEFT_TURN':
                edge_color = 'g'
                face_color = 'g'
            elif    l.get_junction() == 'RIGHT_BRANCHING' or \
                    l.get_junction() == 'RIGHT_MERGING':
                edge_color = 'r'
                face_color = 'w'
            elif    l.get_junction() == 'LEFT_BRANCHING' or \
                    l.get_junction() == 'LEFT_MERGING':
                edge_color = 'g'
                face_color = 'w'
            else:
                edge_color = 'k'
                face_color = 'w'
            data.append([x, y, magnitude, direction, edge_color, face_color])
        return data

    # Returns the center line data in the format:
    # [ [[x0, y0], [x1, y1], ...], [[x0, y0], [x1, y1], ...] ]
    def __aggregate_lines(self):
        data = [[]]
        for wl in self.whiteline:
            p0 = self.line[wl.get_line()].get_point_start()
            p1 = self.line[wl.get_line()].get_point_end()
            x0, y0 = self.point[p0].get_xy()
            x1, y1 = self.point[p1].get_xy()
            if len(data[-1]) == 0: data[-1] = [[x0, y0], [x1, y1]]
            elif data[-1][-1] == [x0, y0]: data[-1].append([x1, y1])
            else: data.append([[x0, y0], [x1, y1]])
        return np.array(data)

    # Returns the road edge data in the format:
    # [ [[x0, y0], [x1, y1], ...], [[x0, y0], [x1, y1], ...] ]
    def __aggregate_edges(self):
        data = [[]]
        for re in self.roadedge:
            p0 = self.line[re.get_line()].get_point_start()
            p1 = self.line[re.get_line()].get_point_end()
            x0, y0 = self.point[p0].get_xy()
            x1, y1 = self.point[p1].get_xy()
            if len(data[-1]) == 0: data[-1] = [[x0, y0], [x1, y1]]
            elif data[-1][-1] == [x0, y0]: data[-1].append([x1, y1])
            else: data.append([[x0, y0], [x1, y1]])
        return np.array(data)

    # Displays the vector map as a matplotlib figure. (Blocking function.)
    def plot(self):
        from matplotlib import pyplot as plt
        plt.figure('Vector Map')
        plt.axis('equal')
        plt.grid(True)
        for x, y, m, d, ec, fc in self.__aggregate_lanes():
            plt.arrow(
                x, y, m * np.cos(d), m * np.sin(d),
                head_width=0.25, head_length=0.2, fc=fc, ec=ec,
                width=0.1, length_includes_head=True
            )
        for line in self.__aggregate_lines():
            plt.plot(line[:,0], line[:,1], 'y-')
        for edge in self.__aggregate_edges():
            plt.plot(edge[:,0], edge[:,1], 'b-')
        plt.show()

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
        if self.__idx == len(self.__data): raise StopIteration
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
        return np.arctan2(p.Ly - self.Ly, p.Bx - self.Bx)

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

    def get_point_start(self):
        return self.BPID

    def get_point_end(self):
        return self.FPID

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

    def get_dtlane(self):
        return self.DID

    def get_length(self):
        return self.Span

    def get_node_start(self):
        return self.BNID

    def get_node_end(self):
        return self.FNID

    def set_lane_before(self, lane_before):
        self.BLID = lane_before

    def set_lane_after(self, lane_after):
        self.FLID = lane_after

    def get_junction(self):
        if self.JCT == 0: return 'NORMAL'
        elif self.JCT == 1: return 'LEFT_BRANCHING'
        elif self.JCT == 2: return 'RIGHT_BRANCHING'
        elif self.JCT == 3: return 'LEFT_MERGING'
        elif self.JCT == 4: return 'RIGHT_MERGING'
        elif self.JCT == 5: return 'COMPOSITION'
        else: raise ValueError('Junction ' + str(self.JCT) + ' not valid.')

    def get_turn(self):
        if self.LaneType == 0: return 'STRAIGHT'
        elif self.LaneType == 1: return 'LEFT_TURN'
        elif self.LaneType == 2: return 'RIGHT_TURN'
        else: raise ValueError('Turn ' + self.LaneType + ' not valid.')

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

    def get_direction(self):
        return self.Dir

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

    def get_line(self):
        return self.LID

    def __str__(self):
        data = [self.LID, self.Width, self.Color, self.type, self.LinkID]
        return ','.join(map(str, data))

class RoadEdge:
    def __init__(self, line=0, node=0):
        self.LID = line          # Corresponding Line ID
        self.LinkID = node       # Corresponding Node ID

    def get_line(self):
        return self.LID

    def __str__(self):
        data = [self.LID, self.LinkID]
        return ','.join(map(str, data))
