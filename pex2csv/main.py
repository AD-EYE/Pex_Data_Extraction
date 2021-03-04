import numpy as np
import sys

import parse
from preproc import StaticObjectProcessor,RoadProcessor
from vmap import VectorMap


# config
PEX_FILE_LOCATION = "/home/adeye/Downloads/VectorMapTestSmallest.pex"
# PEX_FILE_LOCATION = "/home/adeye/AD-EYE_Core/AD-EYE/Experiments/W05_KTH/Simulation/W05_KTH.pex"
VECTORMAP_FILES_FOLDER = "/home/adeye/AD-EYE_Core/Pex_Data_Extraction/pex2csv/csv/"
OnlyVisualisation = False # True if you want to generate the visualisation of the files from VECTORMAP_FILES_FOLDER,
                         # False if if you want to create the vector map of PEX_FILE_LOCATION
USE_PRESCAN_SPEED = True

if OnlyVisualisation == False :
    if __name__ == '__main__':


        roads = parse.get_roads(path=PEX_FILE_LOCATION)
        static_objects = parse.get_staticobject(path=PEX_FILE_LOCATION)
        roads_processor = RoadProcessor(roads)
        roads_processor.create_lanes()
        static_objects_processor = StaticObjectProcessor()
        static_objects_processor.add_staticobject(static_objects)
        static_objects_processor.create_static_object()
        vector_map = VectorMap()
        crosswalks = vector_map.make_Area(roads_processor.crosswalks)
        for lane in roads_processor.lanes:
            if USE_PRESCAN_SPEED:
                vector_map.make_lane(crosswalks, lane.SpeedLimit, lane.RefSpeed, lane.get_lanes(), junction_end=lane.get_junction_end(), junction_start=lane.get_junction_start())
            else:
                vector_map.make_lane(crosswalks, lane.DefinedSpeed, lane.DefinedSpeed, lane.get_lanes(), junction_end=lane.get_junction_end(), junction_start=lane.get_junction_start())




        # Commented out since centers and edges seem to crash autoware
        # for edge in roads_processor.edges:
        #     vector_map.make_line(edge.get_lanes(), line_type='EDGE')
        #for center in roads_processor.centers:
        #    vector_map.make_line(center.get_lanes(), line_type='CENTER')
        vector_map.make_crosswalk(crosswalks)
        vector_map.make_Stoplines(roads_processor.stoplines)
        error = vector_map.make_TrafficLight(static_objects_processor.TrfLight)
        if error == True :
            sys.exit()
        vector_map.merge_redundant_points()
        vector_map.rebuild_lane_conections()
        vector_map.export(VECTORMAP_FILES_FOLDER)
        # vector_map.plot()

else :
    vector_map = VectorMap()
    Files = [VECTORMAP_FILES_FOLDER+"point.csv",VECTORMAP_FILES_FOLDER+"lane.csv",VECTORMAP_FILES_FOLDER+"dtlane.csv"]
    vector_map.readfiles(Files)
    vector_map.merge_redundant_points()
    vector_map.rebuild_lane_conections()
    vector_map.plot()
