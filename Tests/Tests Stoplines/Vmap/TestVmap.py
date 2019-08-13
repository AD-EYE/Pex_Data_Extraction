'''This file was created to see if preproc ´s support of Speedlimit work. This Test file will use a simulation made with prescan with different RT and differente SL per RT.

.. author:: Nicolas Helleboid

'''

from preproc import RoadProcessor
from vmap import VectorMap
import numpy as np
import parse

# config
PEX_FILE_LOCATION1 = "C:\\Users\\Public\\Documents\\Experiments\\TestVM\\TestVM.pex"
PEX_FILE_LOCATION2 = "C:\\Users\\Public\\Documents\\Experiments\\Simulation\\Base_Map_S.pex"

roads = parse.get_roads(path=PEX_FILE_LOCATION2)
rproc = RoadProcessor()
rproc.add_roads(roads)
rproc.create_lanes()
vm = VectorMap()


for lane in rproc.lanes:
    #print(lane.SpeedLimit)
    vm.make_lane(lane.SpeedLimit, lane.RefSpeed, lane.get_lanes(), junction_end=lane.get_junction_end(), junction_start=lane.get_junction_start())


print(vm.lane[1].get_LimitVel())
vm.lane[4].set_LimitVel(400)
print(vm.lane[4].get_LimitVel())
