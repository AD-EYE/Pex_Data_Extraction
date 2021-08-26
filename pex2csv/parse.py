'''This module contains all of the code that parse the simulation.
It will extract roads from the simulation in order to convert those road into
the VectorMapping format(done in Vmap.py)

'''


import numpy as np
from lxml import etree

from road import *
from staticobject import *


def get_staticobject(path='./data/roads.pex'):
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
    staticobject_In_Simu = tree.findall('//Actor')
    staticobject = {}

    # For each Traffic Light in the simulation we produce a corresponding TrafficLight in the TrafLight list

    for t in staticobject_In_Simu:
        description = t.get('Description')

        id = t.get('id')
        if ('Roadside' in description):
            staticobject[id] = get_TLight(t, id)
    return staticobject


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
        elif (type == 'CubicSplineRoad'):
            roads.update(get_flex(s, id))
        elif (type == 'PedestrianCrossing'):
            roads[id] = get_crosswalk(s, id)
        elif (type == 'ClothoidRoad'):
            roads[id] = get_clothoid(s, id, connections, path)
    return roads

    # The following fonctions are called by get_staticobject and return the static object with the right parameters define in staticobject.py corresponding to the static object id in the input. #

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
    cw = []
    for R in RoadMarking:
        if "BitmapRoadMarker" in str(R.get('id')) :
            hStop = float(R[1].get('Heading'))* np.pi / 180
            x1 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 - (lw/2) * np.sin(hStop+h)
            y1 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0 + (lw/2)*np.cos(hStop+h)
            x2 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 + (lw/2) * np.sin(hStop+h)
            y2 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0  - (lw/2) * np.cos(hStop+h)
            x3 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0
            y3 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0
            Stl.append((x1, y1, x2, y2, x3, y3,nbr_of_lanes-lanes_in_x_dir,lw))
        if "PedestrianMarkingGeneric" in str(R.get('id')) :
            hw = float(R[1].get('Heading'))*np.pi/180
            cl = float(R.get('CrossingLength'))
            cwh = float(R.get('CrossingWidth'))
            xl = float(R[0].get('X'))
            yl = float(R[0].get('Y'))
            x1 = x0 + (xl - (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y1 = y0 + (xl - (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            x2 = x0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.cos(h) - (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.sin(h)
            y2 = y0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.sin(h) + (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.cos(h)
            x3 = x0 + (xl + (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y3 = y0 + (xl + (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            cw.append([x1,y1,x2,y2,x3,y3])
    return BendRoad(id, x0, y0, h, rh, clr, lw, nbr_of_lanes, lanes_in_x_dir, Vmax, Vmax, Stl, cw)

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
    cw = []
    for R in RoadMarking:
        if "BitmapRoadMarker" in str(R.get('id')) :
            hStop = float(R[1].get('Heading'))* np.pi / 180
            x1 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 - (lw/2) * np.sin(hStop+h)
            y1 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0 + (lw/2)*np.cos(hStop+h)
            x2 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 + (lw/2) * np.sin(hStop+h)
            y2 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0  - (lw/2) * np.cos(hStop+h)
            x3 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0
            y3 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0
            Stl.append((x1, y1, x2, y2, x3, y3,nbr_of_lanes-lanes_in_x_dir,lw))
        if "PedestrianMarkingGeneric" in str(R.get('id')) :
            hw = float(R[1].get('Heading'))*np.pi/180
            cl = float(R.get('CrossingLength'))
            cwh = float(R.get('CrossingWidth'))
            xl = float(R[0].get('X'))
            yl = float(R[0].get('Y'))
            x1 = x0 + (xl - (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y1 = y0 + (xl - (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            x2 = x0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.cos(h) - (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.sin(h)
            y2 = y0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.sin(h) + (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.cos(h)
            x3 = x0 + (xl + (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y3 = y0 + (xl + (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            cw.append([x1,y1,x2,y2,x3,y3])
    return CurvedRoad(id, x0, y0, h, rh, cp1, cp2, dx, dy, lw, nbr_of_lanes, lanes_in_x_dir, Vmax, Vmax, Stl, cw)

def get_clothoid(s, id, connections, path):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')
    h = float(s[1].get('Heading')) * np.pi / 180
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    lanes_in_x_dir = int(s.get('DirectionChangeAfterLane'))
    RoadMarking = s[16]
    Stl = []
    cw = []
    ClothoidSection = s[20]

    C2 = float(ClothoidSection[0].get('R')) * float(ClothoidSection[0].get('L'))
    if ClothoidSection.get('R0') == 'INF' :
        Lstart = 0
    else :
        Lstart = C2 / float(ClothoidSection.get('R0'))
    if ClothoidSection.get('R1') == 'INF' :
        Lend = 0
    else :
        Lend = C2 / float(ClothoidSection.get('R1'))
    if ClothoidSection[0].get('FlippedCurve') == 'false' :
        flipped = False
    else :
        flipped = True

    for R in RoadMarking:
        if "BitmapRoadMarker" in str(R.get('id')) :
            hStop = float(R[1].get('Heading'))* np.pi / 180
            x1 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 - (lw/2) * np.sin(hStop+h)
            y1 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0 + (lw/2)*np.cos(hStop+h)
            x2 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 + (lw/2) * np.sin(hStop+h)
            y2 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0  - (lw/2) * np.cos(hStop+h)
            x3 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0
            y3 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0
            Stl.append((x1, y1, x2, y2, x3, y3,nbr_of_lanes-lanes_in_x_dir,lw))
        if "PedestrianMarkingGeneric" in str(R.get('id')) :
            hw = float(R[1].get('Heading'))*np.pi/180
            cl = float(R.get('CrossingLength'))
            cwh = float(R.get('CrossingWidth'))
            xl = float(R[0].get('X'))
            yl = float(R[0].get('Y'))
            x1 = x0 + (xl - (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y1 = y0 + (xl - (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            x2 = x0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.cos(h) - (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.sin(h)
            y2 = y0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.sin(h) + (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.cos(h)
            x3 = x0 + (xl + (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y3 = y0 + (xl + (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            cw.append([x1,y1,x2,y2,x3,y3])

    TabConnect = [0,0]
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

    return ClothoidRoads(id, x0, y0, h, C2, Lstart, Lend, flipped, lw, nbr_of_lanes, lanes_in_x_dir, Tabpointcon, Vmax, Vmax, cw, Stl)

def get_flex(s, id): # a flex road is created with several curved roads
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
    Lid = []
    Lx = []
    Ly = []
    LBt = []
    LFt = []
    Lh = []
    cw = []
    for R in RoadMarking:
        if "BitmapRoadMarker" in str(R.get('id')) :
            hStop = float(R[1].get('Heading'))* np.pi / 180
            x1 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 - (lw/2) * np.sin(hStop+h)
            y1 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0 + (lw/2)*np.cos(hStop+h)
            x2 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 + (lw/2) * np.sin(hStop+h)
            y2 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0  - (lw/2) * np.cos(hStop+h)
            x3 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0
            y3 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0
            Stl.append((x1, y1, x2, y2, x3, y3,nbr_of_lanes-lanes_in_x_dir,lw))
        if "PedestrianMarkingGeneric" in str(R.get('id')) :
            hw = float(R[1].get('Heading'))*np.pi/180
            cl = float(R.get('CrossingLength'))
            cwh = float(R.get('CrossingWidth'))
            xl = float(R[0].get('X'))
            yl = float(R[0].get('Y'))
            x1 = x0 + (xl - (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y1 = y0 + (xl - (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            x2 = x0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.cos(h) - (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.sin(h)
            y2 = y0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.sin(h) + (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.cos(h)
            x3 = x0 + (xl + (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y3 = y0 + (xl + (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            cw.append([x1,y1,x2,y2,x3,y3])


    Lid.append(id)
    Lx.append(0)
    Ly.append(0)
    LBt.append(0)
    LFt.append(cp1)
    Lh.append(0)
    i = 0
    CrossSections = s[20] #.findall('//RoadCrossSection')
    ns = {'xsi': "http://www.w3.org/2001/XMLSchema-instance"}
    for c in CrossSections: # here we find each curve of the flexible road (to create several flexible roads)
        type = c.xpath('@xsi:type', namespaces=ns)[0]
        if type == 'CubicSplineCrossSection':
            i = i + 1
            Lid.append(c.get('id'))
            Lx.append(float(c[0].get('X')))
            Ly.append(float(c[0].get('Y')))
            LBt.append(float(c.get('EntryTension')))
            LFt.append(float(c.get('ExitTension')))
            Lh.append(float(c[1].get('Heading')) * np.pi / 180)

    Lid.append(0)
    Lx.append(dx)
    Ly.append(dy)
    LBt.append(cp2)
    LFt.append(cp1)
    Lh.append(rh)

    CurvedRoads = {}
    X = []
    Y = []
    cwj = []
    Stlj = []
    for j in range (i+1): # here we detect on which curved roads are the crosswalks and the stoplines
        cwj_local  = []
        Stlj_local = []
        (xCR,yCR) = (x0 + Lx[j] * np.cos(h) - Ly[j] * np.sin(h), y0 + Lx[j] * np.sin(h) + Ly[j] * np.cos(h))
        X.append(xCR)
        Y.append(yCR)
        cp1j = LFt[j]
        cp2j = LBt[j+1]
        if j>0 :
            hj = Lh[j] + h
            rhj = Lh[j + 1] - Lh[j]
            (p1x,p1y) = (X[j-1] + cp1j*np.cos(hj),Y[j-1] - cp1j*np.sin(hj))
            (p2x,p2y) = (X[j] + cp2j*np.cos(hj + rhj),Y[j] - cp2*np.sin(hj+rhj))
            k=0
            while k < (len(cw)):
                xc = (cw[k][2]+cw[k][4])/2
                yc = (cw[k][3]+cw[k][5])/2
                if ( min(X[j-1],X[j],p1x,p2x) <= xc < max(X[j-1],X[j],p1x,p2x) ) and ( min(Y[j-1],Y[j],p1y,p2y) <= yc < max(Y[j-1],Y[j],p1y,p2y) ) :
                    cwj_local.append(cw.pop(k))
                else : k+=1
            k=0
            while k < (len(Stl)):
                if ( min(X[j-1],X[j],p1x,p2x) <= Stl[k][4] < max(X[j-1],X[j],p1x,p2x) ) and ( min(Y[j-1],Y[j],p1y,p2y) <= Stl[k][5] < max(Y[j-1],Y[j],p1y,p2y) ) :
                    Stlj_local.append(Stl.pop(k))
                else : k+=1

            cwj.append(cwj_local)
            Stlj.append(Stlj_local)
    k=0
    cwj_local  = []
    Stlj_local = []
    while k < (len(cw)):
        cwj_local.append(cw.pop(k))
    while k < (len(Stl)):
        Stlj_local.append(Stl.pop(k))
    cwj.append(cwj_local)
    Stlj.append(Stlj_local)


    for j in range(i+1): # Now we create the curved roads

        NewCurvedRoad = CurvedRoad(Lid[j],
                                   x0 + Lx[j] * np.cos(h) - Ly[j] * np.sin(h),
                                   y0 + Lx[j] * np.sin(h) + Ly[j] * np.cos(h),
                                   Lh[j] + h,
                                   Lh[j + 1] - Lh[j], LFt[j], LBt[j + 1],
                                   (Lx[j + 1] - Lx[j]) * np.cos(-Lh[j]) - (Ly[j + 1] - Ly[j]) * np.sin(-Lh[j]),
                                   (Lx[j + 1] - Lx[j]) * np.sin(-Lh[j]) + (Ly[j + 1] - Ly[j]) * np.cos(-Lh[j]),
                                   lw, nbr_of_lanes, lanes_in_x_dir, Vmax, Vmax, Stlj[j], cwj[j])

        CurvedRoads[Lid[j]] = NewCurvedRoad
    return CurvedRoads

def get_roundabout(s, id, connections, path):
    origin_x0 = float(s[0].get('X'))
    origin_y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')
    heading = float(s[1].get('Heading'))
    radius = float(s.get('Radius'))
    lane_width = float(s.get('LaneWidth'))
    number_of_lanes = int(s.get('NumberOfLanes'))
    RoadCrossSection = s[18]
    RoadMarking = s[16]
    heading_of_crosssection = []
    filletradius_of_crosssection = []
    number_of_lanes_of_crosssection = []
    number_of_lanes_in_xdirection_in_crosssection = []
    road_end_marker_in_crossection = []
    for s in RoadCrossSection:
        heading_of_crosssection.append((float(s.get('Heading')) + heading) * np.pi / 180)
        filletradius_of_crosssection.append((float(s.get('FilletRadiusPercentage'))))
        number_of_lanes_of_crosssection.append((int(s.get('NumberOfLanes'))))
        number_of_lanes_in_xdirection_in_crosssection.append((int(s.get('DirectionChangeAfterLane'))))
        road_end_marker_in_crossection.append((str(s.get('RoadEndMarker'))))
        
    cross_walk = []
    for R in RoadMarking:
        if "PedestrianMarkingGeneric" in str(R.get('id')) :
            hw = float(R[1].get('Heading'))*np.pi/180
            cl = float(R.get('CrossingLength'))
            cwh = float(R.get('CrossingWidth'))
            xl = float(R[0].get('X'))
            yl = float(R[0].get('Y'))
            x1 = origin_x0 + (xl - (cl/2)*np.sin(hw))*np.cos(heading) - (yl + (cl/2)*np.cos(hw))*np.sin(heading)
            y1 = origin_y0 + (xl - (cl/2)*np.sin(hw))*np.sin(heading) + (yl + (cl/2)*np.cos(hw))*np.cos(heading)
            x2 = origin_x0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.cos(heading) - (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.sin(heading)
            y2 = origin_y0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.sin(heading) + (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.cos(heading)
            x3 = origin_x0 + (xl + (cl/2)*np.sin(hw))*np.cos(heading) - (yl + (cl/2)*np.cos(hw))*np.sin(heading)
            y3 = origin_y0 + (xl + (cl/2)*np.sin(hw))*np.sin(heading) + (yl + (cl/2)*np.cos(hw))*np.cos(heading)
            cross_walk.append([x1,y1,x2,y2,x3,y3])

    connection_roads = [0,0,0,0]

    for connection in connections:
        
        id_of_Road_A = connection.get('Road_A_UniqueId')
        id_of_Road_B = connection.get('Road_B_UniqueId')
        
        if (id in id_of_Road_A):
            
            connection_roads[int(connection.get('Joint_A_Id'))] = id_of_Road_B
            
        elif (id in id_of_Road_B):
            
            connection_roads[int(connection.get('Joint_B_Id'))] = id_of_Road_A

    mid_crosssection_points = []
    for i in range(len(connection_roads)):
        mid_crosssection_points.append(get_links_points_roundabout(connection_roads[i],path))
        
    return RoundaboutRoad(id, origin_x0, origin_y0, radius, lane_width, heading_of_crosssection, filletradius_of_crosssection, number_of_lanes_of_crosssection, number_of_lanes_in_xdirection_in_crosssection, number_of_lanes, Vmax, Vmax, mid_crosssection_points,road_end_marker_in_crossection, cross_walk)

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
    cw = []
    for R in RoadMarking:
        if "BitmapRoadMarker" in str(R.get('id')) :
            x1 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 - (lw/2) * np.sin(h)
            y1 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0 + (lw/2) * np.cos(h)
            x2 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 + (lw*0.5) * np.sin(h)
            y2 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0  - (lw*0.5) * np.cos(h)
            x3 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0
            y3 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0
            Stl.append((x1, y1, x2, y2, x3, y3,nbr_of_lanes-lanes_in_x_dir,lw))
        if "PedestrianMarkingGeneric" in str(R.get('id')) :
            hw = float(R[1].get('Heading'))*np.pi/180
            cl = float(R.get('CrossingLength'))
            cwh = float(R.get('CrossingWidth'))
            xl = float(R[0].get('X'))
            yl = float(R[0].get('Y'))
            x1 = x0 + (xl - (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y1 = y0 + (xl - (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            x2 = x0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.cos(h) - (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.sin(h)
            y2 = y0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.sin(h) + (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.cos(h)
            x3 = x0 + (xl + (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y3 = y0 + (xl + (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            cw.append([x1,y1,x2,y2,x3,y3])
    return StraightRoad(id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, Vmax, Vmax, Stl, cw)

def get_crosswalk(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')
    h = float(s[1].get('Heading')) * np.pi / 180
    l = float(s.get('RoadLength'))
    lw = float(s.get('LaneWidth'))
    nbr_of_lanes = int(s.get('NumberOfLanes'))
    lanes_in_x_dir = int(s.get('DirectionChangeAfterLane'))
    rw = nbr_of_lanes*lw #total width of the road

    cw = []
    x1 = x0 - (rw/2)*np.sin(h)
    y1 = y0 + (rw/2)*np.cos(h)
    x2 = x0 + l*np.cos(h) - (rw/2)*np.cos(h)
    y2 = y0 + l*np.sin(h) + (rw/2)*np.cos(h)
    x3 = x0 + (rw/2)*np.sin(h)
    y3 = y0 - (rw/2)*np.cos(h)
    cw.append([x1,y1,x2,y2,x3,y3])

    return Crosswalkr(id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, Vmax, Vmax, cw)

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
    cw =[]

    for R in RoadMarking:
        if "BitmapRoadMarker" in str(R.get('id')) :
            x1 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 - (lw/2) * np.sin(h)
            y1 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0 + (lw/2) * np.cos(h)
            x2 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 + (lw*0.5) * np.sin(h)
            y2 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0  - (lw*0.5) * np.cos(h)
            x3 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0
            y3 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0
            Stl.append((x1, y1, x2, y2, x3, y3,nbr_of_lanes-lanes_in_x_dir,lw))
        if "PedestrianMarkingGeneric" in str(R.get('id')) :
            hw = float(R[1].get('Heading'))*np.pi/180
            cl = float(R.get('CrossingLength'))
            cwh = float(R.get('CrossingWidth'))
            xl = float(R[0].get('X'))
            yl = float(R[0].get('Y'))
            x1 = x0 + (xl - (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y1 = y0 + (xl - (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            x2 = x0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.cos(h) - (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.sin(h)
            y2 = y0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.sin(h) + (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.cos(h)
            x3 = x0 + (xl + (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y3 = y0 + (xl + (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            cw.append([x1,y1,x2,y2,x3,y3])


    return EntryRoad(id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, entry_road_angle, apron_length, side_road_length, Vmax, Vmax, Stl, cw)

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
    cw = []
    for R in RoadMarking:
        if "BitmapRoadMarker" in str(R.get('id')) :
            x1 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 - (lw/2) * np.sin(h)
            y1 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0 + (lw/2) * np.cos(h)
            x2 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 + (lw*0.5) * np.sin(h)
            y2 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0  - (lw*0.5) * np.cos(h)
            x3 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0
            y3 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0
            Stl.append((x1, y1, x2, y2, x3, y3,nbr_of_lanes-lanes_in_x_dir,lw))
        if "PedestrianMarkingGeneric" in str(R.get('id')) :
            hw = float(R[1].get('Heading'))*np.pi/180
            cl = float(R.get('CrossingLength'))
            cwh = float(R.get('CrossingWidth'))
            xl = float(R[0].get('X'))
            yl = float(R[0].get('Y'))
            x1 = x0 + (xl - (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y1 = y0 + (xl - (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            x2 = x0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.cos(h) - (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.sin(h)
            y2 = y0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.sin(h) + (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.cos(h)
            x3 = x0 + (xl + (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y3 = y0 + (xl + (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            cw.append([x1,y1,x2,y2,x3,y3])
    return ExitRoad(id, x0, y0, h, l, lw, nbr_of_lanes, lanes_in_x_dir, exit_road_angle, apron_length, side_road_length, Vmax, Vmax, Stl, cw)

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
    lane_offset = int(s.get('LaneOffset'))

    Stl = []
    cw = []

    for R in RoadMarking:
            x1 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 - (lw/2) * np.sin(h)
            y1 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0 + (lw/2) * np.cos(h)
            x2 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0 + (lw*0.5) * np.sin(h)
            y2 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0  - (lw*0.5) * np.cos(h)
            x3 = -float(R[0].get('Y'))*np.sin(h) + float(R[0].get('X'))*np.cos(h)  + x0
            y3 = float(R[0].get('X'))*np.sin(h) + float(R[0].get('Y'))*np.cos(h) +y0
            Stl.append((x1, y1, x2, y2, x3, y3,nbr_of_lanes_start-lanes_in_x_dir_start,lw))
            if "PedestrianMarkingGeneric" in str(R.get('id')) :
                hw = float(R[1].get('Heading'))*np.pi/180
                cl = float(R.get('CrossingLength'))
                cwh = float(R.get('CrossingWidth'))
                xl = float(R[0].get('X'))
                yl = float(R[0].get('Y'))
                x1 = x0 + (xl - (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
                y1 = y0 + (xl - (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
                x2 = x0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.cos(h) - (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.sin(h)
                y2 = y0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.sin(h) + (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.cos(h)
                x3 = x0 + (xl + (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
                y3 = y0 + (xl + (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
                cw.append([x1,y1,x2,y2,x3,y3])
    return AdapterRoad(id, x0, y0, h, l, lw, nbr_of_lanes_start, nbr_of_lanes_end, lanes_in_x_dir_start, lanes_in_x_dir_end, Vmax, Vmax, Stl, cw, lane_offset)

def get_xcross(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')
    h = float(s[1].get('Heading')) * np.pi / 180
    RoadMarking = s[16]
    cs = s[18]
    lw = float(cs[0].get('LaneWidth'))
    cs_h = []
    cs_len_till_stop = []
    cs_nbr_of_lanes = []
    cs_lanes_in_x_dir = []
    cs_l = []
    cs_road_end_marker = []
    for c in cs:
        
        cs_h.append((float(c.get('Heading'))) * np.pi / 180)
        cs_len_till_stop.append(float(c.get('RoadLengthTillStopMarker')))
        cs_nbr_of_lanes.append(int(c.get('NumberOfLanes')))
        cs_lanes_in_x_dir.append(int(c.get('DirectionChangeAfterLane')))
        cs_l.append(float(c.get('RoadEndLength')))
        cs_road_end_marker.append(str(c.get('RoadEndMarker')))
        
    Stl = []
    cw = []

    for i in range(4):
       
        if cs_road_end_marker[i] == "Solid" :
            
            x1 = -lw*(cs_nbr_of_lanes[i]/2)*np.sin(h+cs_h[i]) + (cs_l[i]-cs_len_till_stop[i])*np.cos(h+cs_h[i])  + x0
            y1 = lw*(cs_nbr_of_lanes[i]/2)*np.cos(h+cs_h[i]) + (cs_l[i]-cs_len_till_stop[i])*np.sin(h+cs_h[i]) +y0
            x2 = lw*((cs_nbr_of_lanes[i]/2)-cs_lanes_in_x_dir[i])*np.sin(h+cs_h[i]) + (cs_l[i]-cs_len_till_stop[i])*np.cos(h+cs_h[i])  + x0
            y2 = -lw*((cs_nbr_of_lanes[i]/2)-cs_lanes_in_x_dir[i])*np.cos(h+cs_h[i]) + (cs_l[i]-cs_len_till_stop[i])*np.sin(h+cs_h[i]) +y0
            x3 = (x1+x2)/2
            y3 = (y1+y2)/2
            
            Stl.append((x1, y1, x2, y2, x3, y3,cs_nbr_of_lanes[i]-cs_lanes_in_x_dir[i],lw))
       

    for R in RoadMarking:
        if "PedestrianMarkingGeneric" in str(R.get('id')) :
            hw = float(R[1].get('Heading'))*np.pi/180
            cl = float(R.get('CrossingLength'))
            cwh = float(R.get('CrossingWidth'))
            xl = float(R[0].get('X'))
            yl = float(R[0].get('Y'))
            x1 = x0 + (xl - (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y1 = y0 + (xl - (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            x2 = x0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.cos(h) - (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.sin(h)
            y2 = y0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.sin(h) + (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.cos(h)
            x3 = x0 + (xl + (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y3 = y0 + (xl + (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            cw.append([x1,y1,x2,y2,x3,y3])

     
    return XCrossRoad(id, x0, y0, h, lw, cs_h, cs_len_till_stop, cs_nbr_of_lanes, cs_lanes_in_x_dir, cs_l, Vmax, Vmax, Stl, cw)

def get_ycross(s, id):
    x0 = float(s[0].get('X'))
    y0 = float(s[0].get('Y'))
    Vmax = s.get('MaxSpeed')
    h = float(s[1].get('Heading')) * np.pi / 180
    RoadMarking = s[16]
    cs = s[18]
    lw = float(cs[0].get('LaneWidth'))
    cs_h = []
    cs_len_till_stop = []
    cs_nbr_of_lanes = []
    cs_lanes_in_x_dir = []
    cs_l = []
    cs_road_end_marker = []
    for c in cs:
        cs_h.append((float(c.get('Heading'))) * np.pi / 180)
        cs_len_till_stop.append(float(c.get('RoadLengthTillStopMarker')))
        cs_nbr_of_lanes.append(int(c.get('NumberOfLanes')))
        cs_lanes_in_x_dir.append(int(c.get('DirectionChangeAfterLane')))
        cs_l.append(float(c.get('RoadEndLength')))
        cs_road_end_marker.append(str(c.get('RoadEndMarker')))

    Stl = []
    cw = []

    for i in range(3):
        if cs_road_end_marker[i] == "Solid" :
            x1 = -lw*(cs_nbr_of_lanes[i]/2)*np.sin(h+cs_h[i]) + (cs_l[i]-cs_len_till_stop[i])*np.cos(h+cs_h[i])  + x0
            y1 = lw*(cs_nbr_of_lanes[i]/2)*np.cos(h+cs_h[i]) + (cs_l[i]-cs_len_till_stop[i])*np.sin(h+cs_h[i]) +y0
            x2 = lw*((cs_nbr_of_lanes[i]/2)-cs_lanes_in_x_dir[i])*np.sin(h+cs_h[i]) + (cs_l[i]-cs_len_till_stop[i])*np.cos(h+cs_h[i])  + x0
            y2 = -lw*((cs_nbr_of_lanes[i]/2)-cs_lanes_in_x_dir[i])*np.cos(h+cs_h[i]) + (cs_l[i]-cs_len_till_stop[i])*np.sin(h+cs_h[i]) +y0
            x3 = (x1+x2)/2
            y3 = (y1+y2)/2
            Stl.append((x1, y1, x2, y2, x3, y3,cs_nbr_of_lanes[i]-cs_lanes_in_x_dir[i],lw))

    for R in RoadMarking:
        if "PedestrianMarkingGeneric" in str(R.get('id')) :
            hw = float(R[1].get('Heading'))*np.pi/180
            cl = float(R.get('CrossingLength'))
            cwh = float(R.get('CrossingWidth'))
            xl = float(R[0].get('X'))
            yl = float(R[0].get('Y'))
            x1 = x0 + (xl - (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y1 = y0 + (xl - (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            x2 = x0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.cos(h) - (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.sin(h)
            y2 = y0 + (xl + cwh*np.cos(hw) -(cl/2)*np.sin(hw))*np.sin(h) + (yl + cwh*np.sin(hw) + (cl/2)*np.cos(hw))*np.cos(h)
            x3 = x0 + (xl + (cl/2)*np.sin(hw))*np.cos(h) - (yl + (cl/2)*np.cos(hw))*np.sin(h)
            y3 = y0 + (xl + (cl/2)*np.sin(hw))*np.sin(h) + (yl + (cl/2)*np.cos(hw))*np.cos(h)
            cw.append([x1,y1,x2,y2,x3,y3])

    return YCrossRoad(id, x0, y0, h, lw, cs_h, cs_len_till_stop, cs_nbr_of_lanes, cs_lanes_in_x_dir, cs_l, Vmax, Vmax, Stl, cw)

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
