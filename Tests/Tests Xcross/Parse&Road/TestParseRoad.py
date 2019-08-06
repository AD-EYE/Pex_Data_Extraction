'''This file was created to see if parse.py ´s support of Xcrossing work. This Test file will use a simulation made with prescan with different RT and differente SL per RT.

.. author:: Nicolas Helleboid

'''
import numpy as np
import parse
from preproc import RoadProcessor
from vmap import VectorMap


# config
PEX_FILE_LOCATION1 = "C:\\Users\\Public\\Documents\\Experiments\\TestVM\\TestVM.pex"
PEX_FILE_LOCATION2 = "C:\\Users\\Public\\Documents\\Experiments\\Simulation\\Base_Map_S.pex"

roads = parse.get_roads(path=PEX_FILE_LOCATION1)

rproc = RoadProcessor()
rproc.add_roads(roads)
rproc.create_lanes()
vm = VectorMap()
for lane in rproc.lanes:
    vm.make_lane(lane.SpeedLimit, lane.RefSpeed, lane.get_lanes(), junction_end=lane.get_junction_end(), junction_start=lane.get_junction_start())
i=0
# for id in roads:
#     i += 1
#     print(roads[id].l)

vm.export()
vm.plot()
