from lxml import etree
import math
import csv
from BendRoad import BendRoad
from CurvedRoad import CurvedRoad
from StraightRoad import StraightRoad

csv_filepath = './csv/'
data_filepath = './data/'

def save_coords(coords, filename):
    with open(csv_filepath + filename, 'w', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for x in range(len(coords)):
            wr.writerow(coords[x])

def process_xml():

    ns = {'xsi': "http://www.w3.org/2001/XMLSchema-instance"}
    tree = etree.parse(data_filepath + 'roads.pex')
    bend_roads = []

    for segment in tree.findall('//RoadSegment[@xsi:type="BendRoad"]', ns):
        clr = float(segment.get('CenterlineRadius'))
        rh = float(segment.get('RelativeHeading'))
        rh_rad = rh * math.pi/180
        x = float(segment[0].get('X'))
        y = float(segment[0].get('Y'))
        broad = BendRoad(x, y, clr, rh_rad)
        coords = broad.get_coords()

        save_coords(coords, segment.get('id') + '.csv')

    for segment in tree.findall('//RoadSegment[@xsi:type="BezierRoad"]', ns):
        rh_rad = float(segment.get('RelativeHeading'))* math.pi/180
        cp1 = float(segment.get('ControlPoint1Distance'))
        cp2 = float(segment.get('ControlPoint2Distance'))
        h_rad = float(segment[1].get('Heading')) * math.pi/180
        x = float(segment[0].get('X'))
        y = float(segment[0].get('Y'))
        x_off = float(segment.get('Xoffset'))
        y_off = float(segment.get('Yoffset'))
        croad = CurvedRoad(x,y,rh_rad,cp1,cp2,h_rad, x_off, y_off)
        coords = croad.get_coords()
        save_coords(coords, segment.get('id') + '.csv')

    for segment in tree.findall('//RoadSegment[@xsi:type="StraightRoad"]', ns):
        length = float(segment.get('RoadLength'))
        x = float(segment[0].get('X'))
        y = float(segment[0].get('Y'))
        h_rad = float(segment[1].get('Heading')) * math.pi/180

        sroad = StraightRoad(x, y, h_rad, length)
        coords = sroad.get_coords()
        save_coords(coords, segment.get('id') + '.csv')

def main():
    process_xml()

if __name__ == '__main__':
    main()
