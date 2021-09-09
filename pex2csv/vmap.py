'''This module contains all of the code defining the structure of the output .csv files for the vector map. The :class:`VectorMap` class is the only one which should be accessed externally. Its public methods provide the interfaces to generate a 2D vector map from (x, y) coordinate data and export the data to the appropriate files.

The vector map data classes :class:`Point`, :class:`Node`, :class:`Line`, :class:`Lane`, :class:`DTLane`, :class:`WhiteLine` and :class:`RoadEdge` use the same private member names that are used in the vector map documentation circulated in the Autoware community. Some of these fields are given default values for unknown reasons or have a completely unknown purpose. This is because the vector map format is not officially documented.

.. moduleauthor:: Samuel Lindemer <lindemer@kth.se>

'''
import numpy as np
from utils import dist
import os
import sys
from progress.bar import IncrementalBar

class VectorMap:
    '''This class is an aggregation of :class:`VMList` objects which contain all of the data for the entire vector map.

    '''
    def __init__(self):
        self.points      = VMList(Point)
        self.nodes       = VMList(Node)
        self.lines       = VMList(Line)
        self.dtlanes     = VMList(DTLane)
        self.lanes       = VMList(Lane)
        self.whitelines  = VMList(WhiteLine)
        self.roadedges   = VMList(RoadEdge)
        self.vectors     = VMList(Vector)
        self.signaldatas = VMList(SignalData)
        self.stoplines   = VMList(Stopline)
        self.areas       = VMList(Area)
        self.crosswalks  = VMList(Crosswalk)

        # Mapping of (x, y) coordinate values to Node IDs.
        self.__xy_node_map = {}

    # Creates a new Point with coordinates (x, y) and its corresponding Node.
    # Returns the Node ID of the new Node.
    def __new_node(self, x, y):
        # Create a new Point and corresponding Node.
        point_id = self.points.create(x, y, 0.0)
        node_id = self.nodes.create(point_id)
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
    def __new_lane(self, SpeedLimit, RefSpeed, node_start=0, node_end=0, lane_before=None,
            dtlane_before=None):
        mag, dir = self.__compute_vector(
            node_start  = node_start,
            node_end    = node_end
        )
        if dtlane_before is not None:
            distance = self.dtlanes[dtlane_before].get_length() + mag
        else: distance = mag
        dtlane_id = self.dtlanes.create(
            point       = self.nodes[node_end].get_point(),
            length      = distance,
            direction   = dir
        )
        lane_id = self.lanes.create(
            SpeedLimit,
            RefSpeed,
            dtlane      = len(self.dtlanes),
            node_start  = node_start,
            node_end    = node_end,
            length      = mag
        )
        if lane_before is not None:
            self.lanes[lane_id].set_lane_before(lane_before)
            self.lanes[lane_before].set_lane_after(lane_id)

        return (lane_id, dtlane_id)

    # Creates a new Line between the last two points. Returns ID of new Line.
    def __new_line(self, node_start=0, node_end=0, line_before=None,
            line_type='EDGE'):
        line_id = self.lines.create(
            point_start = self.nodes[node_start].get_point(),
            point_end   = self.nodes[node_end].get_point()
        )
        if line_type == 'CENTER':
            self.whitelines.create(line = len(self.lines), node = node_start)
        elif line_type == 'EDGE':
            self.roadedges.create(line = len(self.lines), node = node_start)
        else: raise ValueError('__new_line: line_type=' + str(line_type))
        if line_before is not None:
            self.lines[-1].set_line_before(line_before)
            self.lines[line_before].set_line_after(len(self.lines))
        return line_id

    # Returns the distance and direction between two Nodes.
    def __compute_vector(self, node_start=0, node_end=0):
        point_start = self.nodes[node_start].get_point()
        point_end = self.nodes[node_end].get_point()
        magnitude = self.points[point_start].distance_to(self.points[point_end])
        direction = self.points[point_start].direction_to(self.points[point_end])
        return (magnitude, direction)

    def make_lane(self, cross, SpeedLimit, RefSpeed, ps, junction_start='NORMAL', junction_end='NORMAL',
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
            lane_previous, dtlane_previous = self.__new_lane(SpeedLimit, RefSpeed,
                node_start = node_previous,
                node_end = node_current,
                lane_before = lane_previous,
                dtlane_before = dtlane_previous
            )
            for tab in cross :          #here we try to find if a crosswalk crosses the lane to set CrossID of the lane (0 if there is no crosswalk)
                for i in range (3):
                    if dist ((x,y),(tab[i+1],tab[i+2]))<2 :
                        setattr(self.lanes[0], 'CrossID', tab[0])

            # If this is the first Lane, remember the ID. Else, link the
            # previous Lane to the new one.
            if lane_first is None: lane_first = lane_previous
            node_previous = node_current


        # Mark junctions and turns provided by caller.
        self.lanes[lane_first].set_junction(junction_start)
        self.lanes[lane_first].set_turn(turn_start)
        self.lanes[lane_previous].set_junction(junction_end)
        self.lanes[lane_previous].set_turn(turn_end)



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

    def rebuild_lane_conections(self):
        bar = IncrementalBar('       progress', max=2*len(self.lanes))
        for i in range(len(self.lanes)):                                 # Check every lane
            k = 0
            bar.next()
            for j in range(len(self.lanes)):                         # Check them against all the other lanes
                if self.lanes[i].FNID == self.lanes[j].BNID:
                    k = k+1
                    if k == 1: self.lanes[i].FLID = self.lanes[j].DID
                    if k == 2: self.lanes[i].FLID2 = self.lanes[j].DID
                    if k == 3: self.lanes[i].FLID3 = self.lanes[j].DID
                    if k == 4: self.lanes[i].FLID4 = self.lanes[j].DID

        for i in range(len(self.lanes)):
            k = 0
            bar.next()
            for j in range(len(self.lanes)):
                if self.lanes[i].BNID == self.lanes[j].FNID:
                    k = k+1
                    if k == 1: self.lanes[i].BLID = self.lanes[j].DID
                    if k == 2: self.lanes[i].BLID2 = self.lanes[j].DID
                    if k == 3: self.lanes[i].BLID3 = self.lanes[j].DID
                    if k == 4: self.lanes[i].BLID4 = self.lanes[j].DID
        bar.finish()

    def remove_one_point_lanes(self): # to avoid having lanes having p0 - p0 as a result of merge_redundant_points
        lanes_to_delete = []
        for i in range(len(self.lanes)):
            if self.lanes[i].BNID == self.lanes[i].FNID:
                lanes_to_delete.append(i)
        lanes_to_delete.reverse() # need to do it backward so that we remove the actual index (removing one element changes the index of all the ones after)
        print("       the following lanes will be removed" + str(lanes_to_delete))
        for index in lanes_to_delete:
            self.lanes.remove_element(index)
            self.dtlanes.remove_element(index)
            self.decrement_lane_id(index)

    def decrement_lane_id(self, decrement_threshold_index): # to make sure that the lane indexes has no holes after one point lane removal
        for lane in self.lanes:
            if lane.DID >= decrement_threshold_index:
                lane.DID -= 1
            if lane.BLID >= decrement_threshold_index:
                lane.BLID -= 1
            if lane.BLID2 >= decrement_threshold_index:
                lane.BLID2 -= 1
            if lane.BLID3 >= decrement_threshold_index:
                lane.BLID3 -= 1
            if lane.BLID4 >= decrement_threshold_index:
                lane.BLID4 -= 1
            if lane.FLID >= decrement_threshold_index:
                lane.FLID -= 1
            if lane.FLID2 >= decrement_threshold_index:
                lane.FLID2 -= 1
            if lane.FLID3 >= decrement_threshold_index:
                lane.FLID3 -= 1
            if lane.FLID4 >= decrement_threshold_index:
                lane.FLID4 -= 1

    def merge_redundant_points(self):
        c = 0
        for i in range(len(self.lanes)):
            if self.lanes[i].FLID == 0:
                PID_i = self.lanes[i].FNID         #This works because NID = PID
                for j in range(len(self.points)):
                    PID_j = j
                    if PID_i != PID_j:
                        if self.square_distance(PID_i, PID_j) < 0.0001:
                            self.merge_two_points(PID_i, PID_j)
                            c = c+1
                            # print('Case ' + str(c) + ': x = ' + str(self.points[PID_i].Ly) + ', y = ' + str(self.points[PID_i].Bx))
                            # print('       ' + ': x = ' + str(self.points[PID_j].Ly) + ', y = ' + str(self.points[PID_j].Bx))
            if self.lanes[i].BNID == self.lanes[i].FNID:
                print("       lane " + str(self.lanes[i].DID) + " now has twice the same point (should be fixed by the one lane point removal)")

    def square_distance(self, PID_1, PID_2):
        return ((self.points[PID_1].Bx - self.points[PID_2].Bx)**2 + (self.points[PID_1].Ly - self.points[PID_2].Ly)**2 + (self.points[PID_1].H - self.points[PID_2].H)**2)

    def merge_two_points(self, PID_1, PID_2):
        for i in range(len(self.dtlanes)):
            if self.dtlanes[i].PID == PID_2:
                self.dtlanes[i].PID = PID_1
        for i in range(len(self.lanes)):
            # if (self.lanes[i].BNID == PID_1 and self.lanes[i].FNID == PID_2) or (self.lanes[i].BNID == PID_2 and self.lanes[i].FNID == PID_1):
            #     self.lanes.remove_element(i) # delete the lane
            #     self.dtlanes.remove_element(i)
            # else:
            #     if self.lanes[i].BNID == PID_2:
            #         self.lanes[i].BNID = PID_1
            #     if self.lanes[i].FNID == PID_2:
            #         self.lanes[i].FNID = PID_1

            if self.lanes[i].BNID == PID_2:
                self.lanes[i].BNID = PID_1
            if self.lanes[i].FNID == PID_2:
                self.lanes[i].FNID = PID_1

    def make_Stoplines(self, list_of_stoplines):
        '''This method take an array/list of stoplines representing every stoplines in the simulation.
        Each element of the stopline array constitutes of three points which is used to make the stopline  and a number of lanes of the road, number of exit lanes and lane width
        where the stopline is.We use the three points and also the number of exit lanes to form the vector mapper components.
        
        '''
        # First we  find the ID of the closest lane to the stopline, using the third point which is the middle point of the stopline.    
        # For each stopline in the list, we first take the middle point and find out the distance between the middle point and each point in self.points which constitutes the lane
        
        for stopline in list_of_stoplines:
            
            for i in range(len(stopline)):
                
                middle_point = (stopline[i][4],stopline[i][5])
                min_dist = 1000     # We are setting a random value as the minimum distance first.
                for j in range(len(self.points)):
                    
                    x = self.points[j].Ly
                    y = self.points[j].Bx
                    point_of_interest = (x,y)
                    distance = dist(point_of_interest,middle_point) # Calculating the distance
                    if min_dist > distance:
                        min_dist = distance  
                        closest_point = point_of_interest
                        closest_node = j

                for k in range(len(self.lanes)):
                    
                    if closest_node == self.lanes[k].FNID:
                        lane_id = self.lanes[k].BLID

                        PointID1 = self.points.create(stopline[i][0], stopline[i][1], 0)
                        PointID2 = self.points.create(stopline[i][2], stopline[i][3], 0)
                        LineID = self.lines.create(PointID1,PointID2)
                        line_length = dist( (stopline[i][0],stopline[i][1]) , (stopline[i][2],stopline[i][3]) )    # Distance between the first and the last point of the stopline
                        signID = 1
                        
                        # The following loop  checks whether the line length is gretaer then the no of exit lanes and updates the value of linelength and signID
                        # stopline[i][7] represets the number of exit lanes in the list.If it is zero,ie if the cross section contains only entry lane,then the while loop loops infintly.So we provide a conditional check.
                        while round(line_length,2) > stopline[i][7] and stopline[i][7] > 0:
                            signID += 1
                            line_length -= stopline[i][7]
                        StoplineID = self.stoplines.create(LineID, 0, signID , lane_id-1) # As you can see here we pass on the nb of relevant lanes as the signID

    def make_Area(self, crosswalk):
        '''
        This method takes an array of tab representing every 3 points for a crosswalk.
        It returns an array of the crosswalks ID and the coordinates of the points describing them --> will be usefull to set CrossID in Lane
        cross = [CrossID, Point1 x, Point1 y, Point2 x, Point2 y, Point3 x, Point3 y]
        '''
        empty = [] #list filled with indexes k where crosswalk[k]==[]
        k=0
        for tab in crosswalk :
            if tab == []:
                empty.append(k)
            k=k+1

        empty.reverse()

        for j in empty :  # removing empty lists from the list of lists crosswalk
            del crosswalk[j]

        cross = []
        k = 0
        for tab in crosswalk :
            cross.append([k,tab[0][0],tab[0][1],tab[0][2],tab[0][3],tab[0][4],tab[0][5]])
            k=k+1

        return cross

    def make_crosswalk(self,cross):
        '''
        this method creates the area and the crosswalks (and the corresponding points and lines)
        '''
        for tab in cross :
            PID1=self.points.create(tab[1],tab[2],0)
            PID2=self.points.create(tab[3],tab[4],0)
            PID3=self.points.create(tab[5],tab[6],0)

            LineID1=self.lines.create(PID1,PID2)
            LineID2=self.lines.create(PID2,PID3)
            LineID3=self.lines.create(PID3,PID1)

            AreaID=self.areas.create(LineID1,LineID3)
            CrosswalkID=self.crosswalks.create(AreaID)




    def make_TrafficLight(self, TrafficLightList):


            # Going throught the list of traffic Lights in the simulationS

            n = len(TrafficLightList)
            error = False

            if n > len(self.stoplines):
                print("error : traffic lights must always be linked to a stopline")
                error = True

            for i in range(n):

                # We first find the closest stopline in order to link them

                min_dist=1000
                Orign_Point = (TrafficLightList[i].x0,TrafficLightList[i].y0)
                for j in range(len(self.stoplines)):

                    x1 =self.points[self.lines[self.stoplines[j].LID].BPID].Ly
                    y1= self.points[self.lines[self.stoplines[j].LID].BPID].Bx
                    point_of_interest = (x1,y1)
                    distance = dist(point_of_interest,Orign_Point)
                    if min_dist > distance:
                        min_dist = distance
                        stoplines_id = j
                        nb_clones = self.stoplines[j].SignID
                        lane_id = self.stoplines[j].LinkID
                if min_dist>10:
                    print("error : the traffic light at the coordinates", Orign_Point, " is too far away from the stopline linked to it")
                    error = True

                if error == False :
                    stopline_number = stoplines_id

                    for k in range(nb_clones): # Since a stopline and a traffic light can only be linked to one lane, we have to make clones if the road has more than 1 lane

                        pointID1 = self.points.create(TrafficLightList[i].x0, TrafficLightList[i].y0, 3.6)
                        pointID2 = self.points.create(TrafficLightList[i].x0, TrafficLightList[i].y0, 3.3)
                        pointID3 = self.points.create(TrafficLightList[i].x0, TrafficLightList[i].y0, 3.0)

                        VectorID1 = self.vectors.create(pointID1, TrafficLightList[i].h*180/np.pi)
                        VectorID2 = self.vectors.create(pointID2, TrafficLightList[i].h*180/np.pi)
                        VectorID3 = self.vectors.create(pointID3, TrafficLightList[i].h*180/np.pi)

                        SignDataID1 = self.signaldatas.create(VectorID1, 0, 1, self.stoplines[stopline_number].LinkID)  # That why creating stoplines in a specific order is important if not done then tfl and stoplines can be misslink
                        SignDataID2 = self.signaldatas.create(VectorID2, 0, 3, self.stoplines[stopline_number].LinkID)
                        SignDataID3 = self.signaldatas.create(VectorID3, 0, 2, self.stoplines[stopline_number].LinkID)



                        # Linking Stopline

                        self.stoplines[stopline_number].set_TLID(SignDataID1)

                        stopline_number +=1

            if error == True :
                return(error)

            for p in range(len(self.stoplines)):  # Now that evreything is done we have to put SIgnId of each stoplines to 0
                self.stoplines[p].set_SignID(0)   # Since SignID are not yet used, we assign them here and put them at 0
            return(error)


    # Returns the drivable lane data in the format:
    # [ [x0, y0, mag0, dir0, edge_color0, face_color0],
    #   [x1, y1, mag1, dir1, edge_color1, face_color1], ...]
    # Colors are used in the plot() method to generate graphical arrows.
    def __aggregate_lanes(self):
        data = []
        for l in self.lanes:
            y, x = self.points[self.nodes[l.get_node_start()].get_point()].get_xy()
            magnitude = l.get_length()
            direction = self.dtlanes[l.get_dtlane()].get_direction()
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
        for wl in self.whitelines:
            p0 = self.lines[wl.get_line()].get_point_start()
            p1 = self.lines[wl.get_line()].get_point_end()
            x0, y0 = self.points[p0].get_xy()
            x1, y1 = self.points[p1].get_xy()
            if len(data[-1]) == 0: data[-1] = [[x0, y0], [x1, y1]]
            elif data[-1][-1] == [x0, y0]: data[-1].append([x1, y1])
            else: data.append([[x0, y0], [x1, y1]])
        if data != [[]]: return data
        else: return None

    # Returns the road edge data in the format:
    # [ [[x0, y0], [x1, y1], ...], [[x0, y0], [x1, y1], ...] ]
    def __aggregate_edges(self):
        data = [[]]
        for re in self.roadedges:
            p0 = self.lines[re.get_line()].get_point_start()
            p1 = self.lines[re.get_line()].get_point_end()
            x0, y0 = self.points[p0].get_xy()
            x1, y1 = self.points[p1].get_xy()
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
        plt.grid(True)
        xmin = 1000
        xmax = -1000
        ymin = 1000
        ymax = -1000

        for x, y, m, d, ec, fc in self.__aggregate_lanes():
            plt.arrow(
                x, y, m * np.sin(d), m * np.cos(d),
                head_width=0.25, head_length=0.2, fc=fc, ec=ec,
                width=0.1, length_includes_head=True
            )
            if x < xmin :
                 xmin = x
            elif x > xmax :
                xmax = x
            if y < ymin :
                ymin = y
            elif y > ymax :
                ymax = y
        plt.axis ([xmin-2, xmax+2, ymin-2, ymax+2])

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

    def export(self, folder):
        '''Saves the entire vector map to the appropriate .csv files to the directory ./csv.

        .. warning:: This will overwrite the contents of ./csv.

        '''
        if os.path.isdir(folder) == False : # checks if the csv file exists and creates it if not
            os.mkdir(folder)

        self.points.export(folder+'point.csv')
        self.nodes.export(folder+'node.csv')
        self.lines.export(folder+'line.csv')
        self.dtlanes.export(folder+'dtlane.csv')
        self.lanes.export(folder+'lane.csv')
        self.whitelines.export(folder+'whiteline.csv')
        self.roadedges.export(folder+'roadedge.csv')
        self.vectors.export(folder+'vector.csv')
        self.signaldatas.export(folder+'signaldata.csv')
        self.stoplines.export(folder+'stopline.csv')
        self.crosswalks.export(folder+'crosswalk.csv')
        self.areas.export(folder+'area.csv')

    def readfiles (self, Files):
        '''
        read the .csv files. Creates nodes, points, lanes and dt_lanes
        '''
        count = 0
        l = []
        dt = []
        for file in Files :
            File1 = open(file, "r")
            content = File1.readlines()
            for i in range(1,len(content)) :
                line = []
                value = ""
                for j in range(len(content[i]))  :
                    char = content[i][j]
                    if (char != " ") and (char != "\n") and (char != ","):
                        value += char
                    if (char == " ") or j == (len(content[i])-1) or (char == ",") :
                        val = float(value)
                        value = ""
                        line.append(val)
                if count == 0 :
                    self.__new_node(line[5], line[4])
                elif count == 1 :
                    self.lanes.create(line[18], line[18], int(line[1]), int(line[4]), int(line[5]), int(line[2]), int(line[3]), line[14])
                elif count == 2 :
                    self.dtlanes.create(int(line[2]), line[1], line[3])
            count += 1



class VMList:
    '''This class is an ordered list of vector map objects with 1-based indexing to comply with the vector map format. Element addressing may be used for getting and setting, just as with the standard Python List. This class is to be used as both an Iterator and an Abstract Factory for constructing and accessing vector map data.

    :param type: The class of object to be aggregated.
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

    def remove_element(self, index):
        del self.__data[index-1]



    def create(self, *args, **kwargs):
        '''Creates a new object of the class declared on this objects's construction. Arguments and keyword arguments passed in here will be passed directly to the new object's constructor.

        :returns: int -- the ID of the new vector map entry.

        '''
        self.__data.append(self.__type(*args, **kwargs))
        return len(self.__data)

    def export(self, path):
        '''Prints all data to a file in the vector map .csv format. Every vector map object in this file should implement __str__() override which returns its data in the correct comma-separated order according to the vector map format. Each line of a vector map .csv file starts with a unique ID. These ID values are the indicies in this :class:`VMList` object.

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
    def __init__(self, x, y, z):
        self.B = 0.0        # Latitude
        self.L = 0.0        # Longitude
        self.H = z       # Altitude
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
    def __init__(self, SpeedLimit, RefSpeed, dtlane=0, node_start=0, node_end=0, lane_before=0,
            lane_after=0, length=0.0, junction='NORMAL', turn='STRAIGHT',cross=0):
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
        self.CrossID = cross        # ID of the crosswalk crossing the lane
        self.Span = length          # Lane lengh (between Nodes)
        self.LCnt = 1
        self.Lno = 1
        self.LimitVel = SpeedLimit
        self.RefVel = RefSpeed
        self.RoadSecID = 0
        self.LaneChgFG = 0

        self.set_junction(junction)
        self.set_turn(turn)

    def get_dtlane(self):
        return self.DID

    def get_LimitVel(self):
        return self.LimitVel

    def get_RefVel(self):
        return self.RefVel

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

    def set_LimitVel(self, Value):
        self.LimitVel = Value

    def set_RefVel(self, Value):
        self.RefVel = Value

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

class Vector:
    '''Vector map data saved to vector.csv. This class especially usefull for the definition of Traffic Light.

    :param line: The corresponding :class:`Vector` ID.
    :type line: int

    :param node: The corresponding :class:`Node` ID.            ########### update this !!
    :type node: int

    '''
    def __init__(self, point, Heading):
        self.pid = point       # Corresponding point ID
        self.hang = Heading    # Heading
        self.Vang = 90         # cf slide

    def __str__(self):
        data = [self.pid, self.hang, self.Vang]
        return ','.join(map(str, data))

class SignalData:
    '''Vector map data saved to signaldata.csv. This class especially usefull for the definition of Traffic Light.

    :param line: The corresponding :class:`Vector` ID.
    :type line: int

    :param node: The corresponding :class:`Node` ID.            ########### update this !!
    :type node: int

    '''
    def __init__(self, vector, plid, type, LinkID):
        self.VID = vector      # Corresponding Vector ID
        self.plid = plid
        self.type = type
        self.LinkID = LinkID       # cf slide

    def __str__(self):
        data = [self.VID, self.plid, self.type, self.LinkID]
        return ','.join(map(str, data))

class Stopline:
    '''Vector map data saved to stopline.csv. This class especially usefull for the definition of Traffic Light.

    :param line: The corresponding :class:`Vector` ID.
    :type line: int

    :param node: The corresponding :class:`Node` ID.            ########### update this !!
    :type node: int

    '''
    def __init__(self, LID, TLID, SignID, LinkID):
        self.LID = LID      # Corresponding Vector ID
        self.TLID = TLID
        self.SignID = SignID
        self.LinkID = LinkID       # cf slide

    def set_SignID(self, SignID):
        self.SignID = SignID

    def set_TLID(self, TLID):
        self.TLID = TLID

    def __str__(self):
        data = [self.LID, self.TLID, self.SignID, self.LinkID]
        return ','.join(map(str, data))
class Area:
    '''Vector map data saved to area.csv.

    :param line: the corresponding "class line" ID
    :type line: int

    :param area: the Area ID
    :type area: int

    '''

    def __init__(self,SLID,ELID):                # Area ID
        self.SLID = SLID                # ID of the first (start) line of the Area
        self.ELID = ELID                # ID of the last (end) line of the Area

    def set_SLID(self,line):
        self.SLID = line

    def set_ELID(self,line):
        self.ELID = line

    def __str__(self):
        data = [self.SLID, self.ELID]
        return ','.join(map(str, data))

class Crosswalk:
        '''Vector map data saved to crosswalk.csv

        :param cw: the crosswalk ID
        :type cw: int

        :param area: the corresponding "class area" ID
        :type area: int

        '''

        def __init__(self,AID):
            self.AID = AID
            self.Type = 1
            self.BdID = 0
            self.LinkID = 0

        def set_AID(self,area):
            self.AID = area

        def __str__(self):
            data = [self.AID, self.Type, self.BdID, self.LinkID]
            return ','.join(map(str,data))
