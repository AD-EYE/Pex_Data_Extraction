'''This module contains all of the code defining the structure of the output .csv files for the vector map. The :class:`VectorMap` class is the only one which should be accessed externally. Its public methods provide the interfaces to generate a 2D vector map from (x, y) coordinate data and export the data to the appropriate files.

The vector map data classes :class:`Point`, :class:`Node`, :class:`Line`, :class:`Lane`, :class:`DTLane`, :class:`WhiteLine` and :class:`RoadEdge` use the same private member names that are used in the vector map documentation circulated in the Autoware community. Some of these fields are given default values for unknown reasons or have a completely unknown purpose. This is because the vector map format is not officially documented.

.. moduleauthor:: Samuel Lindemer <lindemer@kth.se>

'''
import numpy as np

class VectorMap:
    '''This class is an aggregation of :class:`VMList` objects which contain all of the data for the entire vector map.

    '''
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

    def make_lane(self, ps, junction_start='NORMAL', junction_end='NORMAL',
            turn_start='STRAIGHT', turn_end='STRAIGHT'):
        '''This method takes an ordered array of (x, y) coordinates defining a drivable path and generates the data and references required by the vector map. The vector map format spcifies that the distance between points must be 1 meter or less. The order of the points indicates the direction of traffic flow. These objects are created:  :class:`Point`, :class:`Node`, :class:`DTLane` and :class:`Lane`.

        .. note:: When this method is used multiple times to create connected drivable paths, it is important that both paths contain the exact (x, y) coordinate where the paths intersect. Otherwise, the two paths will not be linked in the vector map.

        :param ps: An array of coordinates [[x0, y0], [x1, y1], ...] defining a drivable path.
        :type ps: array
        :param junction_start: The :class:`Lane` junction type at the start of the path.
        :type junction_start: string
        :param junction_end: The :class:`Lane` junction type at the end of the path.
        :type junction_end: string
        :param turn_start: The :class:`Lane` turn type at the start of the path.
        :type turn_start: string
        :param turn_end: The :class:`Lane` turn type at the end of the path.
        :type turn_end: string

        '''
        # Warn for empty input array and return.
        if not ps.any():
            print('make_lane(): Warning - empty input array.')
            return

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

    def make_line(self, ps, line_type='EDGE'):
        '''This method takes an ordered array of (x, y) coordinates defining a road edge or a center line and generates the data and references required by the vector map. The vector map format spcifies that the distance between points must be 1 meter or less. These objects are created: :class:`Point`, :class:`Node`, :class:`Line`, :class:`WhiteLine` and :class:`RoadEdge`.

        :param ps: An array of coordinates [[x0, y0], [x1, y1], ...] defining a drivable path.
        :type ps: array
        :param line_type: EDGE or CENTER.
        :type line_type: string

        '''

        # Warn for empty input array.
        if not ps.any():
            print('make_line(): Warning - empty input array.')
            return

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
        if data != [[]]: return data
        else: return None

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
        if data != [[]]: return data
        else: return None

    def plot(self):
        '''Displays the vector map as a matplotlib figure. The road edges are shown in blue, the centers in yellow and the lane vectors shown as arrows. Right turns,  branches and merges are shown in red, and the left turns, branches and merges are shown in green. This is a blocking function.

        '''
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
        lines = self.__aggregate_lines()
        if lines is not None:
            for line in lines:
                line = np.array(line)
                plt.plot(line[:,0], line[:,1], 'y-')
        edges = self.__aggregate_edges()
        if edges is not None:
            for edge in edges:
                edge = np.array(edge)
                plt.plot(edge[:,0], edge[:,1], 'b-')
        plt.show()

    def export(self):
        '''Saves the entire vector map to the appropriate .csv files to the directory ./csv.

        .. warning:: This will overwrite the contents of ./csv.

        '''
        self.point.export('./csv/point.csv')
        self.node.export('./csv/node.csv')
        self.line.export('./csv/line.csv')
        self.dtlane.export('./csv/dtlane.csv')
        self.lane.export('./csv/lane.csv')
        self.whiteline.export('./csv/whiteline.csv')
        self.roadedge.export('./csv/roadedge.csv')

class VMList:
    '''This class is an ordered list of vector map objects with indexing beginning at 1, not 0, to comply with the vector map format. Iteration, item getting and setting, and element count work the same as Python's default List.

    :param type: The class of object to be contained in this list.
    :type type: class

    '''
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

    def append(self, *args, **kwargs):
        '''Appends an object of the type declared on instantiation of the VMList object. Arguments and keyword arguments passed in here will be passed directly to the new object's __init__.

        '''
        self.__data.append(self.__type(*args, **kwargs))

    def export(self, path):
        '''Prints all data to a file in the vector map .csv format. Each vector map object class defined in this file has a __str__ override which returns its data in the correct comma-separated order according to the vector map format. Each line of a vector map .csv file starts with a unique ID. These ID values are the indicies in this :class:`VMList` object.

        :param path: The file name to save the data to.
        :type path: string

        '''
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
    '''Vector map data saved to point.csv. Contains ALL of the coordinate data for the entire map.

    :param x: Global X coordinate.
    :type x: float
    :param y: Global Y coordinate.
    :type y: float

    '''
    def __init__(self, x, y):
        self.B = 0.0        # Latitude
        self.L = 0.0        # Longitude
        self.H = 0.0        # Altitude
        self.Ly = x         # Global Y, values are swapped for Autoware, does not work swapping the lines
        self.Bx = y         # Global X
        self.ReF = 7
        self.MCODE1 = 0
        self.MCODE2 = 0
        self.MCODE3 = 0

    def distance_to(self, p):
        '''
        :param p: The target for distance measurment.
        :type p: Point
        :returns: float -- The distance between this :class:`Point` and :class:`Point` p.

        '''
        return np.sqrt((p.Bx - self.Bx)**2 + (p.Ly - self.Ly)**2)

    def direction_to(self, p):
        '''
        :param p: The target for angle measurment.
        :type p: Point
        :returns: float -- The direction in radians (-pi to pi) from this :class:`Point` to :class:`Point` p.
        '''
        return np.arctan2(p.Ly - self.Ly, p.Bx - self.Bx)

    def get_xy(self):
        return (self.Bx, self.Ly)

    def __str__(self):
        data = [self.B, self.L, self.H, self.Bx, self.Ly, self.ReF,
                self.MCODE1, self.MCODE2, self.MCODE3]
        return ','.join(map(str, data))

class Node:
    '''Vector map data saved to node.csv. This class is merely a reference to a single :class:`Point`.

    :param point: The corresponding :class:`Point` ID.
    :type point: int

    '''
    def __init__(self, point):
        self.PID = point            # Corresponding Point ID

    def get_point(self):
        return self.PID

    def __str__(self):
        return str(self.PID)

class Line:
    '''Vector map data saved to line.csv. This class defines the edges of roads and painted lines on roads.

    :param point_start: The ID of the :class:`Point` that starts the line.
    :type point_start: int
    :param point_end: The ID of the :class:`Point` that ends the line.
    :type point_end: int
    :param line_before: The ID of the :class:`Line` connected to the start of this one.
    :type line_before: int
    :param line_afer: The ID of the :class:`Line` connected to the end of this one.
    :type line_afer: int

    '''
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
    '''Vector map data saved to lane.csv. This class partially defines the drivable paths in the world.

    :param dtlane: The corresponding :class:`DTLane` ID.
    :type dtlane: int
    :param node_start: The ID of the :class:`Node` that starts the lane.
    :type node_start: int
    :param node_end: The ID of the :class:`Node` that ends the lane.
    :type node_end: int
    :param lane_before: The ID of the :class:`Lane` connected to the start of this one.
    :type lane_before: int
    :param lane_after: The ID of the :class:`Lane` connected to the end of this one.
    :type lane_after: int
    :param length: The distance between the start and end :class:`Node`.
    :type length: float
    :param junction: NORMAL, LEFT_BRANCHING, LEFT_MERGING, RIGHT_BRANCHING, RIGHT_MERGING, COMPOSITION.
    :type junction: string
    :param turn: STRAIGHT, LEFT_TURN, RIGHT_TURN.
    :type turn: string

    '''
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
    '''Vector map data saved to dtlane.csv. This class partially defines the drivable paths in the world.

    :param point: The corresponding :class:`Point` ID.
    :type point: int
    :param length: The distance from the very start of the entire drivable path to here. NOT the same as length as defined in :class:`Lane`.
    :type length: float
    :param direction: The direction, in radians, from this :class:`DTLane` to the next one.
    :type direction: float

    '''
    def __init__(self, point=0, length=0.0, direction=0.0):
        self.PID = point             # Corresponding Point ID
        self.Dist = length           # TOTAL distance to path start
        self.Dir = direction         # Direction in radians
        self.Apara = 0.0
        self.r = 90000000000.0
        self.slope = 0.0
        self.cant = 0.0
        self.LW = 1.75
        self.RW = 1.75

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
    '''Vector map data saved to whiteline.csv. This class is merely a reference to a single :class:`Node` and a single :class:`Line`, and a color option.

    :param line: The corresponding :class:`Line` ID.
    :type line: int
    :param node: The corresponding :class:`Node` ID.
    :type node: int
    :param color: 'W' for white, 'Y' for yellow.
    :type color: char

    '''
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
    '''Vector map data saved to roadedge.csv. This class is merely a reference to a single :class:`Node` and a single :class:`Line`.

    :param line: The corresponding :class:`Line` ID.
    :type line: int
    :param node: The corresponding :class:`Node` ID.
    :type node: int

    '''
    def __init__(self, line=0, node=0):
        self.LID = line          # Corresponding Line ID
        self.LinkID = node       # Corresponding Node ID

    def get_line(self):
        return self.LID

    def __str__(self):
        data = [self.LID, self.LinkID]
        return ','.join(map(str, data))
