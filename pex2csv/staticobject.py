##@package staticobject
#This module contains all of the code defining the structure of different statical object. By taking initial values from the parser the classes calculate a mathematical definition of the statical object.
#
#moduleauthor: Nicolas Helleboid <nicohe@kth.se>


##This is the interface class for all the Statical Objects. Every statical object has certain things in common such as coordinates of its orign and heading.
class StaticObject:

    ##The constructor
    #@param self The object pointer
    #@param id A string. The id of the object
    def __init__(self, id):
        ##A string. Represents the ID of the statical object (TrafficLightRoadSideNL, UnitedSet...).The exact ID can be found in the pex file.id: represent the ID of the statical object (TrafficLightRoadSideNL, UnitedSet...).The exact ID can be found in the pex file.
        self.id = id
        ##A float. The x coordinate of orign of the Statical Object
        self.x0 = 0
        ##A float. The y coordinate of orign of the Statical Object
        self.y0 = 0
        ##A float. Heading of the Statical Object
        self.h = 0

    ##This method returns the coordinates of the statical object's origin.
    #returns (Float, Float)
    #@param self The object pointer
    def getOrignPoint(self):
        return (self.x0, self.y0)

    ##This method returns the initial heading of the statical object.
    #returns Float
    #@param self The object pointer
    def getHeading(self):
        return self.h

##This a representation of the Traffic Light in Prescan.
class TrafficLight(StaticObject):

    ##The constructor
    #@param self The object pointer
    #@param id A string. The id of the object
    #@param x0 A Float. The x coordinate of orign of the Traffic Light
    #@param y0 A Float. The y coordinate of orign of the Traffic Light
    #@param h A Float. Heading of the Traffic Light
    #@param s An Integer. Style of the Traffic Light
    def __init__(self, id, x0, y0, h, s):
        StaticObject.__init__(self, id)
        ##A Float. The x coordinate of orign of the Traffic Light
        self.x0 = x0
        ##A Float. The y coordinate of orign of the Traffic Light
        self.y0 = y0
        ##A Float. Heading of the Traffic Light
        self.h = h
        ##An Integer. Style of the Traffic Light (RoadSide, Japan overhead and so on...). Cf Parse.py for the converting-list integer to style.
        self.s = s


