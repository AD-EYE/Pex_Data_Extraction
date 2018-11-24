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
        vm.make_lane(lane.get_lanes(), junction_end=lane.get_junction_end(), junction_start=lane.get_junction_start())
    for edge in rproc.edges:
        vm.make_line(edge.get_lanes(), line_type='EDGE')
    for center in rproc.centers:
        vm.make_line(center.get_lanes(), line_type='CENTER')

    vm.export()
    vm.plot()
