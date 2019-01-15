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

    def adjust_for_turn(self, point):
        points = self.lanes
        for i in range(len(points)):
            if(dist(points[i - 1], point) <= 1.0):
                points.insert(i, list(point))
                break

    def adjust_for_roundabout(self, point):
        points = self.lanes
        for i in range(len(points)):
            if(dist(points[i - 1], point) <= 1.0):
                points.insert(i, list(point))
                break

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
                path = self.__get_path(exit.next_road)
                if exit.next_road == -1:
                    self.__add_roundabout_exit(exit)
                    continue
                if not path: continue
                self.__add_roundabout_exit(exit)

                for p in path:
                    road = p
                    if "XCrossing" in p.id: break
                    if not "Roundabout" in p.id:
                        road = roads.pop(p.id, None)
                        if road is None: break
                    self.__add_segment(road)
            roads.pop(roundabout.id, None)

    # Creates lanes traveling from each xcrossing until the path meets
    # another xcrossing or a dead end
    def __create_xcrossings(self, roads):
        xcrossings = self.__get_xcrossings()
        for xcrossing in xcrossings:
            rturns = []
            lturns = []

            for s in xcrossing.segments:
                rturns.append(s.rturn[0].getstart())
                rturns.append(s.rturn[0].getend())
                lturns.append(s.lturn[0].getend())
                lturns.append(s.lturn[0].getstart())

            for s in xcrossing.segments:
                self.__add_xcross(s, rturns, lturns)

                path = self.__get_path(s.next_road)
                if not path: continue

                for p in path:
                    road = roads.pop(p.id, None)
                    if not road:
                        break
                    self.__add_segment(road)

            roads.pop(xcrossing.id, None)

    # This function should only do someting if there are no roundabouts
    # or xcrossings. That means that the road network is a single path
    # between two dead ends.
    def __create_rest(self, roads):
        if roads:
            end = self.__get_end_roads()
            if end:
                path = self.__get_path(end.id)
                for p in path:
                    self.__add_segment(p)

    # Breaks down a roundabout into its lanes, edges and centers and creates
    # lanes for them
    def __add_roundabout_exit(self, exit):
        self.__add_edge(exit.e1)
        self.__add_edge(exit.e2)
        self.__add_center(exit.c)
        self.__add_lane(exit.l[0], True, junction_start = 'LEFT_MERGING')
        self.__add_lane(exit.l[1], False, junction_end = 'RIGHT_BRANCHING')

    # Breaks down an xcrossing into its lanes, edges and centers and creates
    # lanes for them
    def __add_xcross(self, xcross, rturns, lturns):
        self.__add_segment(xcross, rturns = rturns, lturns = lturns)
        self.__add_lane(xcross.lturn[0], False, 'LEFT_BRANCHING', 'RIGHT_MERGING')
        self.__add_lane(xcross.rturn[0], False, 'RIGHT_BRANCHING', 'LEFT_MERGING')

    # Creates a lane which consists of a single path of x and y coordinates.
    # The path can have a junction end or start
    def __add_lane(self, lane, reverse, junction_end = 'NORMAL', junction_start = 'NORMAL', rturns = None, lturns = None, epoints = None):
        l = []
        for (x, y) in lane:
            l.append([x, y])
        newlane = Lane(l, junction_end, junction_start, reverse)
        if(rturns):
            for point in rturns:
                newlane.adjust_for_turn(point)
        if(lturns):
            for point in lturns:
                newlane.adjust_for_turn(point)
        if(epoints):
            for point in epoints:
                newlane.adjust_for_roundabout(point)
        self.lanes.append(newlane)

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
        self.__add_lane(lane.l[0], not lane.isturned, rturns = rturns, lturns = lturns)
        self.__add_lane(lane.l[1], lane.isturned, rturns = rturns, lturns = lturns, epoints = epoints)
        self.__add_center(lane.c)
        self.__add_edge(lane.e1)
        self.__add_edge(lane.e2)

    # Gets a path for the road segment with the given id
    # The path starts at the segmend and ends at the next roundabout,
    # xcrossing or dead end.
    def __get_path(self, id):
        roads = self.roads
        segments = []
        if id in roads:
            road = roads[id]
        else:
            return segments
        segments.append(road)
        while True:
            if road.next_road == -1:
                break
            nr = roads[road.next_road]

            if nr.next_road == road.id:
                self.__turn_road(nr, road.id)
            if "Roundabout" in nr.id:
                segments.append(self.__get_exit_lane(nr, road.id))
                break
            elif "XCrossing" in nr.id:
                break
            road = nr
            segments.append(road)
        return segments

    # Fetches a exit lane segment of a roundabout
    def __get_exit_lane(self, roundabout, roadid):
        for exit in roundabout.exit_lanes:
            if exit.next_road == roadid:
                return exit

    # Fetches a dead end road, that is a road that is not connected
    # to another road segment on either end
    def __get_end_roads(self):
        roads = self.roads
        for id in roads.keys():
            if not "Roundabout" in id and roads[id].previous_road == -1:
                return roads[id]
        return None

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
