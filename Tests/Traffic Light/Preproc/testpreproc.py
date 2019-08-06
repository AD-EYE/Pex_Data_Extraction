'''This file was created to see if preproc.py ´s support of Traffic Ligh work. This Test file will use a simulation made with prescan with different RT with TrafficLight

.. author:: Nicolas Helleboid

'''
import numpy as np
import parse
from preproc import StaticalObjectProcessor

# config
PEX_FILE_LOCATION1 = "C:\\Users\\Public\\Documents\\Experiments\\TestVM\\TestVM.pex"
PEX_FILE_LOCATION2 = "C:\\Users\\Public\\Documents\\Experiments\\Simulation\\Base_Map_S.pex"

roads = parse.get_roads(path=PEX_FILE_LOCATION1)
statobj = parse.get_staticalobject(path=PEX_FILE_LOCATION2)
rproc = StaticalObjectProcessor()
rproc.add_staticalobject(statobj)
print(rproc.StatObjects["TrafficLightRoadSideNL_1"].x0)
rproc.create_statical_object()
print(rproc.TrfLight)


i=0
for id in roads:
    i += 1
    print("Road",i,"is a",roads[id].id, "with the following speedlimit :",roads[id].SpeedLimit)

j=0
for tl in rproc.TrfLight:
    j+=1
    print("Traffic Light",j,"is a",rproc.TrfLight[j-1].id, "with the following coordinate x0: ",rproc.TrfLight[j-1].x0,"y0:",rproc.TrfLight[j-1].y0)
    point = (rproc.TrfLight[j-1].x0 , rproc.TrfLight[j-1].y0)
    print("It was added to Rproc with the following coordinate :", point)
