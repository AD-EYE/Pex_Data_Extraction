from preproc import StaticalObjectProcessor,RoadProcessor
from vmap import VectorMap
import numpy as np
import parse
import sys

# config
PEX_FILE_LOCATION = "/home/adeye/AD-EYE_Core/AD-EYE/Experiments/W00_global_test_world/Simulation/Experiment/Experiment.pex"
VECTORMAP_FILES_FOLDER = "/home/adeye/AD-EYE_Core/Pex_Data_Extraction/pex2csv/csv/"
OnlyVisualisation = True # True if you want to generate the visualisation of the files from VECTORMAP_FILES_FOLDER,
                         # False if if you want to create the vector map of PEX_FILE_LOCATION

if OnlyVisualisation == False :
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
        cross = vm.make_Area(rproc.crosswalk)
        for lane in rproc.lanes:
            if Take_Speed_Prescan:
                vm.make_lane(cross, lane.SpeedLimit, lane.RefSpeed, lane.get_lanes(), junction_end=lane.get_junction_end(), junction_start=lane.get_junction_start())
            else:
                vm.make_lane(cross, lane.DefinedSpeed, lane.DefinedSpeed, lane.get_lanes(), junction_end=lane.get_junction_end(), junction_start=lane.get_junction_start())




        # Commented out since centers and edges seem to crash autoware
        # for edge in rproc.edges:
        #     vm.make_line(edge.get_lanes(), line_type='EDGE')
        #for center in rproc.centers:
        #    vm.make_line(center.get_lanes(), line_type='CENTER')
        vm.make_crosswalk(cross)
        vm.make_Stoplines(rproc.stoplines)
        error = vm.make_TrafficLight(rproc2.TrfLight)
        if error == True :
            sys.exit()
        vm.merge_redundant_points()
        vm.rebuild_lane_conections()
        vm.export()
        vm.plot()

else :
    vm = VectorMap()
    Files = [VECTORMAP_FILES_FOLDER+"point.csv",VECTORMAP_FILES_FOLDER+"lane.csv",VECTORMAP_FILES_FOLDER+"dtlane.csv"]
    vm.readfiles(Files)
    vm.merge_redundant_points()
    vm.rebuild_lane_conections()
    vm.plot()
