'''This file was created to see if preproc ´s support of Speedlimit work. This Test file will use a simulation made with prescan with different RT and differente SL per RT.

.. author:: Nicolas Helleboid

'''

import numpy as np
import parse
from preproc import RoadProcessor

# config
PEX_FILE_LOCATION1 = "C:\\Users\\Public\\Documents\\Experiments\\TestVM\\TestVM.pex"
PEX_FILE_LOCATION2 = "C:\\Users\\Public\\Documents\\Experiments\\Simulation\\Base_Map_S.pex"

roads = parse.get_roads(path=PEX_FILE_LOCATION2)

#
# for id in roads:
#     for (x,y) in roads[id].l[1]:
#         print((x,y))
#     print()
#     print()

rproc = RoadProcessor()
rproc.add_roads(roads)
rproc.create_lanes()
i=1

for lanes in rproc.lanes:
    print("Lane",i)
    print(lanes.lanes)
    print("Lane",i,"has the following SL :",lanes.SpeedLimit)
    i += 1