from preproc import StaticalObjectProcessor,RoadProcessor
from vmap import VectorMap
import numpy as np
import parse

# config
PEX_FILE_LOCATION = "/home/adeye/AD-EYE_Core/AD-EYE/Experiments/W01_Base_Map/Simulation/W01_Base_Map.pex"

if __name__ == '__main__':


    Take_Speed_Prescan = True

    roads = parse.get_roads(path=PEX_FILE_LOCATION)
    statobj = parse.get_staticalobject(path=PEX_FILE_LOCATION)
    rproc = RoadProcessor(roads)
    rproc.create_lanes()
    rproc2 = StaticalObjectProcessor()
    rproc2.add_staticalobject(statobj)
    rproc2.create_statical_object()
    vm = VectorMap()
    for lane in rproc.lanes:
        if Take_Speed_Prescan:
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
    vm.merge_redundant_points()
    vm.rebuild_lane_conections()
    #vm.round_points()
    vm.export()
    vm.plot()
