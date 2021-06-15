##This file was created to see if parse.py ´s support of Speedlimit work. This Test file will use a simulation made with prescan with different RT and differente SL per RT.
##author:: Nicolas Helleboid

import numpy as np
import parse
import matplotlib.pyplot as plt

# config
PEX_FILE_LOCATION1 = "C:\\Users\\Public\\Documents\\Experiments\\TestVM\\TestVM.pex"
PEX_FILE_LOCATION2 = "C:\\Users\\Public\\Documents\\Experiments\\Simulation\\Base_Map_S.pex"



roads = parse.get_roads(path=PEX_FILE_LOCATION1)
i=0
e1=[]
e2=[]
for id in roads:
    i += 1
    print("Road",i,"is a",roads[id].id)
    for x, y in roads[id].e1[0]:
        e1.append((x,y))
    for i in range(len(roads[id].e2)):
        for x, y in roads[id].e2[i]:
            e2.append((x,y))
x1=[]
y1=[]
for i in range(len(e2)):
    x1.append(e2[i][0])
    y1.append(e2[i][1])

x2=[]
y2=[]
for i in range(len(e1)):
    x2.append(e1[i][0])
    y2.append(e1[i][1])


print(len(e1))
print(len(e2))
print()
print(e1,"edge 1")
print(e2,"edge 2")
plt.plot(x1,y1)
plt.plot(x2,y2)
plt.show()

