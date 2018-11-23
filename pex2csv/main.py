from matplotlib import pyplot as plt
from preproc import RoadProcessor
from vmap import VectorMap
import numpy as np
import parse


if __name__ == '__main__':
    roads = parse.get_roads(path='./data/base_experiment.pex')
    rproc = RoadProcessor(roads)
    vm = VectorMap()

    for lane in rproc.lanes:
        vm.make_lane(lane, junction_end='LEFT_BRANCHING', junction_start='LEFT_MERGING')
    for edge in rproc.edges:
        vm.make_line(edge, line_type='EDGE')
    for center in rproc.centers:
        vm.make_line(center, line_type='CENTER')

    vm.export()
    vm.plot()

    centers = []
    edges = []
    lanes = []
    for id in roads.keys():
        try:
            for path in roads[id].c:
                for (x, y) in path:
                    centers.append([x, y])
            for path in roads[id].l:
                for (x, y) in path:
                    lanes.append([x, y])
            for path in roads[id].e:
                for (x, y) in path:
                    edges.append([x, y])
            if "Roundabout" in id:
                for xl in roads[id].exit_lanes:
                    for path in xl.c:
                        for(x, y) in path:
                            centers.append([x, y])
                    for path in xl.e:
                        for(x, y) in path:
                            edges.append([x, y])
                    for path in xl.l:
                        for(x, y) in path:
                            lanes.append([x, y])
            elif "XCrossing" in id:
                for s in roads[id].segments:
                    for path in s.c:
                        for (x, y) in path:
                            centers.append([x, y])
                    for path in s.e:
                        for (x, y) in path:
                            edges.append([x, y])
                    for path in s.l:
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
    #plt.show()
