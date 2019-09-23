'''This file was created to see if parse.py ´s support of Speedlimit work. This Test file will use a simulation made with prescan with different RT and differente SL per RT.

.. author:: Nicolas Helleboid

'''
import numpy as np
import parse

# config
PEX_FILE_LOCATION1 = "C:\\Users\\Public\\Documents\\Experiments\\TestVM\\TestVM.pex"
PEX_FILE_LOCATION2 = "C:\\Users\\Public\\Documents\\Experiments\\Simulation\\Base_Map_S.pex"

roads = parse.get_roads(path=PEX_FILE_LOCATION1)
tfl = parse.get_staticalobject(path=PEX_FILE_LOCATION1)
print(tfl)
i=0
for id in roads:
    i += 1
    print("Road",i,"is a",roads[id].id, "with the following speedlimit :",roads[id].SpeedLimit)

j=0
for tl in tfl:
    j+=1
    print("Traffic Light",j,"is a",tfl[tl].id, "with the following coordinate x0: ",tfl[tl].x0,"y0:",tfl[tl].y0," and heading :",tfl[tl].h)
