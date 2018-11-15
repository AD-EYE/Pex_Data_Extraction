from matplotlib import pyplot as plt
from vmap import VectorMap
import numpy as np
import parse
import inspect

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
    vm.make_lane(lanes, junction_end='RIGHT_MERGING')
    vm.make_line(edges, line_type='EDGE')
    vm.make_line(centers, line_type='CENTER')
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
