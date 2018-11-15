from vmap import VectorMap
from vmplot import vmplot
import numpy as np
import parse

def dist(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def process_order(roads):
    for id1 in roads.keys():
        for id2 in roads.keys():
            if id1 == id2: continue
            if dist(roads[id1].getstart(), roads[id2].getstart()) <= 1.0:
                roads[id1].previous_road = id2
                roads[id2].previous_road = id1
            elif dist(roads[id1].getstart(), roads[id2].getend()) <= 1.0:
                roads[id1].previous_road = id2
                roads[id2].next_road = id1
            elif dist(roads[id1].getend(), roads[id2].getstart()) <= 1.0:
                roads[id1].next_road = id2
                roads[id2].previous_road = id1
            elif dist(roads[id1].getend(), roads[id2].getend()) <= 1.0:
                roads[id1].next_road = id2
                roads[id2].next_road = id1

if __name__ == '__main__':
    roads = parse.get_roads(path='./data/connected_roads1.pex')

    centers = []
    edges = []
    lanes = []

    for id in roads.keys():
        for (x, y) in roads[id].c:
            centers.append([x, y])
        try:
            if type(roads[id].e1) is list:
                for path in roads[id].e1:
                    for (x, y) in path:
                        edges.append([x, y])
            else:
                for (x, y) in roads[id].e1:
                    edges.append([x, y])
            for (x, y) in roads[id].e2:
                edges.append([x, y])
            for (x, y) in roads[id].l1:
                lanes.append([x, y])
            for (x, y) in roads[id].l2:
                lanes.append([x, y])
            for path in roads[id].x:
                for (x, y) in path:
                    edges.append([x, y])
            for path in roads[id].xl:
                for (x, y) in path:
                    lanes.append([x, y])
        except Exception as e: print(e)

    centers = np.array(centers)
    edges = np.array(edges)
    lanes = np.array(lanes)

    vm = VectorMap()
    vm.make_lane(lanes, junction_end='RIGHT_MERGING')
    vm.make_line(edges, line_type='EDGE')
    vm.make_line(centers, line_type='CENTER')
    vm.export()

    # Blocking function.
    vmplot(vm)
