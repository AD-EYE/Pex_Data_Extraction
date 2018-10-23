from road import BendRoad, CurvedRoad
from matplotlib import pyplot as plt
from lxml import etree
import csv, math

csv_filepath = './csv/'
data_filepath = './data/'

def save_coords(coords, filename):
    with open(csv_filepath + filename, 'w', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for x in range(len(coords)):
            wr.writerow(coords[x])

if __name__ == '__main__':

    ns = {'xsi': "http://www.w3.org/2001/XMLSchema-instance"}
    tree = etree.parse(data_filepath + 'roads.pex')
    roads = {}

    for segment in tree.findall('//RoadSegment[@xsi:type="BendRoad"]', ns):
        clr = float(segment.get('CenterlineRadius'))
        rh = float(segment.get('RelativeHeading')) * math.pi / 180
        x0 = float(segment[0].get('X'))
        y0 = float(segment[0].get('Y'))
        # roads[segment.get('id')] = BendRoad(x0, y0, clr, rh)

    for segment in tree.findall('//RoadSegment[@xsi:type="BezierRoad"]', ns):
        rh = float(segment.get('RelativeHeading')) * math.pi/180
        cp1 = float(segment.get('ControlPoint1Distance'))
        cp2 = float(segment.get('ControlPoint2Distance'))
        h = float(segment[1].get('Heading')) * math.pi / 180
        x0 = float(segment[0].get('X'))
        y0 = float(segment[0].get('Y'))
        dx = float(segment.get('Xoffset'))
        dy = float(segment.get('Yoffset'))
        roads[segment.get('id')] = CurvedRoad(x0, y0, rh, cp1, cp2, h, dx, dy)

    xs = []
    ys = []
    for id in roads.keys():
        for (x, y) in roads[id].center:
            xs.append(x)
            ys.append(y)
    plt.plot(xs, ys, '.')
    plt.grid(True)
    plt.show()
