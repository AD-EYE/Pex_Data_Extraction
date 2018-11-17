from preproc import RoadProcessor
from vmap import VectorMap
import numpy as np
import parse

if __name__ == '__main__':
    roads = parse.get_roads(path='./data/connected_roads1.pex')
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
