from utils import *

liste1 = []
liste2 = []

for i in range(10):
    liste1.append((9-i,(9-i)+1))
    liste2.append((9-i,(-2*(9-i)+4)))

(x1,y1) = Intersection_Lines(liste2, liste1)
print( (x1,y1) )