from preproc import StaticalObjectProcessor,RoadProcessor
from vmap import VectorMap
import numpy as np
import parse

# config
PEX_FILE_LOCATION = "C:\\Users\\nico7\\Desktop\\Round3.pex"

if __name__ == '__main__':


    Take_Speed_Pescan = True

    roads = parse.get_roads(path=PEX_FILE_LOCATION)
    statobj = parse.get_staticalobject(path=PEX_FILE_LOCATION)
    rproc = RoadProcessor(Take_Speed_Pescan)
    rproc.add_roads(roads)
    rproc.create_lanes()
    rproc2 = StaticalObjectProcessor()
    rproc2.add_staticalobject(statobj)
    rproc2.create_statical_object()
    vm = VectorMap()
    for lane in rproc.lanes:
        if Take_Speed_Pescan:
            vm.make_lane(lane.SpeedLimit, lane.RefSpeed, lane.get_lanes(), junction_end=lane.get_junction_end(), junction_start=lane.get_junction_start())
        else:
            vm.make_lane(lane.DefinedSpeed, lane.DefinedSpeed, lane.get_lanes(), junction_end=lane.get_junction_end(), junction_start=lane.get_junction_start())






    # Commented out since centers and edges seem to crash autoware
    # for edge in rproc.edges:
    #     vm.make_line(edge.get_lanes(), line_type='EDGE')
    #for center in rproc.centers:
    #    vm.make_line(center.get_lanes(), line_type='CENTER')
    vm.make_Stoplines(rproc.stoplines)
    vm.make_TrafficLight(rproc2.TrfLight)
    vm.export()
    vm.plot()
