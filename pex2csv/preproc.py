import numpy as np

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

        for id in roads.keys():
            if "Roundabout" in id:
                for exit in roads[id].exit_lanes:
                    print("Next road: ", exit.next_road)

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
            self.add_lane(roundabout)

            for exit in roundabout.exit_lanes:
                paths = self.get_paths(exit.next_road)
                if not paths: continue
                self.add_lane(exit)

                for path in paths:
                    road = path
                    if "XCrossing" in path.id: break
                    if not "Roundabout" in path.id:
                        road = roads.pop(path.id, None)
                    self.add_lane(road)

        for xcrossing in xcrossings:
            for s in xcrossing.segments:
                self.add_lane(s)
                paths = self.get_paths(s.next_road)
                if not paths: continue

                for path in paths:
                    road = roads.pop(path.id, None)
                    if not road:
                        break
                    self.add_lane(road)

        #if end:
         #   paths = self.get_path_from_end(end.id)
         #   for path in paths:
         #       self.add_lane(path)

    def add_lane(self, lane):
        l1 = []
        l2 = []
        center = []
        e1 = []
        e2 = []
        edges = []
        if lane.isturned:
            for (x, y) in lane.l[1]:
                l1.append([x, y])
            for (x, y) in lane.l[0]:
                l2.append([x, y])
        else:
            for (x, y) in lane.l[0]:
                l1.append([x, y])
            for (x, y) in lane.l[1]:
                l2.append([x, y])
        for path in lane.c:
            for (x, y) in path:
                center.append([x, y])
        for path in lane.e1:
            for (x, y) in path:
                e1.append([x, y])
            self.edges.append(np.array(e1))
            e1 = []
        for path in lane.e2:
            for (x, y) in path:
                e2.append([x, y])
            self.edges.append(np.array(e2))

        if lane.isturned:
            self.lanes.append(np.array(l1))
            self.lanes.append(np.array(list(reversed(l2))))
        else:
            self.lanes.append(np.array(list(reversed(l1))))
            self.lanes.append(np.array(l2))

        self.centers.append(np.array(center))

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
