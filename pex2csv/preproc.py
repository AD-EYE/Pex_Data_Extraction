import numpy as np

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
        self.roads = roads
        self.process_order()
        self.create_lanes()

    def process_order(self):
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

    def fix_order(self):
        roads = self.roads
        road = self.getfirst()

        for i in range(self.number_of_roads()):
            nr = self.getnext(road)

            if (nr != -1 and roads[nr].next_road == road):
                roads[nr].next_road = roads[nr].previous_road
                roads[nr].previous_road = road
            road = nr

    def create_lanes(self):
        roads = self.roads.copy()
        roundabouts = self.get_roundabouts()
        end = self.get_end_roads()
        xcrossings = self.get_xcrossings()

        for roundabout in roundabouts:
            self.__add_segment(roundabout)

            for exit in roundabout.exit_lanes:
                paths = self.get_paths(exit.next_road)
                if not paths: continue
                self.__add_roundabout_exit(exit)

                for path in paths:
                    road = path
                    if "XCrossing" in path.id: break
                    if not "Roundabout" in path.id:
                        road = roads.pop(path.id, None)
                    self.__add_segment(road)

        for xcrossing in xcrossings:
            for s in xcrossing.segments:
                self.__add_xcross(s)
                paths = self.get_paths(s.next_road)
                if not paths: continue

                for path in paths:
                    road = roads.pop(path.id, None)
                    if not road:
                        break
                    self.__add_segment(road)

        #if end:
         #   paths = self.get_path_from_end(end.id)
         #   for path in paths:
         #       self.add_lane(path)

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

    def get_paths(self, id):
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
                nr.turn_road()
                nr.next_road = nr.previous_road
                nr.previous_road = road.id
            if "Roundabout" in nr.id:
                xl = self.get_exit_lane(nr, road.id)
                segments.append(xl)
                break
            elif "XCrossing" in nr.id:
                break
            elif road.next_road == -1:
                break
            road = nr
            segments.append(road)
        return segments

    def get_path_from_end(self, id):
        roads = self.roads
        road = roads[id]
        segments = []
        segments.append(road)

        while True:
            if road.next_road == -1: break
            nr = roads[road.next_road]
            if "Roundabout" in nr.id: break

            if nr.next_road == road.id:
                nr.turn_road()
                nr.next_road = nr.previous_road
                nr.previous_road = road.id

            segments.append(nr)
            road = nr

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

def dist(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
