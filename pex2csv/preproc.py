import numpy as np
from utils import dist

class Lane(object):
    def __init__(self, lanes, junction_end='NORMAL', junction_start='NORMAL', reverse=False):
        self.lanes = lanes
        self.junction_end = junction_end
        self.junction_start = junction_start

        if reverse:
            self.__reverse_lanes()

    def get_lanes(self):
        return self.lanes

    def get_junction_end(self):
        return self.junction_end

    def get_junction_start(self):
        return self.junction_start

    def __reverse_lanes(self):
        self.lanes = self.lanes[::-1]

class RoadProcessor(object):
    def __init__(self, roads):
        self.lanes = []
        self.centers = []
        self.edges = []
        self.roads = []

    def add_roads(self, roads):
        self.roads = roads

    def create_lanes(self):
        self.__process_order()
        self.__create_lanes()

    def __process_order(self):
        roads = self.roads
        for id1 in roads.keys():
            if "Roundabout" in id1:
                for exit in roads[id1].exit_lanes:
                    for id2 in roads.keys():
                        if id1 == id2: continue
                        if "XCrossing" in id2:
                            for s in roads[id2].segments:
                                self.set_order(exit, s)
                        self.set_order(exit, roads[id2])
            elif "XCrossing" in id1:
                for segment in roads[id1].segments:
                    for id2 in roads.keys():
                        if id1 == id2: continue
                        self.set_order(segment, roads[id2])
            for id2 in roads.keys():
                if id1 == id2: continue
                self.set_order(roads[id1], roads[id2])

    def set_order(self, road1, road2):
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

    def __create_lanes(self):
        roads = self.roads.copy()
        roundabouts = self.get_roundabouts()
        xcrossings = self.get_xcrossings()

        for roundabout in roundabouts:
            self.__add_segment(roundabout)

            for exit in roundabout.exit_lanes:
                path = self.__get_path(exit.next_road)
                if not path: continue
                self.__add_roundabout_exit(exit)

                for p in path:
                    road = p
                    if "XCrossing" in p.id: break
                    if not "Roundabout" in p.id:
                        road = roads.pop(p.id, None)
                        if road is None: break
                    self.__add_segment(road)

        for xcrossing in xcrossings:
            for s in xcrossing.segments:
                self.__add_xcross(s)
                path = self.__get_path(s.next_road)
                if not path: continue

                for p in path:
                    road = roads.pop(p.id, None)
                    if not road:
                        break
                    self.__add_segment(road)

            roads.pop(xcrossing.id, None)

        if roads:
            end = self.get_end_roads()
            if end:
                path = self.__get_path(end.id)
                for p in path:
                    self.__add_segment(p)

    def __add_roundabout_exit(self, exit):
        self.__add_edge(exit.e1)
        self.__add_edge(exit.e2)
        self.__add_center(exit.c)
        self.__add_lane(exit.l[0], True, junction_start = 'LEFT_MERGING')
        self.__add_lane(exit.l[1], False, junction_end = 'RIGHT_BRANCHING')

    def __add_xcross(self, xcross):
        self.__add_segment(xcross)
        self.__add_lane(xcross.rturn[0], False, 'RIGHT_BRANCHING', 'LEFT_MERGING')
        self.__add_lane(xcross.lturn[0], False, 'LEFT_BRANCHING', 'RIGHT_MERGING')

    def __add_lane(self, lane, reverse, junction_end = 'NORMAL', junction_start = 'NORMAL'):
        l = []
        for (x, y) in lane:
            l.append([x, y])
        self.lanes.append(Lane(np.array(l), junction_end, junction_start, reverse))

    def __add_center(self, center):
        for path in center:
            c = []
            for (x, y) in path:
                c.append([x, y])
            self.centers.append(Lane(np.array(c)))

    def __add_edge(self, edge):
        for path in edge:
            e = []
            for (x, y) in path:
                e.append([x, y])
            self.edges.append(Lane(np.array(e)))

    def __add_segment(self, lane):
        self.__add_lane(lane.l[0], not lane.isturned)
        self.__add_lane(lane.l[1], lane.isturned)
        self.__add_center(lane.c)
        self.__add_edge(lane.e1)
        self.__add_edge(lane.e2)

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
                segments.append(self.get_exit_lane(nr, road.id))
                break
            elif "XCrossing" in nr.id:
                break
            road = nr
            segments.append(road)
        return segments

    def get_exit_lane(self, roundabout, roadid):
        for exit in roundabout.exit_lanes:
            if exit.next_road == roadid:
                return exit

    def getnext(self, id):
        return self.roads[id].next_road

    def get_end_roads(self):
        roads = self.roads
        for id in roads.keys():
            if not "Roundabout" in id and roads[id].previous_road == -1:
                return roads[id]
        return None

    def get_roundabouts(self):
        roads = self.roads
        ra = []
        for id in roads.keys():
            if "Roundabout" in id:
                ra.append(roads[id])
        return ra

    def get_xcrossings(self):
        roads = self.roads
        xcross = []
        for id in roads.keys():
            if "XCrossing" in id:
                xcross.append(roads[id])
        return xcross

    def __turn_road(self, road, previous_road_id):
        road.turn_road()
        road.next_road = road.previous_road
        road.previous_road = previous_road_id
