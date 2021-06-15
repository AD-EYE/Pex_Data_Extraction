##This module contains all of the code defining the structure of different statical object. By taking initial values from the parser the classes calculate a mathematical definition of the statical object.
##.. moduleauthor:: Nicolas Helleboid <nicohe@kth.se>


##This is the interface class for all the Statical Objects. Every statical object has certain things in common such as coordinates of its orign and heading.
#
#The attributes are :
#
#id : a string. Represents the ID of the statical object (TrafficLightRoadSideNL, UnitedSet...).The exact ID can be found in the pex file.id: represent the ID of the statical object (TrafficLightRoadSideNL, UnitedSet...).The exact ID can be found in the pex file.
#
#x0 : a float. The x coordinate of orign of the Statical Object
#
#y0 : a float. The y coordinate of orign of the Statical Object
#
#h : a float. Heading of the Statical Object
class StaticObject:

    ##The constructor
    #@param self The object pointer
    #@param id A string. The id of the object
    def __init__(self, id):
        self.id = id
        self.x0 = 0
        self.y0 = 0
        self.h = 0

    ##This method returns the orign coordinates of the statical object.
    #returns (Float, Float)
    #@param self The object pointer
    def getOrignPoint(self):
        return (self.x0, self.y0)

    ##This method returns the orign coordinates of the statical object.
    #returns Float
    #@param self The object pointer
    def getHeading(self):
        return self.h

##This a representation of the Traffic Light in Prescan.
#
#The attributes are :
#
#id : A string. The Unique id
#
#x0 : A Float. The x coordinate of orign of the Traffic Light
#
#y0 : A Float. The y coordinate of orign of the Traffic Light
#
#h : A Float. Heading of the Traffic Light
#
#s : An Integer. Style of the Traffic Light (RoadSide, Japan overhead and so on...). Cf Parse.py for the converting-list integer to style.

class TrafficLight(StaticObject):

    ##The constructor
    #
    #@param self The object pointer
    #@param id A string. The id of the object
    #@param x0 A Float. The x coordinate of orign of the Traffic Light
    #@param y0 A Float. The y coordinate of orign of the Traffic Light
    #@param h A Float. Heading of the Traffic Light
    #@param s An Integer. Style of the Traffic Light
    def __init__(self, id, x0, y0, h, s):
        StaticObject.__init__(self, id)
        self.x0 = x0
        self.y0 = y0
        self.h = h
        self.s = s


