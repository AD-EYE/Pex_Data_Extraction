from preproc import RoadProcessor
from vmap import VectorMap
import numpy as np
import parse

if __name__ == '__main__':
    roads = parse.get_roads(path='./data/connected_roads1.pex')
    rproc = RoadProcessor(roads)

    centers = []
    edges = []
    tlanes = rproc.get_lanes()

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
            for road in roads[id].exit_lanes:
                for (x, y) in road.e1:
                    edges.append([x, y])
                for (x, y) in road.e2:
                    edges.append([x, y])
                for path in road.l:
                    for (x, y) in path:
                        lanes.append([x, y])
        except Exception as e: print(e)

    centers = np.array(centers)
    edges = np.array(edges)

    vm = VectorMap()
    for tlane in tlanes:
        vm.make_lane(tlane, junction_end='RIGHT_MERGING')
    vm.make_line(edges, line_type='EDGE')
    vm.make_line(centers, line_type='CENTER')
    vm.export()
    vm.plot()
