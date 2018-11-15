from matplotlib import pyplot as plt
from vmap import VectorMap
import numpy as np
import parse
import inspect
from preproc import RoadProcessor

if __name__ == '__main__':
    roads = parse.get_roads(path='./data/connected_roads1.pex')
    rproc = RoadProcessor(roads)

    centers = []
    edges = []
    lanes = []
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
            for path in roads[id].l:
                for (x, y) in path:
                    lanes.append([x, y])
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
    lanes = np.array(lanes)

    plt.figure(1)
    plt.title('Point Cloud')
    plt.plot(centers[:,0], centers[:,1], 'bo')
    plt.plot(edges[:,0], edges[:,1], 'ro')
    plt.plot(lanes[:,0], lanes[:,1], 'ko')
    plt.legend(['center', 'edge', 'lane'])
    plt.axis('equal')
    plt.grid(True)
    xmin, xmax = plt.xlim()
    ymin, ymax = plt.ylim()

    vm = VectorMap()
    for tlane in tlanes:
        vm.make_lane(tlane, junction_end='RIGHT_MERGING')
    vm.make_line(edges, type='EDGE')
    vm.make_line(centers, type='CENTER')
    vm.export()

    plt.figure(2)
    plt.title('Vector Map')
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    plt.grid(True)
    for x, y, m, d in vm.get_all_vectors():
        plt.arrow(
            x, y, m * np.cos(d), m * np.sin(d),
            head_width=0.25, head_length=0.2, fc='w', ec='k',
            width=0.1, length_includes_head=True
        )

    plt.show()
