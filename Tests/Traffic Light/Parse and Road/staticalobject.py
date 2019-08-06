'''This module contains all of the code defining the structure of different statical object. By taking initial values from the parser the classes calculate a mathematical definition of the statical object.

.. moduleauthor:: Nicolas Helleboid <nicohe@kth.se>

'''


class StaticalObject:
    '''This is the interface class for all the Statical Objects. Every statical object has certain things in common such as coordinates of its orign and heading.

        :param id: represent the ID of the statical object (TrafficLightRoadSideNL, UnitedSet...).The exact ID can be found in the pex file.
        :type id: string

        :param x0: The x coordinate of orign of the Statical Object
        :type x0: Float

        :param y0: The y coordinate of orign of the Statical Object
        :type y0: Float

        :param h: Heading of the Statical Object
        :type h: Float

    '''
    def __init__(self, id):
        self.id = id
        self.x0 = 0
        self.y0 = 0
        self.h = 0


    def getOrignPoint(self):
        '''This method returns the orign coordinates of the statical object.
        :returns (Float, Float)
        '''
        return (self.x0, self.y0)

    def getHeading(self):
        '''This method returns the orign coordinates of the statical object.

        :returns Float
        '''
        return self.h

class TrafficLight(StaticalObject):
    '''
    This a representation of the Traffic Light in Prescan.

    :param id: Unique id.
    :type id: String

    :param x0: The x coordinate of orign of the Traffic Light
    :type x0: Float

    :param y0: The y coordinate of orign of the Traffic Light
    :type y0: Float

    :param h: Heading of the Traffic Light
    :type h: Float

    :param s: Style of the Traffic Light (RoadSide, Japan overhead and so on...). Cf Parse.py for the converting-list integer to style
    :type s: Integer



    '''
    def __init__(self, id, x0, y0, h, s):
        StaticalObject.__init__(self, id)
        self.x0 = x0
        self.y0 = y0
        self.h = h
        self.s = s


