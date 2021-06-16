##This module contains :class:RoadProcessor that processes road segments in
##order to easily feed coordinates to the vector mapping module.
##Only :class:RoadProcessor should be used externally.

import numpy as np
from utils import dist


## A wrapper class for lanes that will be incrementally fed to the vecor mapping module.
#
#This Wrapper class will be use to define actual lanes, centers and edges of road. For edges and centers, some of the following parameters are irrelevant and
#will be set to default values.
#
#The attributes are :
#
#lane : A tab of point defining an edge or center or lane. (A very bad parameter name)
#
#junction_end/junction_start : String
#
#SpeedLimit/RefSpeed : A float. Value representing the speedlimit/ the reference speed of the lane (only usefull for lane)
class Lane(object):

    ##The constructor
    #@param self The object pointer
    #@param lanes a list of points ([x, y]) representing the road
    #@param junction_end A string with a default value of "NORMAL"
    #@param junction_start A string with a default value of "NORMAL"
    def __init__(self, lanes, junction_end='NORMAL', junction_start='NORMAL'):
        self.lanes = lanes
        self.junction_end = junction_end
        self.junction_start = junction_start
        self.SpeedLimit = -1
        self.RefSpeed = -1
        self.DefinedSpeed = -1

    ##This method return the array lanes (the tab of point defining a lane or edge or center
    #@param self The object pointer
    def get_lanes(self):
        return np.array(self.lanes)

    ##This method return junction_end parameters
    #@param self The object pointer
    def get_junction_end(self):
        return self.junction_end

    ##This method return junction_start parameters
    #@param self The object pointer
    def get_junction_start(self):
        return self.junction_start

    ##This method take a point provided, check if points in the lanes parameters are less than one meter apart from the given point.
    ##If that not the case, this method insert the given in order for the lanes parameters to be less than 1 meter away from each other
    #@param self The object pointer
    #@param point A tuple representing a point (x, y)
    def adjust_for_turn(self, point):

        points = self.lanes
        for i in range(len(points)):
            if(dist(points[i - 1], point) <= 1.0):
                points.insert(i, list(point))
                break

    ##This method modifies the array lanes (the tab of point defining a lane or edge or center)
    #@param self The object pointer
    #@param point A tuple representing a point (x, y)
    def adjust_for_roundabout(self, point):
        points = self.lanes
        for i in range(len(points)):
            if(dist(points[i - 1], point) <= 1.0):
                points.insert(i, list(point))
                break

##Class responsible for processing the Statical Object for the vmap module
#
#The attributes are :
#
#TrfLight: Tab of Traffic Light Object defined in staticalobject.py
#
#StatObject: Tab of StaticalObject Object (defined in staticalobject.py)
class StaticObjectProcessor(object):

    ##The constructor
    #@param self The object pointer
    def __init__(self):
        self.TrfLight = []    # If you want to take into account other Stat Object just add a tab and code the different create and get function
        self.StatObjects = []

    ##A method to add a statical object
    #@param self The object pointer
    #@param statobjects A statical object
    def add_staticobject(self, statobjects):
        self.StatObjects = statobjects

    ##A method to create a statical object
    #@param self The object pointer
    def create_static_object(self):
        self.create_Traffic_Light()

    ##A method to create a traffic light
    #@param self The object pointer
    def create_Traffic_Light(self):
        StatObjects = self.StatObjects
        tflLight = []
        for id in StatObjects.keys():
            if "Light" in id:
                tflLight.append(StatObjects[id])
        self.TrfLight = tflLight


##Class responsible for processing the road segments for the vmap module

class RoadProcessor(object):

    ##The constructor
    #@param self The object pointer
    #@param roads A list of road objects defined in Road.py
    def __init__(self, roads):

        # All of the following list will be filled with Lane Objects
        self.lanes = []
        self.centers = []
        self.edges = []
        self.stoplines = []
        self.crosswalks = []

        # Fill up the Roads list with information from the parse module
        self.roads = roads


    # For a better understanding of the following functions/methods go to the wiki about the Vector Mapper #

    ##Creates the lanes for each roads per RT in roads
    #@param self The object pointer
    def create_lanes(self):
        roads = self.roads.copy()
        self.__create_roundabouts(roads)
        self.__create_xcrossings(roads)
        self.__create_ycrossings(roads)
        self.__create_bezier_roads(roads)
        self.__create_straight_roads(roads)
        self.__create_bend_roads(roads)
        self.__create_entry_roads(roads)
        self.__create_exit_roads(roads)
        self.__create_adapter_roads(roads)
        self.__create_crosswalksR(roads)
        self.__create_clothoid(roads)

    #Creates lanes traveling from each roundabout until the path meets
    #another roundabout, xcrossing or a dead end
    #@param self The object pointer
    #@param roads A list of roads
    def __create_roundabouts(self, roads):
        roundabouts = self.__get_roundabouts()
        for roundabout in roundabouts:
            self.crosswalks.append(roundabout.crosswalk)
            self.__add_roundabout(roundabout)
            roads.pop(roundabout.id, None)

    #Creates lanes traveling from each xcrossing until the path meets
    #another xcrossing or a dead end
    #@param self The object pointer
    #@param roads A list of roads
    def __create_xcrossings(self, roads):
        xcrossings = self.__get_xcrossings()
        for xcrossing in xcrossings:
            self.stoplines.append(xcrossing.stopline)
            self.crosswalks.append(xcrossing.crosswalk)
            roads.pop(xcrossing.id, None)
            self.__add_segment(xcrossing)
            roads.pop(xcrossing.id, None)

    #Creates lanes traveling from each ycrossing until the path meets
    #another ycrossing or a dead end
    #@param self The object pointer
    #@param roads A list of roads
    def __create_ycrossings(self, roads):
        ycrossings = self.__get_ycrossings()
        for ycrossing in ycrossings:
            self.stoplines.append(ycrossing.stopline)
            self.crosswalks.append(ycrossing.crosswalk)
            roads.pop(ycrossing.id, None)
            self.__add_segment(ycrossing)
            roads.pop(ycrossing.id, None)

    ##Creates bezier roads
    #@param self The object pointer
    #@param roads A list of roads
    def __create_bezier_roads(self, roads):
        bezierroads = self.__get_bezierroads()
        for bezierroad in bezierroads:
            self.stoplines.append(bezierroad.stopline)
            self.crosswalks.append(bezierroad.crosswalk)
            road = roads.pop(bezierroad.id, None)
            self.__add_segment(road)


    ##Creates straight roads
    #@param self The object pointer
    #@param roads A list of roads
    def __create_straight_roads(self, roads):
        straightroads = self.__get_straightroads()
        for straightroad in straightroads:
            self.stoplines.append(straightroad.stopline)
            self.crosswalks.append(straightroad.crosswalk)
            road = roads.pop(straightroad.id, None)
            self.__add_segment(road)

    ##Creates crosswalk roads
    #@param self The object pointer
    #@param roads A list of roads
    def __create_crosswalksR(self, roads):
        crosswalks = self.__get_crosswalksR()
        for crosswalkR in crosswalks:
            self.crosswalks.append(crosswalkR.crosswalk)
            roads.pop(crosswalkR.id, None)
            self.__add_segment(crosswalkR)

    ##Creates bend roads
    #@param self The object pointer
    #@param roads A list of roads
    def __create_bend_roads(self, roads):
        bendroads = self.__get_bendroads()
        for bendroad in bendroads:
            self.stoplines.append(bendroad.stopline)
            self.crosswalks.append(bendroad.crosswalk)
            road = roads.pop(bendroad.id, None)
            self.__add_segment(road)

    ##Creates entry roads
    #@param self The object pointer
    #@param roads A list of roads
    def __create_entry_roads(self, roads):
        entryroads = self.__get_entryroads()
        for entryroad in entryroads:
            self.stoplines.append(entryroad.stopline)
            self.crosswalks.append(entryroad.crosswalk)
            road = roads.pop(entryroad.id, None)
            self.__add_entry(road)

    ##Creates exit roads
    #@param self The object pointer
    #@param roads A list of roads
    def __create_exit_roads(self, roads):
        exitroads = self.__get_exitroads()
        for exitroad in exitroads:
            self.stoplines.append(exitroad.stopline)
            self.crosswalks.append(exitroad.crosswalk)
            road = roads.pop(exitroad.id, None)
            self.__add_exit(road)

    ##Creates adapter roads
    #@param self The object pointer
    #@param roads A list of roads
    def __create_adapter_roads(self, roads):
        adapterroads = self.__get_adapterroads()
        for adapterroad in adapterroads:
            self.stoplines.append(adapterroad.stopline)
            self.crosswalks.append(adapterroad.crosswalk)
            road = roads.pop(adapterroad.id, None)
            self.__add_adapter(road)


    ##Creates spiral roads
    #@param self The object pointer
    #@param roads A list of roads
    def __create_clothoid(self, roads):
        clothoids = self.__get_clothoids()
        for clotho in clothoids :
            self.crosswalks.append(clotho.crosswalk)
            self.stoplines.append(clotho.stopline)
            road = roads.pop(clotho.id, None)
            self.__add_segment(road)

    ##Creates a lane which consists of a single path of x and y coordinates.
    ##The path can have a junction end or start
    #@param self The object pointer
    #@param SpeedLimit A Float
    #@param RefSpeed A Float
    #@param DefinedSpeed A Float
    #@param lane A list of points (x, y) representing 
    #@param junction_end A String with the default value "NORMAL"
    #@param junction_start A String with the default value "NORMAL"
    #@param rturns A list of points (x, y) representing a right turn
    #@param lturns A list of points (x, y) representing a left turn
    #@param epoints A list of points (x, y) representing 
    def __add_lane(self, SpeedLimit, RefSpeed, DefinedSpeed, lane, junction_end = 'NORMAL', junction_start = 'NORMAL', rturns = None, lturns = None, epoints = None):
        l = []
        for (x, y) in lane:
            l.append([x, y])
        newlane = Lane(l, junction_end, junction_start)
        newlane.SpeedLimit = SpeedLimit
        newlane.RefSpeed = RefSpeed
        newlane.DefinedSpeed = DefinedSpeed
        if(rturns):
            for point in rturns:
                newlane.adjust_for_turn(point)
        if(lturns):
            for point in lturns:
                newlane.adjust_for_turn(point)
        if(epoints):
            for point in epoints:
                newlane.adjust_for_roundabout(point)
        self.lanes.append(newlane)

    ##Creates a Lane object to add to the list of center lines
    #@param self The object pointer
    #@center A list of list of points (x, y)
    def __add_center(self, center):
        for path in center:
            c = []
            for (x, y) in path:
                c.append([x, y])
            self.centers.append(Lane(c))

    ##Creates a Lane object to add to the list of edges lines
    #@param self The object pointer
    #@edge A list of list of points (x, y)
    def __add_edge(self, edge):
        for path in edge:
            e = []
            for (x, y) in path:
                e.append([x, y])
            self.edges.append(Lane(e))

    ##Breaks down a road segment into lanes, edges and center for the
    ##vmap module
    #@param self The object pointer
    #@param lan
    #@param rturns A list of points (x, y) representing a right turn
    #@param lturns A list of points (x, y) representing a left turn
    def __add_segment(self, lane, rturns = None, lturns = None):
        for i in range(len(lane.l)):
            self.__add_lane(lane.SpeedLimit, lane.SpeedLimit, lane.DefinedSpeed, lane.l[i], rturns = rturns, lturns = lturns)
        self.__add_center(lane.c)
        self.__add_edge(lane.e1)
        self.__add_edge(lane.e2)

    ##Breaks down a road segment into lanes, edges and center for the
    ##vmap module
    #@param self The object pointer
    #@param lane
    #@param rturns A list of points (x, y) representing a right turn
    #@param lturns A list of points (x, y) representing a left turn
    #@param epoints A list of points (x, y) representing 
    def __add_roundabout(self, lane, rturns = None, lturns = None, epoints = None):
            self.__add_segment( lane, rturns = rturns, lturns = lturns)

    ##Breaks down a entry road segment into lanes, edges and center for the
    ##vmap module
    #@param self The object pointer
    #@param lane
    #@param rturns
    #@param lturns
    def __add_entry(self, lane, rturns = None, lturns = None):
        for i in range(len(lane.l)):
            self.__add_lane(lane.SpeedLimit, lane.SpeedLimit, lane.DefinedSpeed, lane.l[i], rturns = rturns, lturns = lturns)
        self.__add_center(lane.c)
        self.__add_edge(lane.e1)
        self.__add_edge(lane.e2)

    ##Breaks down a exit road segment into lanes, edges and center for the
    ##vmap module
    #@param self The object pointer
    #@param lane
    #@param rturns
    #@param lturns
    def __add_exit(self, lane, rturns = None, lturns = None):
        for i in range(len(lane.l)):
            self.__add_lane(lane.SpeedLimit, lane.SpeedLimit, lane.DefinedSpeed, lane.l[i], rturns = rturns, lturns = lturns)
        self.__add_center(lane.c)
        self.__add_edge(lane.e1)
        self.__add_edge(lane.e2)

    ##Breaks down an adapter road segment into lanes, edges and center for the
    ##vmap module
    #@param self The object pointer
    #@param lane
    #@param rturns
    #@param lturns
    def __add_adapter(self, lane, rturns = None, lturns = None):
        for i in range(len(lane.l)):
            self.__add_lane(lane.SpeedLimit, lane.SpeedLimit, lane.DefinedSpeed, lane.l[i], rturns = rturns, lturns = lturns)
        self.__add_center(lane.c)
        self.__add_edge(lane.e1)
        self.__add_edge(lane.e2)

    ##Fetches all roundabouts in the road network
    #@param self The object pointer
    def __get_roundabouts(self):
        roads = self.roads
        ra = []
        for id in roads.keys():
            if "Roundabout" in id:
                ra.append(roads[id])
        return ra

    ##Fetches all xcrossing in the road network
    #@param self The object pointer
    def __get_xcrossings(self):
        roads = self.roads
        xcross = []
        for id in roads.keys():
            if "XCrossing" in id:
                xcross.append(roads[id])
        return xcross

    ##Fetches all xcrossing in the road network
    #@param self The object pointer
    def __get_ycrossings(self):
        roads = self.roads
        ycross = []
        for id in roads.keys():
            if "YCrossing" in id:
                ycross.append(roads[id])
        return ycross

    ##Fetches all straight road in the road network
    #@param self The object pointer
    def __get_straightroads(self):
        roads = self.roads
        straights = []
        for id in roads.keys():
            if "StraightRoad" in id:
                straights.append(roads[id])
        return straights

    ##Fetches all crosswalks in the road network
    #@param self The object pointer
    def __get_crosswalksR(self):
        roads = self.roads
        cross = []
        for id in roads.keys():
            if "PedestrianCrossing" in id:
                cross.append(roads[id])
        return cross

    ##Fetches all Bend road in the road network
    #@param self The object pointer
    def __get_bendroads(self):
        roads = self.roads
        bend = []
        for id in roads.keys():
            if "BendRoad" in id:
                bend.append(roads[id])
        return bend

    ##Fetches all Bend road in the road network
    #@param self The object pointer
    def __get_bezierroads(self):
        roads = self.roads
        bezier = []
        for id in roads.keys():
            if "CurvedRoad" in id or "FlexRoad" in id:
                bezier.append(roads[id])
        return bezier

    ##Fetches all Spiral road in the road network
    #@param self The object pointer
    def __get_clothoids(self):
        roads =self.roads
        clo = []
        for id in roads.keys():
            if "ClothoidRoad" in id :
                clo.append(roads[id])
        return clo

    ##Fetches all Entry road in the road network
    #@param self The object pointer
    def __get_entryroads(self):
        roads = self.roads
        entry = []
        for id in roads.keys():
            if "EntryLaneRoad" in id:
                entry.append(roads[id])
        return entry

    ##Fetches all Exit road in the road network
    #@param self The object pointer
    def __get_exitroads(self):
        roads = self.roads
        exit = []
        for id in roads.keys():
            if "ExitLaneRoad" in id:
                exit.append(roads[id])
        return exit

    ##Fetches all Adapter road in the road network
    #@param self The object pointer
    def __get_adapterroads(self):
        roads = self.roads
        adapter = []
        for id in roads.keys():
            if "LaneAdapterRoad" in id:
                adapter.append(roads[id])
        return adapter
