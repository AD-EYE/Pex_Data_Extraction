from lxml import etree
from road import *
import numpy as np

def get_roads(path='./data/roads.pex'):
    ns = {'xsi': "http://www.w3.org/2001/XMLSchema-instance"}
    tree = etree.parse(path)
    segments = tree.findall('//RoadSegment', ns)
    roads = {}

    for s in segments:
        type = s.xpath('@xsi:type', namespaces = ns)[0]
        if (type == 'BendRoad'):
            roads[s.get('id')] = get_bend(s)
        elif (type == 'BezierRoad'):
            roads[s.get('id')] = get_curved(s)
        elif (type == 'StraightRoad'):
            roads[s.get('id')] = get_straight(s)
        elif (type == 'Roundabout'):
            roads[s.get('id')] = get_roundabout(s)

    return roads

def get_bend(s):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    h = float(s[1].get('Heading')) * np.pi / 180
    rh = float(s.get('RelativeHeading')) * np.pi / 180
    clr = float(s.get('CenterlineRadius'))
    return BendRoad(x0, y0, h, rh, clr)

def get_curved(s):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    h = float(s[1].get('Heading')) * np.pi / 180
    rh = float(s.get('RelativeHeading')) * np.pi / 180
    cp1 = float(s.get('ControlPoint1Distance'))
    cp2 = float(s.get('ControlPoint2Distance'))
    dx = float(s.get('Xoffset'))
    dy = float(s.get('Yoffset'))
    return CurvedRoad(x0, y0, h, rh, cp1, cp2, dx, dy)

def get_roundabout(s):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    r = float(s.get('Radius'))
    return RoundaboutRoad(x0, y0, r)

def get_straight(s):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    h = float(s[1].get('Heading')) * np.pi / 180
    l = float(s.get('RoadLength'))
    return StraightRoad(x0, y0, h, l)
