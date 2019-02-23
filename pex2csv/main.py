from preproc import RoadProcessor
from vmap import VectorMap
import numpy as np
import parse

# config
PEX_FILE_LOCATION = '/home/naveenm/AD-EYE-WASP/AD-EYE/PreScan_Experiments/Base_Map/Simulation/Base_Map_S.pex'

if __name__ == '__main__':
    roads = parse.get_roads(path=PEX_FILE_LOCATION)
    rproc = RoadProcessor()
    rproc.add_roads(roads)
    rproc.create_lanes()
    vm = VectorMap()

    for lane in rproc.lanes:
        vm.make_lane(lane.get_lanes(), junction_end=lane.get_junction_end(), junction_start=lane.get_junction_start())
    # Commented out since centers and edges seem to crash autoware
    #for edge in rproc.edges:
    #    vm.make_line(edge.get_lanes(), line_type='EDGE')
    #for center in rproc.centers:
    #    vm.make_line(center.get_lanes(), line_type='CENTER')

    vm.export()
    vm.plot()
