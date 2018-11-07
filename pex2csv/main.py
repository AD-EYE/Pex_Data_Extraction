from matplotlib import pyplot as plt
from vmap import VectorMap
import numpy as np
import parse
import inspect

if __name__ == '__main__':
    roads = parse.get_roads(path='./data/connected_roads1.pex')

    centers = []
    edges = []
    lanes = []

    for id in roads.keys():
        for (x, y) in roads[id].c:
            centers.append([x, y])
        try:
            for (x, y) in roads[id].e1:
                edges.append([x, y])
            for (x, y) in roads[id].e2:
                edges.append([x, y])
            for (x, y) in roads[id].l1:
                lanes.append([x, y])
            for (x, y) in roads[id].l2:
                lanes.append([x, y])
        except: pass

    centers = np.array(centers)
    edges = np.array(edges)
    lanes = np.array(lanes)

    plt.plot(centers[:,0], centers[:,1], 'bo')
    plt.plot(edges[:,0], edges[:,1], 'ro')
    plt.plot(lanes[:,0], lanes[:,1], 'ko')
    plt.legend(['center', 'edge', 'lane'])
    plt.axis('equal')
    plt.grid(True)
    plt.show()

    vm = VectorMap()
    vm.make_lane(lanes, junction_end='RIGHT_MERGING')
    vm.export()
