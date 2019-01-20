'''This module contains :class:RoadProcessor that processes road segments in order to easily feed coordinates to the vector mapping module.

Only :class:RoadProcessor should be used externally.

'''
import numpy as np
from utils import dist

# A wrapper class for lanes that will be incrementally fed to the vecor mapping module
class Lane(object):
    def __init__(self, lanes, junction_end='NORMAL', junction_start='NORMAL', reverse=False):
        self.lanes = lanes
        self.junction_end = junction_end
        self.junction_start = junction_start

        if reverse:
            self.__reverse_lanes()

    def get_lanes(self):
        return np.array(self.lanes)

    def get_junction_end(self):
        return self.junction_end

    def get_junction_start(self):
        return self.junction_start

    def connect_turn_to_lane(self, point):
        points = self.lanes
        for i in range(len(points)):
            if(dist(points[i - 1], point) <= 1.0):
                points[i] = list(point)
                break

    def extend_turn(self, lane, point_index):
        counter = 0
        for (x, y) in lane:
            if counter == point_index:
                self.lanes = [[x, y]] + self.lanes
                break
            counter += 1

    def adjust_for_roundabout(self, point):
        points = self.lanes
        for i in range(len(points)):
            if(dist(points[i - 1], point) <= 1.0):
                points.insert(i, list(point))
                break

    def append(self, point):
        self.lanes.append(point)

    def prepend(self, point):
        self.lanes = [point] + self.lanes

    def __reverse_lanes(self):
        self.lanes = self.lanes[::-1]

class RoadProcessor(object):
    '''
    Class responsible for processing the road segments for the vmap module
    '''
    def __init__(self):
        self.lanes = []
        self.centers = []
        self.edges = []
        self.roads = []

    def add_roads(self, roads):
        self.roads = roads

    def create_lanes(self):
        self.__process_order()
        self.__create_lanes()

    # Goes through all road segments and marks which ones are connected
    # at the start and which ones are connected at the end
    def __process_order(self):
        roads = self.roads
        for id1 in roads.keys():
            if "Roundabout" in id1:
                for exit in roads[id1].exit_lanes:
                    for id2 in roads.keys():
                        if id1 == id2: continue
                        if "XCrossing" in id2:
                            for s in roads[id2].segments:
                                self.__set_order(exit, s)
                        self.__set_order(exit, roads[id2])
            elif "XCrossing" in id1:
                for segment in roads[id1].segments:
                    for id2 in roads.keys():
                        if id1 == id2: continue
                        self.__set_order(segment, roads[id2])
            for id2 in roads.keys():
                if id1 == id2: continue
                self.__set_order(roads[id1], roads[id2])

    # Takes two road segments and finds if they are connected and
    # marks them accordingly
    def __set_order(self, road1, road2):
        if dist(road1.getstart(), road2.getstart()) <= 1.0:
            road1.previous_road = road2.id
            road2.previous_road = road1.id
        elif dist(road1.getstart(), road2.getend()) <= 1.0:
            road1.previous_road = road2.id
            road2.next_road = road1.id
        elif dist(road1.getend(), road2.getstart()) <= 1.0:
            road1.next_road = road2.id
            road2.previous_road = road1.id
        elif dist(road1.getend(), road2.getend()) <= 1.0:
            road1.next_road = road2.id
            road2.next_road = road1.id

    # Creates the lanes in the correct order in ragards to the vmap module
    def __create_lanes(self):
        roads = self.roads.copy()

        self.__create_roundabouts(roads)
        self.__create_xcrossings(roads)
        self.__create_rest(roads)

    # Creates lanes traveling from each roundabout until the path meets
    # another roundabout, xcrossing or a dead end
    def __create_roundabouts(self, roads):
        roundabouts = self.__get_roundabouts()
        for roundabout in roundabouts:
            epoints = []

            for exit in roundabout.exit_lanes:
                epoints.append(exit.l[0].getend())
                epoints.append(exit.l[1].getend())

            self.__add_segment(roundabout, epoints = epoints)

            for exit in roundabout.exit_lanes:
                self.__add_roundabout_exit(exit)

            roads.pop(roundabout.id, None)

    # Creates lanes traveling from each xcrossing until the path meets
    # another xcrossing or a dead end
    def __create_xcrossings(self, roads):
        xcrossings = self.__get_xcrossings()
        for xcrossing in xcrossings:
            rturns = []
            lturns = []

            for s in xcrossing.segments:
                rturns.append(s.rturn[0].getend())
                lturns.append(s.lturn[0].getend())

            for s in xcrossing.segments:
                self.__add_xcross(s, rturns, lturns)

            roads.pop(xcrossing.id, None)

    # This function should only do someting if there are no roundabouts
    # or xcrossings. That means that the road network is a single path
    # between two dead ends.
    def __create_rest(self, roads):
        for id in roads:
            self.__add_segment(self.roads[id])

    # Breaks down a roundabout into its lanes, edges and centers and creates
    # lanes for them
    def __add_roundabout_exit(self, exit):
        self.__add_edge(exit.e1)
        self.__add_edge(exit.e2)
        self.__add_center(exit.c)
        self.__add_lane(exit.id, exit.l[0], True, junction_start = 'LEFT_MERGING')
        self.__add_lane(exit.id, exit.l[1], False, junction_end = 'RIGHT_BRANCHING')

    # Breaks down an xcrossing into its lanes, edges and centers and creates
    # lanes for them
    def __add_xcross(self, xcross, rturns, lturns):
        self.__add_segment(xcross, rturns = rturns, lturns = lturns)
        self.__add_turn(xcross.lturn[0], xcross.l[1], False, 13, 'LEFT_BRANCHING', 'RIGHT_MERGING')
        self.__add_turn(xcross.rturn[0], xcross.l[1], False, 12, 'RIGHT_BRANCHING', 'LEFT_MERGING')

    def __add_turn(self, turn, lane, reverse, point_index, junction_end = 'Normal', junction_start = 'NORMAL'):
        l = []
        for (x, y) in turn:
            l.append([x, y])
        newlane = Lane(l, junction_end, junction_start, reverse)
        newlane.extend_turn(lane, point_index = point_index)
        self.lanes.append(newlane)

    # Creates a lane which consists of a single path of x and y coordinates.
    # The path can have a junction end or start
    def __add_lane(self, id, lane, reverse, junction_end = 'NORMAL', junction_start = 'NORMAL', rturns = None, lturns = None, epoints = None):
        l = []
        for (x, y) in lane:
            l.append([x, y])
        newlane = Lane(l, junction_end, junction_start, reverse)
        if(rturns):
            for point in rturns:
                newlane.connect_turn_to_lane(point)
        if(lturns):
            for point in lturns:
                newlane.connect_turn_to_lane(point)
        if(epoints):
            for point in epoints:
                newlane.adjust_for_roundabout(point)

        if 'Curved' in id:
            self.__fix_bezier_gap(id, newlane, reverse)
        self.lanes.append(newlane)

    def __fix_bezier_gap(self, id, lane, append):
        nextroad = self.roads[id].next_road
        road = self.roads[id]
        nroad = self.roads[nextroad]

        if 'Roundabout' in nextroad:
            for exit in self.roads[nextroad].exit_lanes:
                if exit.next_road == id:
                    if append:
                        lane.prepend(exit.l[0].getstart())
                    else:
                        lane.append(exit.l[1].getstart())
        elif 'Xcrossing' in nextroad:
            for segment in self.roads[nextroad].segments:
                if segment.next_road == id:
                    if append:
                        lane.prepend(segment.l[0].getstart())
                    else:
                        lane.append(segment.l[1].getstart())
        else:
            road = self.roads[id]
            if not dist(road.getend(), nroad.getend()) <= 0.1 or not dist(road.getend(), nroad.getstart()) >= 0.1:
                return

            if append:
                lane.prepend(road.l[0].getend())
            else:
                lane.append(road.l[1].getend())

    def __add_center(self, center):
        for path in center:
            c = []
            for (x, y) in path:
                c.append([x, y])
            self.centers.append(Lane(c))

    def __add_edge(self, edge):
        for path in edge:
            e = []
            for (x, y) in path:
                e.append([x, y])
            self.edges.append(Lane(e))

    # Breaks down a road segment into lanes, edges and center for the
    # vmap module
    def __add_segment(self, lane, rturns = None, lturns = None, epoints = None):
        self.__add_lane(lane.id, lane.l[0], not lane.isturned, rturns = rturns, lturns = lturns)
        self.__add_lane(lane.id, lane.l[1], lane.isturned, rturns = rturns, lturns = lturns, epoints = epoints)
        self.__add_center(lane.c)
        self.__add_edge(lane.e1)
        self.__add_edge(lane.e2)

    # Fetches a exit lane segment of a roundabout
    def __get_exit_lane(self, roundabout, roadid):
        for exit in roundabout.exit_lanes:
            if exit.next_road == roadid:
                return exit

    # Fetches all roundabouts in the road network
    def __get_roundabouts(self):
        roads = self.roads
        ra = []
        for id in roads.keys():
            if "Roundabout" in id:
                ra.append(roads[id])
        return ra

    # Fetches all xcrossing in the road network
    def __get_xcrossings(self):
        roads = self.roads
        xcross = []
        for id in roads.keys():
            if "XCrossing" in id:
                xcross.append(roads[id])
        return xcross

    # Turns the road so the lanes will have the correct direction.
    def __turn_road(self, road, previous_road_id):
        road.turn_road()
        road.next_road = road.previous_road
        road.previous_road = previous_road_id
