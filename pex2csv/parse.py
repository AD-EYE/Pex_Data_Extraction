'''This module contains all of the code that parse the simulation.
It will extract roads from the simulation in order to convert those road into the VectorMapping format(done in Vmap.py)

'''


from lxml import etree
from road import *
from staticalobject import *
import numpy as np

def get_staticalobject(path='./data/roads.pex'):
    '''
    This fonction go fetch the list of traffic Light that make up the simulation in the pex file.
    To do so, the fonction search in the  part of the pex files, and then use the id
    of each  to add them to a list of  using the get_X function define in this module.

    :param path: A path use to point to the pex file
    :type path: String

    '''

    # eTree module fetch the Roads in the Pex file
    ns = {'xsi': "http://www.w3.org/2001/XMLSchema-instance"}
    tree = etree.parse(path)
    staticalobject_In_Simu = tree.findall('//InfraOther')
    staticalobject = {}

    # For each Traffic Light in the simulation we produce a corresponding TrafficLight in the TrafLight list

    for t in staticalobject_In_Simu:
        type = t.xpath('@xsi:type', namespaces = ns)[0]
        id = t.get('id')
        if (type == 'TrafficLightRoadSideNL'):
            staticalobject[id] = get_TLight(t, id)
    return staticalobject


def get_roads(path='./data/roads.pex'):
    '''
    This fonction go fetch the list of road that make up the simulation in the pex file.
    To do so, the fonction search in the RoadSegment part of the pex files, and then use the id
    of each roads to add them to a list of Roads using the get_X function define in this module.

    :param path: A path use to point to the pex file
    :type path: String

    '''

    # eTree module fetch the Roads in the Pex file
    ns = {'xsi': "http://www.w3.org/2001/XMLSchema-instance"}
    tree = etree.parse(path)
    segments = tree.findall('//RoadSegment')
    connections = tree.findall('//Connection')
    roads = {}

    # For each Road Segment in the simulation produce a road type in the road list

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
            roads[id] = get_roundabout(s, id, connections, path)
        elif (type == 'XCrossing'):
            roads[id] = get_xcross(s, id)
        elif (type == 'EntryLaneRoad'):
            roads[id] = get_entry(s, id)
        elif (type == 'ExitLaneRoad'):
            roads[id] = get_exit(s, id)
        elif (type == 'LaneAdapterRoad'):
            roads[id] = get_adapter(s, id)
        elif (type == 'YCrossing'):
            roads[id] = get_ycross(s, id)
    return roads

    # The following fonctions are called by get_staticalobject and return the statical object with the right parameters define in staticalobject.py corresponding to the statical object id in the input. #

def get_TLight(t, id):
    x0 = float(t[0].get('X'))
    y0 = float(t[0].get('Y'))
    h = float(t[1].get('Heading')) * np.pi / 180
    s = 1
    return TrafficLight(id, x0, y0, h, s)



    # The following fonctions are called by get_roads and return the road type with the right parameters define in Road.py corresponding to the road id in the input. #

def get_bend(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')
    h = float(s[1].get('Heading')) * np.pi / 180
    rh = float(s.get('RelativeHeading')) * np.pi / 180
    clr = float(s.get('CenterlineRadius'))
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    lanes_in_x_dir = int(s.get('DirectionChangeAfterLane'))
    RoadMarking = s[16]
    Stl = []
    for R in RoadMarking:
        if "BitmapRoadMarker" in str(R.get('id')) :
            hStop = float(R[1].get('Heading'))* np.pi / 180
            x1 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 - (lw/2) * np.sin(hStop+h)
            y1 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0 + (lw/2)*np.cos(hStop+h)
            x2 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 + (lw/2) * np.sin(hStop+h)
            y2 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0  - (lw/2) * np.cos(hStop+h)
            x3 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0
            y3 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0
            Stl.append((x1, y1, x2, y2, x3, y3))
    return BendRoad(id, x0, y0, h, rh, clr, lw, nbr_of_lanes, lanes_in_x_dir, Vmax, Vmax, Stl)

def get_curved(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')
    h = float(s[1].get('Heading')) * np.pi / 180
    rh = float(s.get('RelativeHeading')) * np.pi / 180
    cp1 = float(s.get('ControlPoint1Distance'))
    cp2 = float(s.get('ControlPoint2Distance'))
    dx = float(s.get('Xoffset'))
    dy = float(s.get('Yoffset'))
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    lanes_in_x_dir = int(s.get('DirectionChangeAfterLane'))
    RoadMarking = s[16]
    Stl = []
    for R in RoadMarking:
        if "BitmapRoadMarker" in str(R.get('id')) :
            hStop = float(R[1].get('Heading'))* np.pi / 180
            x1 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 - (lw/2) * np.sin(hStop+h)
            y1 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0 + (lw/2)*np.cos(hStop+h)
            x2 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 + (lw/2) * np.sin(hStop+h)
            y2 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0  - (lw/2) * np.cos(hStop+h)
            x3 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0
            y3 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0
            Stl.append((x1, y1, x2, y2, x3, y3))
            print(Stl)
    return CurvedRoad(id, x0, y0, h, rh, cp1, cp2, dx, dy, lw, nbr_of_lanes, lanes_in_x_dir, Vmax, Vmax, Stl)

def get_roundabout(s, id, connections, path):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')
    h = float(s[1].get('Heading'))
    r = float(s.get('Radius'))
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    cs = s[18]
    cs_h = []
    cs_filletradius = []
    cs_nb_of_lanes = []
    cs_nb_of_lane_x_direction = []
    for s in cs:
        cs_h.append((float(s.get('Heading')) + h) * np.pi / 180)
        cs_filletradius.append((float(s.get('FilletRadiusPercentage'))))
        cs_nb_of_lanes.append((int(s.get('NumberOfLanes'))))
        cs_nb_of_lane_x_direction.append((int(s.get('DirectionChangeAfterLane'))))

    TabConnect = [0,0,0,0]
    for connection in connections:
        idA = connection.get('Road_A_UniqueId')
        idB = connection.get('Road_B_UniqueId')
        if (id in idA):

            TabConnect[int(connection.get('Joint_A_Id'))] = idB
        elif (id in idB):

            TabConnect[int(connection.get('Joint_B_Id'))] = idA
    Tabpointcon = []
    for i in range(len(TabConnect)):
        Tabpointcon.append(get_links_points_roundabout(TabConnect[i],path))

    return RoundaboutRoad(id, x0, y0, r, lw, cs_h, cs_filletradius, cs_nb_of_lanes, cs_nb_of_lane_x_direction, nbr_of_lanes, Vmax, Vmax, Tabpointcon)

def get_straight(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')
    h = float(s[1].get('Heading')) * np.pi / 180
    l = float(s.get('RoadLength'))
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    lanes_in_x_dir = int(s.get('DirectionChangeAfterLane'))
    RoadMarking = s[16]

    Stl = []
    for R in RoadMarking:
        if "BitmapRoadMarker" in str(R.get('id')) :
            x1 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 - (lw/2) * np.sin(h)
            y1 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0 + (lw/2) * np.cos(h)
            x2 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 + (lw*0.5) * np.sin(h)
            y2 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0  - (lw*0.5) * np.cos(h)
            x3 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0
            y3 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0
            Stl.append((x1, y1, x2, y2, x3, y3,nbr_of_lanes-lanes_in_x_dir))
    return StraightRoad(id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, Vmax, Vmax, Stl)

def get_entry(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')
    h = float(s[1].get('Heading')) * np.pi / 180
    l = float(s.get('RoadLength'))
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    lanes_in_x_dir = int(s.get('DirectionChangeAfterLane'))
    entry_road_angle=float(s.get('EntryRoadAngle')) * np.pi / 180
    apron_length=float(s.get('ApronLength'))
    side_road_length=float(s.get('SideRoadLength'))
    RoadMarking = s[16]
    Stl = []
    for R in RoadMarking:
        if "BitmapRoadMarker" in str(R.get('id')) :
            x1 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 - (lw/2) * np.sin(h)
            y1 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0 + (lw/2) * np.cos(h)
            x2 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 + (lw*0.5) * np.sin(h)
            y2 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0  - (lw*0.5) * np.cos(h)
            x3 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0
            y3 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0
            Stl.append((x1, y1, x2, y2, x3, y3))
    return EntryRoad(id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, entry_road_angle, apron_length, side_road_length, Vmax, Vmax, Stl)

def get_exit(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')
    h = float(s[1].get('Heading')) * np.pi / 180
    l = float(s.get('RoadLength'))
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    lanes_in_x_dir = int(s.get('DirectionChangeAfterLane'))
    exit_road_angle=float(s.get('ExitRoadAngle')) * np.pi / 180
    apron_length=float(s.get('ApronLength'))
    side_road_length=float(s.get('SideRoadLength'))
    RoadMarking = s[16]
    Stl = []
    for R in RoadMarking:
        if "BitmapRoadMarker" in str(R.get('id')) :

            x1 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 - (lw/2) * np.sin(h)
            y1 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0 + (lw/2) * np.cos(h)
            x2 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 + (lw*0.5) * np.sin(h)
            y2 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0  - (lw*0.5) * np.cos(h)
            x3 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0
            y3 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0
            Stl.append((x1, y1, x2, y2, x3, y3))
    return ExitRoad(id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, exit_road_angle, apron_length, side_road_length, Vmax, Vmax, Stl)

def get_adapter(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')
    h = float(s[1].get('Heading')) * np.pi / 180
    l = float(s.get('RoadLength'))
    lw = float(s.get('LaneWidthAtStart'))
    nbr_of_lanes_start = int(s.get('NumberOfLanesAtStart'))
    nbr_of_lanes_end = int(s.get('NumberOfLanesAtEnd'))
    lanes_in_x_dir_start = int(s.get('DirectionChangeAfterLane'))
    lanes_in_x_dir_end = int(s.get('DirectionChangeAfterLaneAtEnd'))
    RoadMarking = s[16]
    Stl = []
    for R in RoadMarking:
            x1 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 - (lw/2) * np.sin(h)
            y1 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0 + (lw/2) * np.cos(h)
            x2 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 + (lw*0.5) * np.sin(h)
            y2 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0  - (lw*0.5) * np.cos(h)
            x3 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0
            y3 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0
            Stl.append((x1, y1, x2, y2, x3, y3))
    return AdapterRoad(id, x0, y0, h, l, lw, nbr_of_lanes_start, nbr_of_lanes_end, lanes_in_x_dir_start, lanes_in_x_dir_end, Vmax, Vmax, Stl)

def get_xcross(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')
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
    Stl = []
    for i in range(4):
        x1 = -lw*(cs_nbr_of_lanes[i]/2)*np.sin(h+cs_h[i]) + (cs_l[i]-cs_len_till_stop[i])*np.cos(h+cs_h[i])  + x0
        y1 = lw*(cs_nbr_of_lanes[i]/2)*np.cos(h+cs_h[i]) + (cs_l[i]-cs_len_till_stop[i])*np.sin(h+cs_h[i]) +y0
        x2 = lw*((cs_nbr_of_lanes[i]/2)-cs_lanes_in_x_dir[i])*np.sin(h+cs_h[i]) + (cs_l[i]-cs_len_till_stop[i])*np.cos(h+cs_h[i])  + x0
        y2 = -lw*((cs_nbr_of_lanes[i]/2)-cs_lanes_in_x_dir[i])*np.cos(h+cs_h[i]) + (cs_l[i]-cs_len_till_stop[i])*np.sin(h+cs_h[i]) +y0
        x3 = (x1+x2)/2
        y3 = (y1+y2)/2
        Stl.append((x1, y1, x2, y2, x3, y3,cs_nbr_of_lanes[i]-cs_lanes_in_x_dir[i]))

    return XCrossRoad(id, x0, y0, h, lw, cs_h, cs_len_till_stop, cs_nbr_of_lanes, cs_lanes_in_x_dir, cs_l, Vmax, Vmax, Stl)

def get_ycross(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')
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

    Stl = []
    for i in range(3):
        cs_l[i]-cs_len_till_stop[i]
        x1 = -lw*(cs_nbr_of_lanes[i]/2)*np.sin(h+cs_h[i]) + (cs_l[i]-cs_len_till_stop[i])*np.cos(h+cs_h[i])  + x0
        y1 = lw*(cs_nbr_of_lanes[i]/2)*np.cos(h+cs_h[i]) + (cs_l[i]-cs_len_till_stop[i])*np.sin(h+cs_h[i]) +y0
        x2 = lw*((cs_nbr_of_lanes[i]/2)-cs_lanes_in_x_dir[i])*np.sin(h+cs_h[i]) + (cs_l[i]-cs_len_till_stop[i])*np.cos(h+cs_h[i])  + x0
        y2 = -lw*((cs_nbr_of_lanes[i]/2)-cs_lanes_in_x_dir[i])*np.cos(h+cs_h[i]) + (cs_l[i]-cs_len_till_stop[i])*np.sin(h+cs_h[i]) +y0
        x3 = (x1+x2)/2
        y3 = (y1+y2)/2
        Stl.append((x1, y1, x2, y2, x3, y3,cs_nbr_of_lanes[i]-cs_lanes_in_x_dir[i]))

    return YCrossRoad(id, x0, y0, h, lw, cs_h, cs_len_till_stop, cs_nbr_of_lanes, cs_lanes_in_x_dir, cs_l, Vmax, Vmax, Stl)



# The following fonction is usefull to get the linking point of roundabout #

def get_links_points_roundabout(id,path):
    '''
    This function go and take the orign point of the road connected to the crosssection of the roundabout

    '''

    # eTree module fetch the Roads in the Pex file
    ns = {'xsi': "http://www.w3.org/2001/XMLSchema-instance"}
    tree = etree.parse(path)
    segments = tree.findall('//RoadSegment')
    point = []



    for s in segments:
        type = s.xpath('@xsi:type', namespaces = ns)[0]
        idseg = s.get('id')
        if (idseg == id):
            x0 = float(s[0].get('X'))
            y0 = float(s[0].get('Y'))
            point.append((x0,y0))
            break


    return point

# Support for multi lane stop line and tfl : 
#