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
        Vmax = s.get('MaxSpeed')    ###############
        if (type == 'BendRoad'):
            roads[id] = get_bend(s, id) ###############PLUS PROPRE METTRE DIRECT DANS LES FCT EN DESSOUS
        elif (type == 'BezierRoad'):
            roads[id] = get_curved(s, id) ###############
        elif (type == 'StraightRoad'):
            roads[id] = get_straight(s, id) ###############
        elif (type == 'Roundabout'):
            roads[id] = get_roundabout(s, id) ###############
        elif (type == 'XCrossing'):
            roads[id] = get_xcross(s, id)
        elif (type == 'EntryLaneRoad'):
            roads[id] = get_entry(s, id) ###############
        elif (type == 'ExitLaneRoad'):
            roads[id] = get_exit(s, id) ###############
        elif (type == 'LaneAdapterRoad'):
            roads[id] = get_adapter(s, id) ###############
    return roads

def get_bend(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')            ###############
    h = float(s[1].get('Heading')) * np.pi / 180
    rh = float(s.get('RelativeHeading')) * np.pi / 180
    clr = float(s.get('CenterlineRadius'))
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    lanes_in_x_dir = int(s.get('DirectionChangeAfterLane'))
    return BendRoad(id, x0, y0, h, rh, clr, lw, nbr_of_lanes, lanes_in_x_dir, Vmax, Vmax)  ###############

def get_curved(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')            ###############
    h = float(s[1].get('Heading')) * np.pi / 180
    rh = float(s.get('RelativeHeading')) * np.pi / 180
    cp1 = float(s.get('ControlPoint1Distance'))
    cp2 = float(s.get('ControlPoint2Distance'))
    dx = float(s.get('Xoffset'))
    dy = float(s.get('Yoffset'))
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    lanes_in_x_dir = int(s.get('DirectionChangeAfterLane'))
    return CurvedRoad(id, x0, y0, h, rh, cp1, cp2, dx, dy, lw, nbr_of_lanes, lanes_in_x_dir, Vmax, Vmax) ###############

def get_roundabout(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')            ###############
    h = float(s[1].get('Heading'))
    r = float(s.get('Radius'))
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    cs = s[18]
    chs = []
    for s in cs:
        chs.append((float(s.get('Heading')) + h) * np.pi / 180)
    return RoundaboutRoad(id, x0, y0, r, lw, chs, nbr_of_lanes, Vmax, Vmax)   ###############

def get_straight(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')            ###############
    h = float(s[1].get('Heading')) * np.pi / 180
    l = float(s.get('RoadLength'))
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    lanes_in_x_dir = int(s.get('DirectionChangeAfterLane'))
    return StraightRoad(id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, Vmax, Vmax) ###############

def get_entry(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')            ###############
    h = float(s[1].get('Heading')) * np.pi / 180
    l = float(s.get('RoadLength'))
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    lanes_in_x_dir = int(s.get('DirectionChangeAfterLane'))
    entry_road_angle=float(s.get('EntryRoadAngle')) * np.pi / 180
    apron_length=float(s.get('ApronLength'))
    side_road_length=float(s.get('SideRoadLength'))
    return EntryRoad(id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, entry_road_angle, apron_length, side_road_length, Vmax, Vmax) ###############

def get_exit(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')            ###############
    h = float(s[1].get('Heading')) * np.pi / 180
    l = float(s.get('RoadLength'))
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    lanes_in_x_dir = int(s.get('DirectionChangeAfterLane'))
    exit_road_angle=float(s.get('ExitRoadAngle')) * np.pi / 180
    apron_length=float(s.get('ApronLength'))
    side_road_length=float(s.get('SideRoadLength'))
    return ExitRoad(id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, exit_road_angle, apron_length, side_road_length, Vmax, Vmax) ###############

def get_adapter(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')            ###############
    h = float(s[1].get('Heading')) * np.pi / 180
    l = float(s.get('RoadLength'))
    lw = float(s.get('LaneWidthAtStart'))
    nbr_of_lanes_start = int(s.get('NumberOfLanesAtStart'))
    nbr_of_lanes_end = int(s.get('NumberOfLanesAtEnd'))
    lanes_in_x_dir_start = int(s.get('DirectionChangeAfterLane'))
    lanes_in_x_dir_end = int(s.get('DirectionChangeAfterLaneAtEnd'))
    return AdapterRoad(id, x0, y0, h, l, lw, nbr_of_lanes_start, nbr_of_lanes_end, lanes_in_x_dir_start, lanes_in_x_dir_end, Vmax, Vmax) ###############

def get_xcross(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    h = float(s[1].get('Heading')) * np.pi / 180
    cs = s[18]
    lw = float(cs[0].get('LaneWidth'))
    cs_h = []
    cs_len_till_stop = []
    cs_nbr_of_lanes = []
    cs_lanes_in_x_dir = []
    cs_l = []
    for c in cs:
        cs_h.append((float(c.get('Heading'))) * np.pi / 180)
        cs_len_till_stop.append(float(c.get('RoadLengthTillStopMarker')))
        cs_nbr_of_lanes.append(int(c.get('NumberOfLanes')))
        cs_lanes_in_x_dir.append(int(c.get('DirectionChangeAfterLane')))
        cs_l.append(float(c.get('RoadEndLength')))
    return XCrossRoad(id, x0, y0, h, lw, cs_h, cs_len_till_stop, cs_nbr_of_lanes, cs_lanes_in_x_dir, cs_l)
