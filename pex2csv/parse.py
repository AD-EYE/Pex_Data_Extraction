from lxml import etree
from road import *
import numpy as np

def get_roads(path='./data/roads.pex'):
    ns = {'xsi': "http://www.w3.org/2001/XMLSchema-instance"}
    tree = etree.parse(path)
    segments = tree.findall('//RoadSegment')
    roads = {}

    for s in segments:
        type = s.xpath('@xsi:type', namespaces = ns)[0]
        id = s.get('id')
        if (type == 'BendRoad'):
            roads[id] = get_bend(s, id)
        elif (type == 'BezierRoad'):
            roads[id] = get_curved(s, id)
        elif (type == 'StraightRoad'):
            roads[id] = get_straight(s, id)
        elif (type == 'Roundabout'):
            roads[id] = get_roundabout(s, id)
        elif (type == 'XCrossing'):
            roads[id] = get_xcross(s, id)
    return roads

def get_bend(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    h = float(s[1].get('Heading')) * np.pi / 180
    rh = float(s.get('RelativeHeading')) * np.pi / 180
    clr = float(s.get('CenterlineRadius'))
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    return BendRoad(id, x0, y0, h, rh, clr, lw, nbr_of_lanes)

def get_curved(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    h = float(s[1].get('Heading')) * np.pi / 180
    rh = float(s.get('RelativeHeading')) * np.pi / 180
    cp1 = float(s.get('ControlPoint1Distance'))
    cp2 = float(s.get('ControlPoint2Distance'))
    dx = float(s.get('Xoffset'))
    dy = float(s.get('Yoffset'))
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    return CurvedRoad(id, x0, y0, h, rh, cp1, cp2, dx, dy, lw, nbr_of_lanes)

def get_roundabout(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    h = float(s[1].get('Heading'))
    r = float(s.get('Radius'))
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    cs = s[18]
    chs = []
    for s in cs:
        chs.append((float(s.get('Heading')) + h) * np.pi / 180)
    return RoundaboutRoad(id, x0, y0, r, lw, chs, nbr_of_lanes)

def get_straight(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    h = float(s[1].get('Heading')) * np.pi / 180
    l = float(s.get('RoadLength'))
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    return StraightRoad(id, x0, y0, h, l, lw, nbr_of_lanes)

def get_xcross(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    h = float(s[1].get('Heading')) * np.pi / 180
    r = float(s.get('Radius'))
    cs = s[18]
    lw = float(cs[0].get('LaneWidth'))
    nbr_of_lanes = int(cs[0].get('NumberOfLanes'))
    len_till_stop = float(cs[0].get('RoadLengthTillStopMarker'))
    chs = []
    for c in cs:
        chs.append((float(c.get('Heading')) + h) * np.pi / 180)
    return XCrossRoad(id, x0, y0, h, r, lw, chs, len_till_stop, nbr_of_lanes)
