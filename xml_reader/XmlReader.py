from lxml import etree
import math
import csv
from BendRoad import BendRoad
from CurvedRoad import CurvedRoad
from StraightRoad import StraightRoad

csv_filepath = './csv/'
data_filepath = './data/'

class XmlReader(object):
    def save_coords(self, coords, filename):
        with open(csv_filepath + filename, 'w', newline='') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            for x in range(len(coords)):
                wr.writerow(coords[x])

    def process_xml(self):

        ns = {'xsi': "http://www.w3.org/2001/XMLSchema-instance"}
        tree = etree.parse(data_filepath + 'roads.pex')
        broads = []
        croads = []
        sroads = []

        roads = tree.findall('//RoadSegment', ns)

        for road in roads:
            roadtype = road.xpath('@xsi:type', namespaces = ns)[0]
            if(roadtype == 'BendRoad'):
                self.process_bend_road(road)
            elif(roadtype == 'BezierRoad'):
                self.process_bezier_road(road)
            elif(roadtype == 'StraightRoad'):
                self.process_straight_road(road)

    def process_bend_road(self, road):
        clr = float(road.get('CenterlineRadius'))
        rh = float(road.get('RelativeHeading'))
        rh_rad = rh * math.pi/180
        x = float(road[0].get('X'))
        y = float(road[0].get('Y'))
        broad = BendRoad(x, y, clr, rh_rad)
        coords = broad.get_coords()

        self.save_coords(coords, road.get('id') + '.csv')

    def process_bezier_road(self, road):
        rh_rad = float(road.get('RelativeHeading'))* math.pi/180
        cp1 = float(road.get('ControlPoint1Distance'))
        cp2 = float(road.get('ControlPoint2Distance'))
        h_rad = float(road[1].get('Heading')) * math.pi/180
        x = float(road[0].get('X'))
        y = float(road[0].get('Y'))
        x_off = float(road.get('Xoffset'))
        y_off = float(road.get('Yoffset'))
        croad = CurvedRoad(x, y, rh_rad, cp1, cp2, h_rad, x_off, y_off)
        coords = croad.get_coords()
        self.save_coords(coords, road.get('id') + '.csv')

    def process_straight_road(self, road):
        length = float(road.get('RoadLength'))
        x = float(road[0].get('X'))
        y = float(road[0].get('Y'))
        h_rad = float(road[1].get('Heading')) * math.pi/180
        sroad = StraightRoad(x, y, h_rad, length)
        coords = sroad.get_coords()
        self.save_coords(coords, road.get('id') + '.csv')
