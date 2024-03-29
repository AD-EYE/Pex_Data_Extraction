##@package road
#This module contains all of the code defining the structure of different
#road segments. By taking initial values from the parser the classes calculate a
#mathematical definition of the road type. So we use the geometry created in
#path.py to define the different roadtype (ex: we use the Bend type to create a Roundabout)

from path import *
import numpy as np
from utils import *

##This is the interface class for all the road types. 
#Every road has certain things in common such as a center, edges, lanes and SpeedLimit/RefSpeed.
class Road:

    ##The constructor
    #@param self The object pointer
    #@param id A string. The road type id.
    def __init__(self, id):
        ##A string. Represent the ID of the road (Bendroad, StraightRoad...).The exact ID can be found in the pex file.
        self.id = id
        ##A list of points (x, y) defining the center of the road
        self.c = []
        ##A list of points (x, y) defining one edge of the road
        self.e1 = []
        ##A list of points (x, y) defining one edge of the road
        self.e2 = []
        ##A list of lists of points (x, y) defining the lanes of the road. Base components are floats.
        self.l = []
        ##A list of lists of points representing the stoplines. Base components are floats.
        self.stopline = []
        ##A list of lists of points representing the crosswalks. Base components are floats.
        self.crosswalk = []
        ##An integer
        self.previous_road = -1
        ##An integer
        self.next_road = -1
        ##A Float. Defines the speed limit on the road.
        self.SpeedLimit = 1
        ##A float. Defines the speed reference on the road.
        self.RefSpeed = 1
        ##A list of Float defining the speed profile (Speed Limit per RoadType)
        self.SpeedProfil = self.SpeedProfil = [70,40,70,70,20,90,20,70,70,50]

    ##This method returns the starting coordinates of the road's center path. 
    #Some road segments might not have a starting point, for example the roundabout road. Those segments will have to override this function accordingly.
    #
    #Returns (Float, Float)
    def getstart(self):
        return self.c[0].getstart()

    ##This method returns the last coordinates of the road's center path.
    #Some road segments might not have an endpoint, for example the roundabout road. Those segments will have to override this function accordingly.
    #
    #Returns (Float, Float)
    def getend(self):
        return self.c[0].getend()

##This a representation of the bend road in Prescan.
class BendRoad(Road):

    ##The constructor
    #@param self the object pointer
    #@param id A string. Unique id.
    #@param x0 A float. The x coordinate of the starting point of the segment
    #@param y0 A float. The y coordinate of the starting point of the segment
    #@param h A float. Global heading of the segment at the starting point
    #@param rh A float. Heading of the segment relative to its heading
    #@param clr A float. Center line radius.
    #@param lw A float. The lane width.
    #@param nbr_of_lanes An integer. the nuber of lanes
    #@param lanes_going_OUT An integer. Number of lanes going out of the crossroad. Used to reverse the lane that goes out of the crossroad
    #@param SpeedL A float. The speed limit
    #@param RefS A float. The reference speed
    #@param Stl List of lists contening relevant points (3 points per list) describing a stopline
    #@param cw List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk
    def __init__(self, id, x0, y0, h, rh, clr, lw, nbr_of_lanes, lanes_going_OUT, SpeedL, RefS, Stl, cw):

        # General Initialization

        Road.__init__(self, id)     #Gave the Id linked to BendRoad
        ##A float. The speed limit
        self.SpeedLimit = SpeedL    #Set the different speeds
        ##A float. The reference speed
        self.RefSpeed = RefS
        ##List of lists contening relevant points (3 points per list) describing a stopline. Base components are floats
        self.stopline = Stl
        ###List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base components are floats
        self.crosswalk = cw
        ##A Float. Represent the speed that the road has per default (defined by the speedprofil in the Road Class)
        self.DefinedSpeed = self.SpeedProfil[1]


        # Lanes, Center and Edges of the Road

        self.c.append(Bend( x0, y0, h, rh, clr))

        self.e1.append(Bend( x0 - lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2),      #Buggy FIX HERE for Object/Tab PB
                        y0 + lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2),
                        h, rh, clr - np.sign(rh) * lw * lanes_going_OUT))

        self.e2.append(Bend( x0 - lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2),      #Same
                        y0 - lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2),
                        h, rh, clr + np.sign(rh) * lw * (nbr_of_lanes -lanes_going_OUT)))

        lwi = (nbr_of_lanes - 1) * lw                                         #This work. To better understand how, i recommand doing this code by hand in a simple case
        for _ in range(nbr_of_lanes):
            self.l.append(Bend( x0 + lwi * np.cos(h + np.pi / 2) / 2,
                                y0 + lwi * np.sin(h + np.pi / 2) / 2,
                               h, rh, clr - np.sign(rh) * lwi / 2))
            lwi -= 2 * lw

        #This changes the direction of the lanes that drive backwards
        if nbr_of_lanes-lanes_going_OUT>0:
            for i in range(nbr_of_lanes-lanes_going_OUT):
                l=[]
                for (x, y) in self.l[i]:
                    l.append([x, y])
                l = l[::-1]
                self.l[i] = l

##This is a representation of Spiral roads (Clothoïd) in Prescan. An Euler Spiral is used to represent it
class ClothoidRoads (Road):


    ##The constructor
    #@param self The object pointer
    #@param id. Unique Id
    #@param x0 A float. The x coordinate of the starting point of the spiral
    #@param y0 A float. The y coordinate of the starting point of the spiral
    #@param h A float. Global heading of the bezier curve at its starting point
    #@param C2 A float. Constant describing the spiral. If R the radius of the spiral at the curvilinear abscissa L, R*L =C**2, and C2 = C**2
    #@param Lstart A float. curvilinear abscissa of the start of the spiral
    #@param Lend A float. curvilinear abscissa of the end of the spiral
    #@param flipped A boolean. Indicates if the orientation of the spiral is flipped
    #@param lw A float. The lane width
    #@param nbr_of_lanes An integer. The number of lanes
    #@param lanes_in_x_dir An integer. The number of lanes going out of the crossroad. Used to reverse the lane that goes out of the crossroad
    #@param Tabpointcon A list of floats representing points. Used to check if the end of the road is connected to the start of another one
    #@param SpeedL A float. The speed limit
    #@param RefS A float. The reference speed
    #@param cw list of lists with relevant points (3 points per lists) describing a crosswalk. Base component is a Float.
    #@param Stl List of lists contening relevant points (3 points per list) describing a stopline. Base component is a Float.

    def __init__(self, id, x0, y0, h, C2, Lstart, Lend, flipped, lw, nbr_of_lanes, lanes_in_x_dir, Tabpointcon, SpeedL, RefS, cw, Stl):

        # General Initialization

        Road.__init__(self, id)
        ##A float. The speed limit
        self.SpeedLimit = SpeedL
        ##A float. The reference speed
        self.RefSpeed = RefS
        ##List of lists contening relevant points (3 points per list) describing a stopline. Base component are Floats.
        self.stopline = Stl
        ##List of lists with relevant points (3 points per lists) describing a crosswalk. Base component are Floats.
        self.crosswalk = cw
        ##A Float. Represent the speed that the road has per default (defined by the speedprofil in the Road Class)
        self.DefinedSpeed = self.SpeedProfil[2]


        # we calculate clothoid roads with an integration, so, step by step, the error increases and the last point
        # of the clothoid is one of two meter away of where it shoul be. In order to correct it, we calculate 2
        # spirals : one starting from (x0,y0) going in the x direction, and one starting from the end of the road
        # (xend2, yend2) and going in the reverse x direction. Then we obtain the good spiral by making the average
        # spiral of the 2 spirals calculated. The average is weigh by the curvilinear abscissa of the point we calculate.
        # (xend, yend) is the (x0,y0) of the road attached to the end of the spiral road
        diff = nbr_of_lanes/2
        center1 = Clothoid(x0, y0, h, C2, 1.0, Lstart, Lend)
        cent1 = []
        for (x,y) in center1 :
            cent1.append([x,y])
            xend, yend = x,y

        if flipped == True : # if the spiral road is flipped, (xend,yend) is the axial symmetric of (xend,yend) calculated.  symmetry axis : line with heading = h and going through (x0,y0)
            a1 = np.tan(h)
            b1 = y0 - a1*x0
            a2 = np.tan(h+np.pi/2)
            b2 = cent1[len(cent1)-1][1] - a2*cent1[len(cent1)-1][0]
            xi = (b2-b1)/(a1-a2)
            yi = a1*xi + b1
            cent1[len(cent1)-1][0] = 2*xi - cent1[len(cent1)-1][0]
            cent1[len(cent1)-1][1] = 2*yi - cent1[len(cent1)-1][1]


        xend, yend = cent1[len(cent1)-1][0], cent1[len(cent1)-1][1]
        xend2, yend2 = xend + 1000, yend - 1000
        for k in range (len(Tabpointcon)): # here we find (xend2, yend2)
            if Tabpointcon[k] != []:
                (x, y) = Tabpointcon[k][0]
                if dist((x,y),(xend,yend)) < dist((xend2,yend2),(xend,yend)) :
                    xend2, yend2 = x,y
        if dist((xend2,yend2),(xend,yend))>5 : # if the end of the spiral road is not connected to the start of an other road
            print ("The rules of the wiki aren't followed : you should connect the end of a spiral road to the start of an other road (except crossroads/roundabouts)")

        center2 =  Clothoid(xend2, yend2, h, C2, -1.0, Lend, Lstart) # spiral driving backwards
        cent2 = []
        for (x,y) in center2 :
            cent2.append([x,y])

        if flipped == True : # reverses the spiral (cf line 215)
            c =[cent1,cent2]
            a1 = np.tan(h)
            a2 = np.tan(h+np.pi/2)
            for elem in c :
                b1 = elem[0][1] - a1*elem[0][0]
                for k in range (len(elem)):
                    b2 = elem[k][1] - a2*elem[k][0]
                    xi = (b2-b1)/(a1-a2)
                    yi = a1*xi + b1
                    elem[k][0] = 2*xi - elem[k][0]
                    elem[k][1] = 2*yi - elem[k][1]

        cent = []
        nbr = min(len(cent1),len(cent2))
        for k in range(nbr): # average of the two spirals
            x1, y1 = cent1[k]
            x2, y2 = cent2[nbr-1-k]
            x = (x1*(nbr-k-1) + x2*k)/(nbr-1)
            y = (y1*(nbr-k-1) + y2*k)/(nbr-1)
            cent.append([x,y])

        if (h>np.pi/2) and (h<3*np.pi/2) :
            cent.reverse()


        for i in range (nbr_of_lanes): # now we add the lanes
            lane = []
            count = 0
            angle = h
            for (x,y) in cent :
                if count>0:
                    pt0 = (cent[count-1])
                    pt1 = (cent[count])

                else :
                    pt0 = cent[0]
                    pt1 = cent[1]
                H = dist(pt0,pt1)
                A = abs(pt0[0]-pt1[0])
                if H != 0:
                    angle = np.arccos( A / H )
                    if pt0[0]< pt1[0]:
                        if pt1[1]< pt0[1]:
                            angle = -angle
                        x1 = x - lw*(i+0.5-diff)*np.sin(angle)
                        y1 = y + lw*(i+0.5-diff)*np.cos(angle)

                    else:
                        if pt1[1]> pt0[1]:
                            angle = -angle
                        x1 = x + lw*(i+0.5-diff)*np.sin(angle)
                        y1 = y - lw*(i+0.5-diff)*np.cos(angle)
                    lane.append([x1,y1])
                count += 1
            self.l.append(lane)




        if nbr_of_lanes-lanes_in_x_dir>0: # reverse the lanes driving backwards
            for j in range(nbr_of_lanes-lanes_in_x_dir):
                lane=[]
                for (x, y) in self.l[j+lanes_in_x_dir]:
                    lane.append([x, y])
                lane = lane[::-1]
                self.l[j+lanes_in_x_dir] = lane








##This a representation of the curved road in Prescan. A bezier curve is used to represent it.
class CurvedRoad(Road):


    ##The constructor
    #@param self The object pointer
    #@param id A string. Unique id
    #@param x0 A float. The x coordinate of the starting point of the bezier curve
    #@param y0 A float. The y coordinate of the starting point of the bezier curve
    #@param h A float. Global heading of the bezier curve at its starting point
    #@param rh A float. Heading of the bezier curve relative to its starting point
    #@param cp1 A float. Represents the distance between the first control point and the starting point at an angle that's equal to the heading.
    #@param cp2 A float. Represents the distance between the second control point and the endpoint at an angle that's equal to the heading plus the relative heading.
    #@param dx A float. Relative x offset of the endpoint from the starting point
    #@param dy A float. Relative y offset of the endpoint from the starting point
    #@param lw A Float. Lane width
    #@param nbr_of_lanes An integer. Number of lanes.
    #@param lanes_going_OUT An integer. Number of lanes going out of the crossroad. Used to reverse the lane that goes out of the crossroad
    #@param SpeedL A float. The speed limit
    #@param RefS A float. The speed of reference
    #@param cw List of lists with relevant points (3 points per lists) describing a crosswalk. Base component is a Float.
    #@param Stl List of lists contening relevant points (3 points per list) describing a stopline. Base component is a Float.

    def __init__(self, id, x0, y0, h, rh, cp1, cp2, dx, dy, lw, nbr_of_lanes, lanes_going_OUT, SpeedL, RefS, Stl, cw): #Same as BendRoad

        # General Initialization

        Road.__init__(self, id)
        ##A float. The speed limit
        self.SpeedLimit = SpeedL
        ##A float. The speed of reference
        self.RefSpeed = RefS
        ##List of lists contening relevant points (3 points per list) describing a stopline. Base component is a Float
        self.stopline = Stl
        ##list of lists with relevant points (3 points per lists) describing a crosswalk. Base component is a Float.
        self.crosswalk = cw
        ##A Float. Represent the speed that the road has per default (defined by the speedprofile in the Road Class)
        self.DefinedSpeed = self.SpeedProfil[2]

        # Creation of the points needed for the Bezier Curve

        x_ = dx * np.cos(h) - dy * np.sin(h)
        y_ = dx * np.sin(h) + dy * np.cos(h)
        x1 = x0 + cp1 * np.cos(h)
        y1 = y0 + cp1 * np.sin(h)
        x2 = x0 + x_ - cp2 * np.cos(h + rh)
        y2 = y0 + y_ - cp2 * np.sin(h + rh)
        x3 = x0 + x_
        y3 = y0 + y_

        xs = [x0, x1, x2, x3]   # Those two lists are used to define a Bezier Curve cf Path.py
        ys = [y0, y1, y2, y3]

        # Lanes, Center and Edges of the Road

        self.c.append(Curve(xs, ys, 0))
        self.e1.append(Curve(xs, ys, lw * nbr_of_lanes / 2))
        self.e2.append(Curve(xs, ys, -lw * nbr_of_lanes / 2))

        lwi = -(nbr_of_lanes - 1) * lw / 2
        for _ in range(nbr_of_lanes):
            lane = Curve(xs,ys,lwi)
            self.l.append(lane)
            lwi += lw

        #This changes the direction of the lanes that drive backwards
        if nbr_of_lanes-lanes_going_OUT>0:
            for i in range(nbr_of_lanes-lanes_going_OUT):
                l=[]
                for (x, y) in self.l[i]:
                    l.append([x, y])
                l = l[::-1]
                self.l[i] = l



##This a representation of the roundabout. Each roundabout contains road cross sections that represent the exits and entries to the segment.
class RoundaboutRoad(Road):
     
    ##The constructor
    #@param self the object pointer
    #@param id A string. Unique id
    #@param origin_x0 A float. The x coordinate of the center of the roundabout.
    #@param origin_y0 A float. The y coordinate of the center of the roundabout.
    #@param radius A float. Distance from the center of the roundabout to the center lane.
    #@param lane_width A float. Lane width.
    #@param heading_of_crosssection A list of float. List of headings in radians
    #@param filletradius_of_crosssection A list of float.
    #@param number_of_lanes_of_crossection A list of integers. List of the number of lanes of each exit
    #@param number_of_lanes_in_xdirection_in_crosssection A list of integers. List of the new directions after each exit.
    #@param number_of_lanes An iteger. The number of lanes
    #@param SpeedL A float. The speed limit
    #@param RefS A float. The speed of reference
    #@param mid_crosssection_points A list of the connecting points between roads.
    #@param road_end_marker_in_crosssection A string. A string which shows whether stoplines are included or not
    #@param cross_walk List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base component is a Float.
    
    def __init__(self, id, origin_x0, origin_y0, radius, lane_width, heading_of_crosssection, filletradius_of_crosssection, number_of_lanes_of_crossection, number_of_lanes_in_xdirection_in_crosssection, number_of_lanes, SpeedL, RefS, mid_crosssection_points,road_end_marker_in_crosssection, cross_walk):



        # General Initialization

        Road.__init__(self, id)
        ##A float. The speed limit
        self.SpeedLimit = SpeedL
        ##A float. The speed of reference
        self.RefSpeed = RefS

        ##A list of connecting points.
        self.connection_roads = mid_crosssection_points
        ##Represent the speed that the road has per default (defined by the speedprofil in the Road Class)
        self.DefinedSpeed = self.SpeedProfil[3]
        ##List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base component is a Float.
        self.crosswalk = cross_walk
        
        # Creating the lanes of roundabout using circles defining the lanes.
        # For the first lane, we take radius as the same radius of roundabout and calculate the lane points
        radius_of_circles_defining_roundabout = radius
        for lane_index in range(number_of_lanes):
            # From path.py we find the geometry related to bend road which defines the roundabout
            lane_geometry =Bend(origin_x0, origin_y0 - (radius_of_circles_defining_roundabout - lane_width/2), 0, 2 * np.pi, radius_of_circles_defining_roundabout - lane_width/2)
            # For the second lane we take the radius subtracting the lane width,and calculate the lane points
            radius_of_circles_defining_roundabout = (radius_of_circles_defining_roundabout - lane_width)
            #Next we append the lane points to the current lane.
            points_of_the_current_lane = []
            for (x,y) in lane_geometry:
                points_of_the_current_lane.append([x, y])
            self.l.append(points_of_the_current_lane)

        # A Roundabout road has four crosssections,for each cross section,there is an entry and exit lane.
        # To create each of these lanes, we use these parameters defined below.

        for crosssection_index in range(4):

            number_of_lanes = number_of_lanes_of_crossection[crosssection_index]
            number_of_exit_lanes = number_of_lanes_in_xdirection_in_crosssection[crosssection_index]
            number_of_entry_lanes = number_of_lanes - number_of_exit_lanes
            fillet_radius = filletradius_of_crosssection[crosssection_index]
            
            # First we  calculate the starting points for both entry and exit lanes,using the midcrossection points.

            starting_point = mid_crosssection_points[crosssection_index]
            
            starting_point_of_entry_lane = (starting_point[0][0] - (number_of_lanes/2) * lane_width * np.sin(heading_of_crosssection[crosssection_index]), starting_point[0][1] + (number_of_lanes / 2) * lane_width * np.cos(heading_of_crosssection[crosssection_index]))
            
            starting_point_of_exit_lane = (starting_point[0][0] + (number_of_lanes/2) * lane_width * np.sin(heading_of_crosssection[crosssection_index]), starting_point[0][1] - (number_of_lanes / 2) * lane_width * np.cos(heading_of_crosssection[crosssection_index]))
           

            #  The following math is used for forming the entry lane.


            counter = 0
            for lane_index in range(number_of_entry_lanes):
               
                #Here we calculate the centre of the circle defining the entry lane,and then using that centre we define the circle.
                center_of_circle_of_entrylane = (starting_point_of_entry_lane[0] - radius * (fillet_radius / 100) * np.sin(heading_of_crosssection[crosssection_index]), starting_point_of_entry_lane[1] + (radius * (fillet_radius / 100)) * np.cos(heading_of_crosssection[crosssection_index]))
                circle_entry_lane = [center_of_circle_of_entrylane[0], center_of_circle_of_entrylane[1], radius * (fillet_radius / 100) + (lane_index + 1) * lane_width] # Circle describe by the entry access
               
              
                # main circle of the roundabout
                main_circle = [origin_x0, origin_y0, (radius - lane_width / 2)]
                
                # Starting point of the entry Lane
                (x_position_of_lane_startingpoint, y_position_of_lane_startingpoint) = (starting_point_of_entry_lane[0] + (lane_index+1+counter) * (lane_width / 2) * np.sin(heading_of_crosssection[crosssection_index]), starting_point_of_entry_lane[1] - (lane_index + 1 + counter) * (lane_width / 2) * np.cos(heading_of_crosssection[crosssection_index]))

                # Point of instersection between main circle and circle described by the entry lane
                (x_position_of_intersection,y_position_of_intersection) = Intersection_Circle(circle_entry_lane,main_circle)[1]

                #Next we find  the  point on the main circle which is closest to the point of intersection.
                #To find that we keep on calculating the distance between  two points,and take the point which returns the minimum distance value,as the closest.
                # Initially we set the  distance between first point of the lane point as the minimum distance and calculate the distance of that point to the point of intersection.
                minimum_distance = dist(self.l[0][0],(x_position_of_intersection,y_position_of_intersection))
                index_value_of_closest_point = 0
                for n in range(len(self.l[0])):
                    # Calculating the distance using dist function and comparing it with the initial value
                    if dist(self.l[0][n],(x_position_of_intersection,y_position_of_intersection)) < minimum_distance:
                        minimum_distance = dist(self.l[0][n],(x_position_of_intersection,y_position_of_intersection))
                        index_value_of_closest_point = n

                #Next we define the three points for forming the curve road, which defines the entry lane

                (x_position_of_firstpoint, y_position_of_firstpoint) = self.l[0][index_value_of_closest_point+5]
                (x_position_of_secondpoint,y_position_of_secondpoint) = self.l[0][index_value_of_closest_point+3]
                (x_position_of_thirdpoint,y_position_of_thirdpoint) = self.l[0][index_value_of_closest_point]

                x_position_for_defining_curve = [x_position_of_lane_startingpoint, x_position_of_thirdpoint, x_position_of_secondpoint, x_position_of_firstpoint]
                y_position_for_defining_curve = [y_position_of_lane_startingpoint, y_position_of_thirdpoint, y_position_of_secondpoint, y_position_of_firstpoint]

                # From path.py, we find out the lane geometry related to curved road and append the points to the lane,which ultimately forms the entry lane.
                lane_geometry = Curve(x_position_for_defining_curve, y_position_for_defining_curve, 0)
                points_of_the_current_lane = []
                for (x,y) in lane_geometry:
                    points_of_the_current_lane.append([x, y])
                counter +=1
                self.l.append(points_of_the_current_lane)
       
            # Exit access
            # Here we follow the same method used in calculating entry lane expect for the math
            counter =0
            for lane_index in range(number_of_exit_lanes):

                center_of_circle_of_exitlane = (starting_point_of_exit_lane[0] + radius * (fillet_radius / 100) * np.sin(heading_of_crosssection[crosssection_index]), starting_point_of_exit_lane[1] - (radius * (fillet_radius / 100)) * np.cos(heading_of_crosssection[crosssection_index]))

                circle_exit_lane = [center_of_circle_of_exitlane[0], center_of_circle_of_exitlane[1], radius * (fillet_radius / 100) + (lane_index + 1) * lane_width]

                main_circle = [origin_x0, origin_y0, (radius - lane_width / 2)]

                (x_position_of_lane_startingpoint,y_position_of_lane_startingpoint) = (starting_point_of_exit_lane[0] - (lane_index+1+counter) * (lane_width / 2) * np.sin(heading_of_crosssection[crosssection_index]), starting_point_of_exit_lane[1] + (lane_index + 1 + counter) * (lane_width / 2) * np.cos(heading_of_crosssection[crosssection_index]))

                (x_position_of_intersection,y_position_of_intersection) = Intersection_Circle(circle_exit_lane,main_circle)[0]

                minimum_distance= dist(self.l[0][0],(x_position_of_intersection,y_position_of_intersection))
                index_value_of_closest_point = 0
                for n in range(len(self.l[0])):

                    if dist(self.l[0][n],(x_position_of_intersection,y_position_of_intersection)) < minimum_distance:
                        minimum_distance = dist(self.l[0][n],(x_position_of_intersection,y_position_of_intersection))
                        index_value_of_closest_point = n


                (x_position_of_firstpoint, y_position_of_firstpoint) = self.l[0][index_value_of_closest_point-5]
                (x_position_of_secondpoint,y_position_of_secondpoint) = self.l[0][index_value_of_closest_point-3]
                (x_position_of_thirdpoint,y_position_of_thirdpoint) = self.l[0][index_value_of_closest_point+1]

                x_position_for_defining_curve = [x_position_of_firstpoint, x_position_of_secondpoint, x_position_of_thirdpoint, x_position_of_lane_startingpoint]
                y_position_for_defining_curve = [y_position_of_firstpoint, y_position_of_secondpoint, y_position_of_thirdpoint, y_position_of_lane_startingpoint]
                lane_geometry = Curve(x_position_for_defining_curve, y_position_for_defining_curve, 0)
                points_of_the_current_lane = []
                for (x,y) in lane_geometry:
                    points_of_the_current_lane.append([x, y])
                self.l.append(points_of_the_current_lane)
                counter +=1

        #Calculation of stopline
        #To find the three points used for calculating the stop line,we use the same math as we used for calculating the entry and exit lane
        #Except that we use the radius as radius of the roundabout and not substracting it from the lane width

        # First we need to find out points for an alternate lane ,with radius of the circles defining roundbout

        alternate_lane = []
        radius_for_alternate_lane = radius
        for lane_index in range(number_of_lanes):
            alternate_lane_geometry =Bend(origin_x0, origin_y0 - (radius_for_alternate_lane), 0, 2 * np.pi, radius_for_alternate_lane)
            radius_for_alternate_lane = (radius_for_alternate_lane - lane_width)
            current_alternate_lane = []
            for (x,y) in alternate_lane_geometry:
                current_alternate_lane.append([x, y])
                alternate_lane.append(current_alternate_lane)
        for crosssection_index in range(4):

            road_end_marker = road_end_marker_in_crosssection[crosssection_index]
            number_of_lanes = number_of_lanes_of_crossection[crosssection_index]
            number_of_exit_lanes = number_of_lanes_in_xdirection_in_crosssection[crosssection_index]
            number_of_entry_lanes = number_of_lanes - number_of_exit_lanes
            fillet_radius = filletradius_of_crosssection[crosssection_index]

            #We use the road_end_marker to decide whether we have to append stopline.If it is solid,append and if it is 'none',disable the stopline.
            if road_end_marker_in_crosssection[crosssection_index] == "Solid":

                starting_point = mid_crosssection_points[crosssection_index]       
                starting_point_of_entry_lane = (starting_point[0][0] - (number_of_lanes/2) * lane_width * np.sin(heading_of_crosssection[crosssection_index]), starting_point[0][1] + (number_of_lanes / 2) * lane_width * np.cos(heading_of_crosssection[crosssection_index]))        
                
                counter = 0
                for lane_index in range(number_of_entry_lanes):
                    #print(lane_index)    
                    center_of_circle_of_entrylane = (starting_point_of_entry_lane[0] - radius * (fillet_radius / 100) * np.sin(heading_of_crosssection[crosssection_index]), starting_point_of_entry_lane[1] + (radius * (fillet_radius / 100)) * np.cos(heading_of_crosssection[crosssection_index]))
                        
                    circle_entry_lane = [center_of_circle_of_entrylane[0], center_of_circle_of_entrylane[1], radius * (fillet_radius / 100) + (lane_index + 1) * lane_width] # Circle describe by the entry access
                        
                    main_circle = [origin_x0, origin_y0, radius]
                        
                    (x_position_of_intersection,y_position_of_intersection) = Intersection_Circle(circle_entry_lane,main_circle)[1]

                    minimum_distance = dist(alternate_lane[0][0],(x_position_of_intersection,y_position_of_intersection))
                    index_value_of_closest_point = 0
                    for n in range(len(alternate_lane[0])):
                        if dist(alternate_lane[0][n],(x_position_of_intersection,y_position_of_intersection)) < minimum_distance:
                            minimum_distance = dist(alternate_lane[0][n],(x_position_of_intersection,y_position_of_intersection))
                            index_value_of_closest_point = n

                    #Here we find out the three points defining the stopline

                    (x_positon_first_point_of_stopline, y_position_first_point_of_stopline) = alternate_lane[0][index_value_of_closest_point+3]
                    
                    (x_position_second_point_of_stopline, y_position_second_point_of_stopline) = alternate_lane[0][index_value_of_closest_point]
                       
                    (x_position_third_point_of_stopline,y_position_third_point_of_stopline)= (((x_positon_first_point_of_stopline+x_position_second_point_of_stopline)/2),((y_position_first_point_of_stopline+y_position_second_point_of_stopline)/2))
                    
                    self.stopline.append((x_positon_first_point_of_stopline,y_position_first_point_of_stopline,x_position_second_point_of_stopline,y_position_second_point_of_stopline,x_position_third_point_of_stopline,y_position_third_point_of_stopline,number_of_lanes,number_of_exit_lanes,lane_width))
                    counter +=1



##This a representation of a roundabout cross section.
class ExitLane(Road):

    ##The constructor
    #@param self The object pointer.
    #@param id A string. Unique id
    #@param x0 A float. The x coordinate of the center of the endpoint of the exit lane.
    #@param y0 A float. The y coordinate of the center of the endpoint of the exit lane.
    #@param r A float. Distance from the center of the roundabout to the center lane.
    #@param lw A float. The lane width
    #@param ch A Float. Heading of the road end relative to the heading of the roundabout.
    #@param nbr_of_lanes An integer. The number of lanes
    #@param SpeedL A float. The speed limit
    #@param RefS A float. The reference speed
    #@param cw List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base components are floats.
    def __init__(self, id, x0, y0, r, lw, ch, nbr_of_lanes, SpeedL, RefS, cw):

        # General Init

        Road.__init__(self, id)
        ##A float. The speed limit
        self.SpeedLimit = SpeedL
        ##A float. The reference speed
        self.RefSpeed = RefS
        ##A float. The defined speed
        self.DefinedSpeed = self.SpeedProfil[4]
        r += lw
        ##A float. The x coordinate of the center of the endpoint of the exit lane.
        self.x = x0
        ##A float. The y coordinate of the center of the endpoint of the exit lane.
        self.y = y0
        ##A float. Distance from the center of the roundabout to the center lane.
        self.r = r
        ##A Float. Heading of the road end relative to the heading of the roundabout.
        self.ch = ch
        ##A float. The lane width
        self.lw = lw
        ##List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base components are floats.
        self.crosswalk = cw

        # Get exit lanes

        # For edges
        (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, lw)
        self.e1.append(Bend(x, y, h, a, rc))
        (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, -lw)
        self.e2.append(Bend(x, y, h, a, rc))

        # For lanes
        (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, lw/2)
        self.l.append(Bend(x, y, h, a, rc))
        (x, y, h, a, rc) = self.get_exit_lane(x0, y0, lw, r, ch, -lw/2)
        self.l.append(Bend(x, y, h, a, rc))

    ##This method returns the starting coordinates of the road's center path. 
    #
    #Returns (Float, Float)
    #@param self The object pointer
    def getstart(self):
        return (self.x, self.y)

    ##This method returns the last coordinates of the road's center path.
    #
    #Returns (Float, Float)
    #@param self The object pointer
    def getend(self):
        return (self.x + (self.r + 2 * self.lw) * np.cos(self.ch),
                self.y + (self.r + 2 * self.lw) * np.sin(self.ch))

    ##This method returns the parameters needed to create the exit lane with a Bend object
    #@param self The object pointer
    #@param self x0 A float. The x coordinate of the center of the endpoint of the exit lane.
    #@param self y0 A float. The y coordinate of the center of the endpoint of the exit lane.
    #@param self lw A float. The total lane's width
    #@param self r A float. Distance from the center of the roundabout to the center lane.
    #@param self ch A float. Heading of the road end relative to the heading of the roundabout.
    #@param self ld a float. The curent lane's width
    def get_exit_lane(self, x0, y0, lw, r, ch, ld):
        sign = np.sign(ld)
        ld = abs(ld)

        x1 = x0 + (r + lw + 3.5) * np.cos(ch)
        y1 = y0 + (r + lw + 3.5) * np.sin(ch)

        x2 = x1 + ld * np.cos(ch - sign * np.pi / 2)
        y2 = y1 + ld * np.sin(ch - sign * np.pi / 2)

        xc1 = x0 + (r - lw + ld) * np.cos(ch - sign * np.pi / 8)
        yc1 = y0 + (r - lw + ld) * np.sin(ch - sign * np.pi / 8)

        rc = radius_of_circle((x2, y2), (xc1, yc1), np.pi/3)

        p1 = (xc1, yc1)
        p2 = (x2, y2)

        if(sign > 0):
            cc1 = circles_from_p1p2r(p1, p2, rc)
        else:
            cc1 = circles_from_p1p2r(p2, p1, rc)

        (x, y) = cc1
        h = np.arctan2(y - y2, x - x2) - sign * np.pi / 2
        return (x2, y2, h, sign * np.pi / 3, rc)


##This a representation of a straight road in Prescan.
class StraightRoad(Road):

    ##The constructor
    #@param self The object pointer.
    #@param id A string. Unique id
    #@param x0 A float. The x coordinate of the center of the start of the road segment.
    #@param y0 A float. The y coordinate of the center of the start of the road segment.
    #@param h A float. Global heading of the road segment at the start point.
    #@param l A float. Length of the road segment
    #@param lw A float. The lane width
    #@param nbr_of_lanes An integer. The number of lanes
    #@param lanes_going_OUT An integer. The number of lanes at the end of the road.
    #@param SpeedL A float. The speed limit
    #@param RefS A float. The reference speed
    #@param Stl List of lists contening relevant points (3 points per list) describing a stopline. Base components are floats.
    #@param cw List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base components are floats.
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes, lanes_going_OUT, SpeedL, RefS, Stl, cw):

        # General Init

        Road.__init__(self, id)
        ##A float. The speed limit
        self.SpeedLimit = SpeedL
        ##A float. The reference speed
        self.RefSpeed = RefS
        ##List of lists contening relevant points (3 points per list) describing a stopline. Base components are floats.
        self.stopline = Stl
        ##List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base components are floats.
        self.crosswalk = cw
        ##A float. Represents the speed that the road has per default (defined by the speedprofile in the Road Class)
        self.DefinedSpeed = self.SpeedProfil[0]

        # Edges, Center Line and Lanes

        self.c.append(Straight( x0, y0, h, l))

        self.e1.append(Straight( x0 - (nbr_of_lanes/2)*lw * np.cos(h + np.pi / 2),
                                y0 - (nbr_of_lanes/2) * lw * np.sin(h + np.pi / 2), h, l))

        self.e2.append(Straight( x0 + (nbr_of_lanes/2)*lw * np.cos(h + np.pi / 2),
                                y0 + lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2), h, l))

        lwi = (nbr_of_lanes -1) * lw/2
        for _ in range(nbr_of_lanes):
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l))
            lwi -= lw

        #This changes the direction of the lanes that drive backwards
        if nbr_of_lanes-lanes_going_OUT>0:
            for i in range(nbr_of_lanes-lanes_going_OUT):
                l=[]
                for (x, y) in self.l[i]:
                    l.append([x, y])
                l = l[::-1]
                self.l[i] = l

##This a representation of a crosswalk road in Prescan.
class Crosswalkr(Road):

    ##The constructor
    #@param self The object pointer.
    #@param id A string. Unique id
    #@param x0 A float. The x coordinate of the center of the start of the road segment.
    #@param y0 A float. The y coordinate of the center of the start of the road segment.
    #@param h A float. Global heading of the road segment at the start point.
    #@param l A float. Length of the road segment
    #@param lw A float. The lane width
    #@param nbr_of_lanes An integer. The number of lanes
    #@param lanes_going_OUT An integer. The number of lanes leaving the crosswalk
    #@param SpeedL A float. The speed limit
    #@param RefS A float. The reference speed
    #@param Stl List of lists contening relevant points (3 points per list) describing a stopline
    #@param cw List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base componemts are floats.
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes, lanes_going_OUT, SpeedL, RefS, cw):

        # General Init

        Road.__init__(self, id)
        ##A float. The speed limit
        self.SpeedLimit = SpeedL
        ##A float. The reference speed
        self.RefSpeed = RefS
        ##List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base components are floats.
        self.crosswalk = cw
        ##A float. Represents the speed that the road has per default (defined by the speedprofile in the Road Class)
        self.DefinedSpeed = self.SpeedProfil[0]

        # Edges, Center Line and Lanes

        self.c.append(Straight( x0, y0, h, l))

        self.e1.append(Straight( x0 - (nbr_of_lanes/2)*lw * np.cos(h + np.pi / 2),
                                y0 - (nbr_of_lanes/2) * lw * np.sin(h + np.pi / 2), h, l))

        self.e2.append(Straight( x0 + (nbr_of_lanes/2)*lw * np.cos(h + np.pi / 2),
                                y0 + lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2), h, l))

        lwi = (nbr_of_lanes -1) * lw/2
        for _ in range(nbr_of_lanes):
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l))
            lwi -= lw

        #This changes the direction of the lanes that drive backwards
        if nbr_of_lanes-lanes_going_OUT>0:
            for i in range(nbr_of_lanes-lanes_going_OUT):
                l=[]
                for (x, y) in self.l[i]:
                    l.append([x, y])
                l = l[::-1]
                self.l[i] = l

##This a representation of an adapter road in Prescan.
class AdapterRoad(Road):

    ##The constructor
    #@param self The object pointer.
    #@param id A string. Unique id
    #@param x0 A float. The x coordinate of the center of the start of the road segment.
    #@param y0 A float. The y coordinate of the center of the start of the road segment.
    #@param h A float. Global heading of the road segment at the start point.
    #@param l A float. Length of the road segment
    #@param lw A float. The lane width
    #@param nbr_of_lanes_start An integer. The number of lanes at the start
    #@param nbr_of_lanes_end An integer. The number of lanes at the end
    #@param lanes_in_x_dir_start An integer.
    #@param lanes_in_x_dir_end An integer.
    #@param SpeedL A float. The speed limit
    #@param RefS A float. The reference speed
    #@param Stl List of lists contening relevant points (3 points per list) describing a stopline
    #@param cw List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base components are floats.
    #@param lane_offset An integer. Represents the lane offset of the adapter (>0 if we remove lanes, <0 if we add lanes)
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes_start, nbr_of_lanes_end, lanes_in_x_dir_start, lanes_in_x_dir_end, SpeedL, RefS, Stl, cw, lane_offset):

        # General Init

        Road.__init__(self, id)
        ##A float. The speed limit
        self.SpeedLimit = SpeedL
        ##A float. The reference speed
        self.RefSpeed = RefS
        ##List of lists contening relevant points (3 points per list) describing a stopline
        self.stopline = Stl
        ##List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base componemts are floats.
        self.crosswalk = cw
        ##A float. Represents the speed that the road has by default (defined by the speedprofile in the Road Class)
        self.DefinedSpeed = self.SpeedProfil[5]

        # Edges, Center Line and Lanes

        self.c.append(Straight( x0, y0, h, l))

        self.e1.append(Straight( x0 + lw * (nbr_of_lanes_start/2)* np.cos(h + np.pi / 2),
                                y0 + lw * (nbr_of_lanes_start/2)* np.sin(h + np.pi / 2), h, l))

        self.e2.append(Straight( x0 - lw * (nbr_of_lanes_start/2)* np.cos(h + np.pi / 2),
                                y0 - lw * (nbr_of_lanes_start/2)* np.sin(h + np.pi / 2), h, l/2))

        difference = abs(nbr_of_lanes_start - nbr_of_lanes_end)
        lo_right = abs(lane_offset)
        lo_left = abs(difference - lo_right)

        if nbr_of_lanes_start%2 == 0 : #if there is an odd number of lanes, then x0 and y0 are on the center of a lane
            offset_center = 0
        else :
            offset_center = 0.5

        if nbr_of_lanes_start>nbr_of_lanes_end:  # If we remove lanes


            self.e1.append(Straight( x0 - lw*(nbr_of_lanes_start/2)*np.sin(h),
                                    y0 + lw*(nbr_of_lanes_start/2)*np.cos(h), h, l/2))

            self.e1.append(Straight( x0 + (l/2)*np.cos(h) - lw*(offset_center-lo_left+nbr_of_lanes_end)*np.sin(h),
                                    y0 + (l/2)*np.sin(h) + lw*(offset_center-lo_left+nbr_of_lanes_end)*np.cos(h), h, l/2))

            self.e2.append(Straight( x0 + lw*(nbr_of_lanes_start/2)*np.sin(h),
                                    y0 - lw*(nbr_of_lanes_start/2)*np.cos(h), h, l/2))

            self.e2.append(Straight( x0 + (l/2)*np.cos(h) + lw*(offset_center-lo_left)*np.sin(h),
                                    y0 + (l/2)*np.sin(h) - lw*(offset_center-lo_left)*np.cos(h), h, l/2))


            lanes_before=[]
            lanes_after=[]
            counter_s = nbr_of_lanes_start -1

            # here we create the lanes juste before the change

            while counter_s > -1 :
                lane = Straight( x0 + lw*(nbr_of_lanes_start/2 -0.5 - counter_s)*np.sin(h),
                                y0 - lw*(nbr_of_lanes_start/2 -0.5 - counter_s)*np.cos(h), h, 3)
                laneBis = []
                for (x,y) in lane :
                    laneBis.append([x,y])

                lanes_before.append(laneBis)
                counter_s -= 1


            # now we reverse the lanes driving backwards
            for k in range (nbr_of_lanes_start-lanes_in_x_dir_start) :
                lanes_before[k]=lanes_before[k][::-1]


            # then we create the lanes just after the change

            counter = 0

            while counter < nbr_of_lanes_end :
                lane = Straight( x0 + (l-3)*np.cos(h) - lw*(nbr_of_lanes_start/2 -0.5 -counter-lo_left)*np.sin(h),
                                y0 + (l-3)*np.sin(h) + lw*(nbr_of_lanes_start/2 -0.5 -counter-lo_left)*np.cos(h), h, 3)
                counter += 1

                laneBis = []
                for (x,y) in lane :
                    laneBis.append([x,y])

                lanes_after.append(laneBis)

            # now we reverse the lanes driving backwards

            for k in range (nbr_of_lanes_end-lanes_in_x_dir_end) :
                lanes_after[k]=lanes_after[k][::-1]




        elif nbr_of_lanes_start<nbr_of_lanes_end:   # Same if we add a lane

            self.e1.append(Straight( x0 - lw*(nbr_of_lanes_start/2)*np.sin(h),
                                    y0 + lw*(nbr_of_lanes_start/2)*np.cos(h), h, l/2))

            self.e1.append(Straight( x0 + (l/2)*np.cos(h) - lw*(-offset_center-lo_right-1+nbr_of_lanes_end)*np.sin(h),
                                    y0 + (l/2)*np.sin(h) + lw*(-offset_center-lo_right-1+nbr_of_lanes_end)*np.cos(h), h, l/2))

            self.e2.append(Straight( x0 + lw*(nbr_of_lanes_start/2)*np.sin(h),
                                    y0 - lw*(nbr_of_lanes_start/2)*np.cos(h), h, l/2))

            self.e2.append(Straight( x0 + (l/2)*np.cos(h) + lw*(-offset_center+lo_right-1)*np.sin(h),
                                    y0 + (l/2)*np.sin(h) - lw*(-offset_center+lo_right-1)*np.cos(h), h, l/2))


            lanes_before=[]
            lanes_after=[]
            counter_s = nbr_of_lanes_start -1

            # here we create the lanes juste before the change

            while counter_s > -1 :
                lane = Straight( x0 + lw*(nbr_of_lanes_start/2 -0.5 - counter_s)*np.sin(h),
                                y0 - lw*(nbr_of_lanes_start/2 -0.5 - counter_s)*np.cos(h), h, 3)
                laneBis = []
                for (x,y) in lane :
                    laneBis.append([x,y])

                lanes_before.append(laneBis)
                counter_s -= 1


            # now we reverse the lanes driving backwards

            for k in range (nbr_of_lanes_start - lanes_in_x_dir_start) :
                lanes_before[k]=lanes_before[k][::-1]


            # then we create the lanes just after the change

            counter = 0

            while counter < nbr_of_lanes_end :
                lane = Straight( x0 + (l-3)*np.cos(h) - lw*(nbr_of_lanes_start/2 -0.5 -counter+lo_left)*np.sin(h),
                                y0 + (l-3)*np.sin(h) + lw*(nbr_of_lanes_start/2 -0.5 -counter+lo_left)*np.cos(h), h, 3)
                counter += 1

                laneBis = []
                for (x,y) in lane :
                    laneBis.append([x,y])

                lanes_after.append(laneBis)

            # now we reverse the lanes driving backwards
            for k in range (nbr_of_lanes_end-lanes_in_x_dir_end) :
                lanes_after[k]=lanes_after[k][::-1]

        else : #if there are the same number of lanes before and after the adapter road
            self.e1.append(Straight( x0 - lw*(nbr_of_lanes_start/2)*np.sin(h),
                                    y0 + lw*(nbr_of_lanes_start/2)*np.cos(h), h, l))
            self.e2.append(Straight( x0 + lw*(nbr_of_lanes_start/2)*np.sin(h),
                                    y0 - lw*(nbr_of_lanes_start/2)*np.cos(h), h, l))

            lanes_total=[]
            counter_s = nbr_of_lanes_start -1

            while counter_s > -1 :
                lane = Straight( x0 + lw*(nbr_of_lanes_start/2 -0.5 - counter_s)*np.sin(h),
                                y0 - lw*(nbr_of_lanes_start/2 -0.5 - counter_s)*np.cos(h), h, l)
                laneBis = []
                for (x,y) in lane :
                    laneBis.append([x,y])

                lanes_total.append(laneBis)
                counter_s -= 1

            for k in range (nbr_of_lanes_start - lanes_in_x_dir_start) :
                lanes_total[k]=lanes_total[k][::-1]

            for k in range (nbr_of_lanes_start):
                self.l.append(lanes_total[k])

            return None



        if len(lanes_before)>len(lanes_after) : # here we store data in lanes_max, lanes_min, lanes_max_x and lanes_min_x to use the same programm section if we add or remove a lane
            lanes_max = lanes_before
            lanes_min = lanes_after
            lanes_max_x = lanes_in_x_dir_start
            lanes_min_x = lanes_in_x_dir_end
        else :
            lanes_max = lanes_after
            lanes_min = lanes_before
            lanes_max_x = lanes_in_x_dir_end
            lanes_min_x = lanes_in_x_dir_start


        # First we connect the lanes in the x direction

        if (lanes_min_x) == 1 :

            (x2,y2) = (lanes_min[len(lanes_min)-lanes_min_x][3][0] , lanes_min[len(lanes_min)-lanes_min_x][3][1])
            (x4,y4) = (lanes_min[len(lanes_min)-lanes_min_x][0][0] , lanes_min[len(lanes_min)-lanes_min_x][0][1])

            for k in range (lanes_max_x):
                (x1,y1) = (lanes_max[len(lanes_max)-k-1][3][0] , lanes_max[len(lanes_max)-k-1][3][1])
                (x3,y3) = Intersection_Lines(lanes_min[len(lanes_min)-lanes_min_x],lanes_max[len(lanes_max)-k-1])
                (x5,y5) = (lanes_max[len(lanes_max)-k-1][0][0] , lanes_max[len(lanes_max)-k-1][0][1])

                if len(lanes_before)>len(lanes_after) :
                    xs1 = [x5, x1, x1, x3]
                    ys1 = [y5, y1, y1, y3]
                    xs2 = [x3, x4, x4, x2]
                    ys2 = [y3, y4, y4, y2]

                else :
                    xs1 = [x4, x2, x2, x3]
                    ys1 = [y4, y2, y2, y3]
                    xs2 = [x3, x5, x5, x1]
                    ys2 = [y3, y5, y5, y1]

                # we create 2 curves to have a smoother shape (a S shape) : x2,x4 and x3 forms (for example) the first curve of the S, and x1,x5 and x3 the second one
                l1 = Curve(xs1, ys1, 0)
                l2 = Curve(xs2, ys2, 0)
                Current_Lane1 = []
                counter_addLine = -1
                for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                    if counter_addLine>-1 :
                        if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    else :
                        Current_Lane1.append([x, y])
                        counter_addLine+=1
                self.l.append(Current_Lane1)

                Current_Lane1 = []
                counter_addLine = -1
                for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                    if counter_addLine>-1 :
                        if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    else :
                        Current_Lane1.append([x, y])
                        counter_addLine+=1
                self.l.append(Current_Lane1)


        else :
            # For example (with a road going only in the x direction)
            #
            #_______________
            #       1            ______________
            #       2                 I
            #       3                 II
            #       4                 III
            #       5            ______________
            #_______________
            #
            # We connect 1 and 2 to I, 3 to II and 4 and 5 to III


            a =np.tan(h)
            k = 0
            i = 0
            if lanes_min_x < lanes_max_x :
                while (k < lanes_max_x) and (i<lanes_min_x-1): # for example, we connect 1,2 and 3 to I and II. When it will inly remain III, we will connect to it the remaining lanes
                    (x4,y4) = (lanes_min[len(lanes_min)-lanes_min_x+i][0][0] , lanes_min[len(lanes_min)-lanes_min_x+i][0][1])
                    (x2,y2) = (lanes_min[len(lanes_min)-lanes_min_x+i][3][0] , lanes_min[len(lanes_min)-lanes_min_x+i][3][1])

                    (x1,y1) = (lanes_max[len(lanes_max)-lanes_max_x + k][3][0] , lanes_max[len(lanes_max)-lanes_max_x + k][3][1])
                    (x5,y5) = (lanes_max[len(lanes_max)-lanes_max_x + k][0][0] , lanes_max[len(lanes_max)-lanes_max_x + k][0][1])

                    (x3,y3) = Intersection_Lines(lanes_min[len(lanes_min)-lanes_min_x+i],lanes_max[len(lanes_max)-lanes_max_x + k])

                    b = y1 - a*x1 # here we find the straight line equation of the lane going through (x1,y1) with an angle of h
                    y2bis = a*x2 + b  # if (x2,y2) is on the same lane than (x1,y1) (ie if the 2 lanes are in front of each other), then y2bis = y2

                    if round(y2,2) == round(y2bis,2): # if the 2 lanes are in front of each other, then i = i+1
                        i+=1


                    if len(lanes_before)>len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]


                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    k +=1
                (x4,y4) = (lanes_min[len(lanes_min)-lanes_min_x+i][0][0] , lanes_min[len(lanes_min)-lanes_min_x+i][0][1])
                (x2,y2) = (lanes_min[len(lanes_min)-lanes_min_x+i][3][0] , lanes_min[len(lanes_min)-lanes_min_x+i][3][1])
                while k<lanes_max_x :
                    (x1,y1) = (lanes_max[len(lanes_max)-lanes_max_x + k][3][0] , lanes_max[len(lanes_max)-lanes_max_x + k][3][1])
                    (x5,y5) = (lanes_max[len(lanes_max)-lanes_max_x + k][0][0] , lanes_max[len(lanes_max)-lanes_max_x + k][0][1])

                    (x3,y3) = Intersection_Lines(lanes_min[len(lanes_min)-lanes_min_x+i],lanes_max[len(lanes_max)-lanes_max_x + k])

                    if len(lanes_before)>len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]


                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    k +=1
            elif lanes_min_x > lanes_max_x :
                # This happens for example in this case :
                #
                #________________ __________________
                # 1 ->             I  ->
                # 2 <-             II ->
                # 3 <-             III <-
                # 4 <-             _________________
                #_________________
                #
                # here we globally remove lanes (there are less lanes after than before) but we add lanes in the x direction
                #
                while (k < lanes_max_x-1) and (i<lanes_min_x):
                    (x4,y4) = (lanes_min[len(lanes_min)-lanes_min_x+i][0][0] , lanes_min[len(lanes_min)-lanes_min_x+i][0][1])
                    (x2,y2) = (lanes_min[len(lanes_min)-lanes_min_x+i][3][0] , lanes_min[len(lanes_min)-lanes_min_x+i][3][1])

                    (x1,y1) = (lanes_max[len(lanes_max)-lanes_max_x + k][3][0] , lanes_max[len(lanes_max)-lanes_max_x + k][3][1])
                    (x5,y5) = (lanes_max[len(lanes_max)-lanes_max_x + k][0][0] , lanes_max[len(lanes_max)-lanes_max_x + k][0][1])

                    (x3,y3) = Intersection_Lines(lanes_min[len(lanes_min)-lanes_min_x+i],lanes_max[len(lanes_max)-lanes_max_x + k])

                    b = y1 - a*x1 # here we find the straight line equation of the lane going through (x1,y1) with an angle of h
                    y2bis = a*x2 + b  # if (x2,y2) is on the same lane than (x1,y1) (ie if the 2 lanes are in front of each other), then y2bis = y2

                    if round(y2,2) == round(y2bis,2): # if the 2 lanes are in front of each other, then i = i+1
                        i+=1


                    if len(lanes_before)>len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]


                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    k +=1

                (x1,y1) = (lanes_max[len(lanes_max)-lanes_max_x + k][3][0] , lanes_max[len(lanes_max)-lanes_max_x + k][3][1])
                (x5,y5) = (lanes_max[len(lanes_max)-lanes_max_x + k][0][0] , lanes_max[len(lanes_max)-lanes_max_x + k][0][1])
                while i<lanes_min_x :

                    (x4,y4) = (lanes_min[len(lanes_min)-lanes_min_x+i][0][0] , lanes_min[len(lanes_min)-lanes_min_x+i][0][1])
                    (x2,y2) = (lanes_min[len(lanes_min)-lanes_min_x+i][3][0] , lanes_min[len(lanes_min)-lanes_min_x+i][3][1])

                    (x3,y3) = Intersection_Lines(lanes_min[len(lanes_min)-lanes_min_x+i],lanes_max[len(lanes_max)-lanes_max_x + k])

                    if len(lanes_before)>len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]


                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    i +=1
            else :
                while (k < lanes_max_x):
                    (x4,y4) = (lanes_min[len(lanes_min)-lanes_min_x+k][0][0] , lanes_min[len(lanes_min)-lanes_min_x+k][0][1])
                    (x2,y2) = (lanes_min[len(lanes_min)-lanes_min_x+k][3][0] , lanes_min[len(lanes_min)-lanes_min_x+k][3][1])

                    (x1,y1) = (lanes_max[len(lanes_max)-lanes_max_x + k][3][0] , lanes_max[len(lanes_max)-lanes_max_x + k][3][1])
                    (x5,y5) = (lanes_max[len(lanes_max)-lanes_max_x + k][0][0] , lanes_max[len(lanes_max)-lanes_max_x + k][0][1])

                    (x3,y3) = Intersection_Lines(lanes_min[len(lanes_min)-lanes_min_x+k],lanes_max[len(lanes_max)-lanes_max_x + k])

                    if len(lanes_before)>len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]


                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    k +=1



        # Now we connect the lanes going in the opposite x direction (same as the x direction but we reverse everything)
        if (len(lanes_min) - lanes_min_x)== 1 :
            (x2,y2) = (lanes_min[0][3][0] , lanes_min[0][3][1])
            (x4,y4) = (lanes_min[0][0][0] , lanes_min[0][0][1])
            for k in range (len(lanes_max) - lanes_max_x):
                (x1,y1) = (lanes_max[k][3][0] , lanes_max[k][3][1])
                (x5,y5) = (lanes_max[k][0][0] , lanes_max[k][0][1])
                (x3,y3) = Intersection_Lines(lanes_min[0],lanes_max[k])

                if len(lanes_before)<len(lanes_after) :
                    xs1 = [x5, x1, x1, x3]
                    ys1 = [y5, y1, y1, y3]
                    xs2 = [x3, x4, x4, x2]
                    ys2 = [y3, y4, y4, y2]

                else :
                    xs1 = [x4, x2, x2, x3]
                    ys1 = [y4, y2, y2, y3]
                    xs2 = [x3, x5, x5, x1]
                    ys2 = [y3, y5, y5, y1]

                l1 = Curve(xs1, ys1, 0)
                l2 = Curve(xs2, ys2, 0)
                Current_Lane1 = []
                counter_addLine = -1
                for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                    if counter_addLine>-1 :
                        if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    else :
                        Current_Lane1.append([x, y])
                        counter_addLine+=1
                self.l.append(Current_Lane1)

                Current_Lane1 = []
                counter_addLine = -1
                for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                    if counter_addLine>-1 :
                        if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    else :
                        Current_Lane1.append([x, y])
                        counter_addLine+=1
                self.l.append(Current_Lane1)


        else :
            a =np.tan(h)
            k = len(lanes_max) - lanes_max_x-1
            i = len(lanes_min) - lanes_min_x-1
            if i < k :
                while (k >-1) and (i>0):
                    (x2,y2) = (lanes_min[i][3][0] , lanes_min[i][3][1])
                    (x4,y4) = (lanes_min[i][0][0] , lanes_min[i][0][1])

                    (x1,y1) = (lanes_max[k][3][0] , lanes_max[k][3][1])
                    (x5,y5) = (lanes_max[k][0][0] , lanes_max[k][0][1])

                    (x3,y3) = Intersection_Lines(lanes_min[i],lanes_max[k])

                    b = y1 - a*x1
                    y2bis = a*x2 + b

                    if round(y2,4) == round(y2bis,4): # if the 2 lanes are in front of each other, then i = i-1
                        i-=1


                    if len(lanes_before)<len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]

                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    k -=1

                (x2,y2) = (lanes_min[i][3][0] , lanes_min[i][3][1])
                (x4,y4) = (lanes_min[i][0][0] , lanes_min[i][0][1])

                while k >-1:
                    (x1,y1) = (lanes_max[k][3][0] , lanes_max[k][3][1])
                    (x5,y5) = (lanes_max[k][0][0] , lanes_max[k][0][1])

                    (x3,y3) = Intersection_Lines(lanes_min[i],lanes_max[k])


                    if len(lanes_before)<len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]

                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    k -=1

            elif i > k :
                while (k >0) and (i>-1):
                    (x2,y2) = (lanes_min[i][3][0] , lanes_min[i][3][1])
                    (x4,y4) = (lanes_min[i][0][0] , lanes_min[i][0][1])

                    (x1,y1) = (lanes_max[k][3][0] , lanes_max[k][3][1])
                    (x5,y5) = (lanes_max[k][0][0] , lanes_max[k][0][1])

                    (x3,y3) = Intersection_Lines(lanes_min[i],lanes_max[k])

                    b = y1 - a*x1
                    y2bis = a*x2 + b

                    if round(y2,4) == round(y2bis,4): # if the 2 lanes are in front of each other, then i = i+1
                        i-=1


                    if len(lanes_before)<len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]

                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    k -=1

                (x1,y1) = (lanes_max[k][3][0] , lanes_max[k][3][1])
                (x5,y5) = (lanes_max[k][0][0] , lanes_max[k][0][1])

                while i >-1:

                    (x2,y2) = (lanes_min[i][3][0] , lanes_min[i][3][1])
                    (x4,y4) = (lanes_min[i][0][0] , lanes_min[i][0][1])

                    (x3,y3) = Intersection_Lines(lanes_min[i],lanes_max[k])


                    if len(lanes_before)<len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]

                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    i -=1
            else :
                while k> -1 :
                    (x2,y2) = (lanes_min[k][3][0] , lanes_min[k][3][1])
                    (x4,y4) = (lanes_min[k][0][0] , lanes_min[k][0][1])

                    (x1,y1) = (lanes_max[k][3][0] , lanes_max[k][3][1])
                    (x5,y5) = (lanes_max[k][0][0] , lanes_max[k][0][1])

                    (x3,y3) = Intersection_Lines(lanes_min[k],lanes_max[k])

                    if len(lanes_before)<len(lanes_after) :
                        xs1 = [x5, x1, x1, x3]
                        ys1 = [y5, y1, y1, y3]
                        xs2 = [x3, x4, x4, x2]
                        ys2 = [y3, y4, y4, y2]

                    else :
                        xs1 = [x4, x2, x2, x3]
                        ys1 = [y4, y2, y2, y3]
                        xs2 = [x3, x5, x5, x1]
                        ys2 = [y3, y5, y5, y1]

                    l1 = Curve(xs1, ys1, 0)
                    l2 = Curve(xs2, ys2, 0)
                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)

                    Current_Lane1 = []
                    counter_addLine = -1
                    for (x,y) in l2: #we add the new lane but we check in the same time that 2 points aren't the same
                        if counter_addLine>-1 :
                            if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        else :
                            Current_Lane1.append([x, y])
                            counter_addLine+=1
                    self.l.append(Current_Lane1)
                    k -=1


##This a representation of an entry road in Prescan.
class EntryRoad(Road):

    ##The constructor
    #@param self The object pointer.
    #@param id A string. Unique id
    #@param x0 A float. The x coordinate of the center of the start of the road segment.
    #@param y0 A float. The y coordinate of the center of the start of the road segment.
    #@param h A float. Global heading of the road segment at the start point.
    #@param l A float. Length of the road segment
    #@param lw A float. The lane width
    #@param nbr_of_lanes An integer. The number of lanes.
    #@param lanes_going_OUT An integer. The number of lanes after the entry.
    #@param entry_road_angle A float. The angle of the entry lane.
    #@param apron_length A float. The lemgth of the apron.
    #@param side_road_length A float. Th length of the side road.
    #@param SpeedL A float. The speed limit.
    #@param RefS A float. The reference speed.
    #@param Stl List of lists contening relevant points (3 points per list) describing a stopline. Base components are floats.
    #@param cw List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base components are floats.
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes, lanes_going_OUT, entry_road_angle, apron_length, side_road_length, SpeedL, RefS, Stl, cw):

        # General Init

        Road.__init__(self, id)
        ##A float. The speed limit
        self.SpeedLimit = SpeedL
        ##A float. The reference speed
        self.RefSpeed = RefS
        ##List of lists contening relevant points (3 points per list) describing a stopline. Base components are floats.
        self.stopline = Stl
        ##List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base components are floats.
        self.crosswalk = cw
        ##A float. Represents the speed that the road has per default (defined by the speedprofile in the Road Class)
        self.DefinedSpeed = self.SpeedProfil[6]
        apron_length2=(apron_length*np.tan(entry_road_angle)+lw/2)/(np.tan(entry_road_angle))

        # Edges, Center Line and Lanes

        self.c.append(Straight( x0, y0, h, l))

        self.e1.append(Straight( x0 + lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2),
                                y0 + lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2), h, l))

        self.e2.append(Straight( x0 - lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2)+ (l-apron_length2) * np.cos(h),
                                y0 - lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2)+ (l-apron_length2) * np.sin(h), h-entry_road_angle, apron_length2))    # Entry part of edge 2

        self.e2.append(Straight( x0 - lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2),
                                y0 - lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2), h-entry_road_angle,l-apron_length2 ))  # Strainght part of edge 2

            # We are creating here every straight lanes that are not influenced by the new entry portion
            #
            #              _______________________  e1
            #              <---------------------
            #              <---------------------
            #              --------------------->
            #              --------------------->
            #
            #                     ________________  e2
            #                 __ /
            #              _/

        lwi=(nbr_of_lanes -1) * lw/2
        for _ in range(nbr_of_lanes-1):
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l))
            lwi -= lw



        # And after that we can create the last lane, which is the entry lane
        #
        #              ___________________________  e1
        #              <--------------------------
        #              <--------------------------
        #              -------------------------->
        #              -------------------------->
        #              --(1)-----------(2)------->
        #                 -- / ____________________  e2
        #           (3) -/ __ /
        #              ___/

        self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                y0 + lwi * np.sin(h + np.pi / 2),
                                h, apron_length2))              # Here we create (1)
        self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) + apron_length2 * np.cos(h),
                                y0 + lwi * np.sin(h + np.pi / 2) + apron_length2 * np.sin(h),
                                h, l-apron_length2))   # Then (2)

        self.l.append(Straight( x0 + (apron_length*np.tan(entry_road_angle)-lwi+lw/2)*np.sin(h),
                                y0 - (apron_length*np.tan(entry_road_angle)-lwi+lw/2)*np.cos(h),   # And finally (3)
                                entry_road_angle+h, (apron_length*np.tan(entry_road_angle)+lw/2)/np.sin(entry_road_angle)))

        #This changes the direction of the lanes that drive backwards
        if nbr_of_lanes-lanes_going_OUT>0:
            for i in range(nbr_of_lanes-lanes_going_OUT):
                l=[]
                for (x, y) in self.l[i]:
                    l.append([x, y])
                l = l[::-1]
                self.l[i] = l

##This a representation of an exit road in Prescan.
class ExitRoad(Road):

    ##The constructor
    #@param self The object pointer.
    #@param id A string. Unique id
    #@param x0 A float. The x coordinate of the center of the start of the road segment.
    #@param y0 A float. The y coordinate of the center of the start of the road segment.
    #@param h A float. Global heading of the road segment at the start point.
    #@param l A float. Length of the road segment
    #@param lw A float. The lane width
    #@param nbr_of_lanes An integer. The number of lanes
    #@param lanes_going_OUT An integer. The number of lanes after the exit road
    #@param exit_road_angle A float. The angle of the exit road
    #@param apron_length A float. The length of the apron road
    #@param side_road_length A float. The length of the side road.
    #@param SpeedL A float. The speed limit
    #@param RefS A float. The reference speed
    #@param Stl List of lists contening relevant points (3 points per list) describing a stopline
    #@param cw List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base componemts are floats.
    def __init__(self, id, x0, y0, h, l, lw, nbr_of_lanes, lanes_going_OUT, exit_road_angle, apron_length, side_road_length, SpeedL, RefS, Stl, cw):

        # General Init

        Road.__init__(self, id)
        ##A float. The speed limit
        self.SpeedLimit = SpeedL
        ##A float. The reference speed
        self.RefSpeed = RefS
        ##List of lists contening relevant points (3 points per list) describing a stopline. Base components are floats.
        self.stopline = Stl
        ##List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base components are floats.
        self.crosswalk = cw
        ##A float. Represents the speed that the road has per default (defined by the speedprofile in the Road Class)
        self.DefinedSpeed = self.SpeedProfil[7]
        apron_length2=(apron_length*np.tan(exit_road_angle)+lw/2)/(np.tan(exit_road_angle))

        # Edges, Center Line and Lanes

        self.c.append(Straight( x0, y0, h, l))

        self.e1.append(Straight( x0 + lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2),
                                y0 + lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2), h, l))

        self.e2.append(Straight( x0 - lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2),
                                y0 - lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2), h,apron_length2))   # Straight part of edge 2

        self.e2.append(Straight( x0 - lw * (nbr_of_lanes/2) * np.cos(h + np.pi / 2)+ (l-apron_length2) * np.cos(h),
                                y0 - lw * (nbr_of_lanes/2) * np.sin(h + np.pi / 2)+ (l-apron_length2) * np.sin(h), h-exit_road_angle,(l-apron_length2-1)*np.cos(h-exit_road_angle) ))    # Exit part of edge 2


        # We are creating here every straight lanes that are not influenced by the new exit portion
        #
        #              _______________________  e1
        #              <---------------------
        #              <---------------------
        #              --------------------->
        #              --------------------->
        #
        #              ________________
        #                              \__
        #                                 \___  e2


        lwi=(nbr_of_lanes -1) * lw/2
        for _ in range(nbr_of_lanes-1):
            self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                    y0 + lwi * np.sin(h + np.pi / 2),
                                    h, l))
            lwi -= lw


        # And after that we can create the last lane, which is the exit lane
        #
        #              _______________________  e1
        #              <---------------------
        #              <---------------------
        #              --------------------->
        #              --------------------->
        #              -----(1)-------------> (2)
        #              ________________  \ (3)
        #                              \__ -->
        #                                 \___  e2

        self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2),
                                y0 + lwi * np.sin(h + np.pi / 2),
                                h, l-apron_length2))        # We create (1) here
        self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) + (l-apron_length2) * np.cos(h),
                                y0 + lwi * np.sin(h + np.pi / 2) + (l-apron_length2) * np.sin(h),
                                h, apron_length2))    # Then (2)
        self.l.append(Straight( x0 + lwi * np.cos(h + np.pi / 2) + (l-apron_length2) * np.cos(h),
                                y0 + lwi * np.sin(h + np.pi / 2) + (l-apron_length2) * np.sin(h),
                                h-exit_road_angle, (apron_length*np.tan(exit_road_angle)+lw/2)/np.sin(exit_road_angle)))  # And finally (3)

        #This changes the direction of the lanes that drive backwards
        if nbr_of_lanes-lanes_going_OUT>0:
            for i in range(nbr_of_lanes-lanes_going_OUT):
                l=[]
                for (x, y) in self.l[i]:
                    l.append([x, y])
                l = l[::-1]
                self.l[i] = l


##This a representation of an xcrossing road in Prescan. Each road contains one segment for each arm of the xcrossing.
class XCrossRoad(Road):

 
    ##The constructor
    #@param self The object pointer.
    #@param id A string. Unique id
    #@param x0 A float. The x coordinate of the center of the start of the road segment.
    #@param y0 A float. The y coordinate of the center of the start of the road segment.
    #@param h A float. Global heading of the road segment at the start point.
    #@param r A float. Distance from the starting point to furthest center point of one of the lanes.
    #@param lw A float. The lane width
    #@param cs_h List (of floats) of headings for each arm of the xcrossing.
    #@param cs_len_till_stop A float. Distance from endpoint of the arms to the arms' stopline.
    #@param cs_nbr_of_lanes List (of integers) of the number of lane for each arm of the xcrossing.
    #@param cs_lanes_going_OUT List (of integers) representing the number of lines at every exit of the crossing
    #@param cs_l List (of floats) of road length for each arm of the xcrossing.
    #@param SpeedL A float. The speed limit
    #@param RefS A float. The reference speed
    #@param Stl List of lists contening relevant points (3 points per list) describing a stopline. Base components are floats.
    #@param cw List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base components are floats.

    def __init__(self, id, x0, y0, h, lw, cs_h, cs_len_till_stop, cs_nbr_of_lanes, cs_lanes_going_OUT, cs_l, SpeedL, RefS, Stl, cw):

        # General Init

        Road.__init__(self, id)
        ##A float. The speed limit
        self.SpeedLimit = SpeedL
        ##A float. The reference speed
        self.RefSpeed = RefS
        ##A float. The x coordinate of the center of the start of the road segment.
        self.x=x0
        ##A float. The x coordinate of the center of the start of the road segment.
        self.y=y0
        ##List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base components are floats.
        self.stopline = Stl
        ##A float. Represents the speed that the road has per default (defined by the speedprofilw in the Road Class)
        self.DefinedSpeed = self.SpeedProfil[8]
        ##List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base components are floats.
        self.crosswalk = cw

        # Lanes Creation

        # Creation of each "Starting Lane"

        counter = 0

        for c in range(4):  # For each Branch of the X Crossing


            nb_of_lanes = cs_nbr_of_lanes[c]
            lanes_going_OUT = cs_lanes_going_OUT[c]
            lwi=(cs_nbr_of_lanes[c] -1) * lw/2
            next_first_lane = counter             # Allow us the access to the first lane created that need to be reversed

            for lane in range(nb_of_lanes):

                l1 = Straight(x0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.cos(cs_h[c]+h) + (lwi)*np.cos(cs_h[c]+h+ np.pi / 2), y0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.sin(cs_h[c]+h) + (lwi)*np.sin(cs_h[c]+h+ np.pi / 2), cs_h[c]+h, (cs_len_till_stop[c]+1))

                Current_Lane = []  # This convert the lane from a path obj to a tab of point
                for (x,y) in l1:
                    Current_Lane.append([x, y])

                self.l.append(Current_Lane[1:])

                lwi -= lw
                counter += 1

            # We are creating here the straight part of the lane at the beginning of each crosssection from the stopline to
            # the beggining of the road in the following order (1 : a -> b then 2->3->4)
            #
            #                     #        #
            #                     #    2   #
            #                     #        #
            #                ######        #######
            #                             a) |---->
            #                   3               1
            #                             b)  ---->
            #                #######       ########
            #                      #       #
            #                      #   4   #
            #                      #       #
            #
            # We need now to change the direction of the lanes that drive backwards


            # Changing the direction of the lanes that drive backwards

            if nb_of_lanes-lanes_going_OUT>0:
                for j in range(nb_of_lanes-lanes_going_OUT):
                    l=[]
                    for (x, y) in self.l[next_first_lane + j]:
                        l.append([x, y])
                    l = l[::-1]
                    self.l[next_first_lane + j] = l



        # Creating every connections between each starting lanes

        # We will now link each crossections of the x crossing
        #
        #                     #      | #
        #                     #    2 | #
        #                     #      | #
        #                ######      | #######
        #                <----------------|----
        #                   3    |          1
        #                        |    b)  ---->
        #                ####### |     ########
        #                      # |     #
        #                      # | 4   #
        #                      # |     #
        #
        #
        # In order to understand the implentation of this next part, please read the comment AND the wiki dedicated to this RT


        total_nb_of_lanes = 0   # This will be usefull to create a counter that can circle back to the beggining of the lane list (see below)
        Number_of_lanes_going_IN = [] #lanes heading towards the center of the crossroad
        Index_lanes_going_out = []
        Index_lanes_going_in = []

        for i in range(4):
            Index_lanes_going_out_local = []
            Index_lanes_going_in_local = []
            nb_of_lanes = cs_nbr_of_lanes[i]
            lanes_going_OUT = cs_lanes_going_OUT[i]

            if lanes_going_OUT > 0 : # here we save the index in self.l of the lanes driving out of the crossroad
                if nb_of_lanes == lanes_going_OUT :
                    for k in range (nb_of_lanes):
                        Index_lanes_going_out_local.append(total_nb_of_lanes+k)
                else :
                    for k in range (lanes_going_OUT) :
                        Index_lanes_going_out_local.append(total_nb_of_lanes+k + (nb_of_lanes-lanes_going_OUT))

            for k in range (nb_of_lanes): # here we save the index in self.l of the lanes going in the crossroad
                if (k+total_nb_of_lanes) not in Index_lanes_going_out_local :
                    Index_lanes_going_in_local.append(k + total_nb_of_lanes)

            total_nb_of_lanes += nb_of_lanes

            Number_of_lanes_going_IN.append(nb_of_lanes - lanes_going_OUT)
            Index_lanes_going_in.append(Index_lanes_going_in_local)
            Index_lanes_going_out.append(Index_lanes_going_out_local)

        count_lanes_going_IN =0


        for m in range(4):  # For each Branch of the X Crossing
            if Number_of_lanes_going_IN[m] !=0 :  # if there are lanes going in the opposite x direction


                nb_of_lanes = cs_nbr_of_lanes[m]
                lanes_going_OUT = cs_lanes_going_OUT[m]
                counter_remaining_lanes = nb_of_lanes - lanes_going_OUT

                lanes_going_IN = []
                for k in range (len(Index_lanes_going_in[m])):
                    lanes_going_IN.append(self.l[Index_lanes_going_in[m][k]])  # Lanes going in the crossroad that we will link to the roads going out of the crossroad


                Lane_available_for_connection = []
                Lane_available_for_connection_right = []
                Lane_available_for_connection_left = []
                for p in range(4):
                    if p != m :
                        for k in range (len(Index_lanes_going_out[p])) :
                            Lane_available_for_connection.append(self.l[Index_lanes_going_out[p][k]])




                if Number_of_lanes_going_IN[m] == 1 :  # If we have only one lane going in the crossroad

                    for r in range(len(Lane_available_for_connection)): # We connect the Only Lane of interest to EVERY lane avaible for conections

                        (x1,y1) = lanes_going_IN[0][len(lanes_going_IN[0])-1]

                        (x2,y2) = Lane_available_for_connection[r][0]

                        (x3,y3) = Intersection_Lines(lanes_going_IN[0],Lane_available_for_connection[r])

                        # here we check if (x3,y3) is on lanes_going_IN[0] (or Lane_available_for_connection[r])
                        # if it is, (x1,y1) (or (x3,y3)) will be the point after (respectively the point before) on the lanes
                        # so that the curve created will be smoother

                        k2=0
                        while k2<len(Lane_available_for_connection[r]) :
                            p2 = Lane_available_for_connection[r][k2]
                            if dist(p2,(x3,y3))<0.5 :
                                (x2,y2) = Lane_available_for_connection[r][k2+1]
                                k2=len(Lane_available_for_connection[r])
                            k2+=1

                        k1=len(lanes_going_IN[0])-1
                        while k1>0 :
                            p1 = lanes_going_IN[0][k1]
                            if dist(p1,(x3,y3))<0.5 :
                                (x1,y1) = lanes_going_IN[0][k1-1]
                                k1=-1
                            k1=k1-1


                        xs = [x1, x3, x3, x2]
                        ys = [y1, y3, y3, y2]

                        l1 = Curve(xs, ys, 0)
                        Current_Lane1 = []
                        counter_addLine = -1
                        for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                            if counter_addLine>-1 :
                                if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                    Current_Lane1.append([x, y])
                                    counter_addLine+=1
                            else :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        self.l.append(Current_Lane1)


                else :

                    Lane_available_for_connection_right = Lane_available_for_connection[0:cs_lanes_going_OUT[(m+1)%3]]
                    Lane_available_for_connection_left = Lane_available_for_connection[cs_lanes_going_OUT[(m+1)%3]:cs_lanes_going_OUT[(m+1)%3]+cs_lanes_going_OUT[(m+2)%3]]

                    if Lane_available_for_connection_left == [] : #If one of the lists is empty then the lanes of interest will be connected to the samme lanes
                        Lane_available_for_connection_left = Lane_available_for_connection_right
                    elif Lane_available_for_connection_right == [] :
                        Lane_available_for_connection_right = Lane_available_for_connection_left

                    # We will create a more specific list out of list 2 (that contains every lanes available for connections
                    # Lane available for connection left in whih you'll have every lane locatrd on the crossection to the left
                    # And Lane available for connection right will is the same but for the lanes located on the corssection to the right

                    if len(lanes_going_IN)%2 !=0: # If there is an odd numbers of lanes then list 2 will be broken into the 2 list right/left and the raminaing lane will be had to the list that have less lanes
                        lanes_going_IN_right = lanes_going_IN[0:(len(lanes_going_IN)//2)+1]
                        lanes_going_IN_left = lanes_going_IN[(len(lanes_going_IN)//2)+1:]

                        if len(Lane_available_for_connection_right) > len(Lane_available_for_connection_left):
                            lanes_going_IN_right.append(lanes_going_IN[int((len(lanes_going_IN)-1)//2)])
                        elif len(Lane_available_for_connection_left) > len(Lane_available_for_connection_right):
                            lanes_going_IN_left.append(lanes_going_IN[int((len(lanes_going_IN)-1)//2)])
                        else :
                            lanes_going_IN_right.append(lanes_going_IN[int((len(lanes_going_IN)-1)//2)])

                    else :
                        lanes_going_IN_right = lanes_going_IN[0:int((len(lanes_going_IN)-1)//2)+1]
                        lanes_going_IN_left = lanes_going_IN[int((len(lanes_going_IN)-1)//2)+1:]



                    for q in range(len(lanes_going_IN_right)):  # Right side of X Crossing

                        # The list now created we make every connections
                        # And we will proceed that way
                        #
                        #                     |      |       |
                        #                     |      |       |
                        # Lanes in list 2 :   |      |       |
                        #                     |      |       |
                        #                    (a2)   (b2)    (c2)
                        #                        |       |
                        #                        |       |
                        # Lanes in list 1 :      |       |
                        #                        |       |
                        #                       (a1)    (b1)
                        #
                        # a1 to a2, and b1 to b2 and c2
                        # If List 1 had three lanes then a1 to a2, b1 to b2, c1 to c2

                        for j in range(len(Lane_available_for_connection_right)):

                            (x1,y1) = lanes_going_IN_right[q][len(lanes_going_IN_right[q])-1]

                            (x2,y2) = Lane_available_for_connection_right[j][0]

                            (x3,y3) = Intersection_Lines(lanes_going_IN_right[q], Lane_available_for_connection_right[j])

                            k2=0
                            while k2<len(Lane_available_for_connection_right[j]) :
                                p2 = Lane_available_for_connection_right[j][k2]
                                if dist(p2,(x3,y3))<0.5 :
                                    (x2,y2) = Lane_available_for_connection_right[j][k2+1]
                                    k2=len(Lane_available_for_connection_right[j])
                                k2+=1

                            k1=len(lanes_going_IN_right[0])-1
                            while k1>0 :
                                p1 = lanes_going_IN_right[q][k1]
                                if dist(p1,(x3,y3))<0.5 :
                                    (x1,y1) = lanes_going_IN_right[q][k1-1]
                                    k1=-1
                                k1=k1-1

                            xs = [x1, x3, x3, x2]
                            ys = [y1, y3, y3, y2]

                            l1 = Curve(xs, ys, 0)
                            Current_Lane1 = []
                            counter_addLine = -1
                            for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                                if counter_addLine>-1 :
                                    if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                        Current_Lane1.append([x, y])
                                        counter_addLine+=1
                                else :
                                    Current_Lane1.append([x, y])
                                    counter_addLine+=1
                            self.l.append(Current_Lane1)





                    for q in range(len(lanes_going_IN_left)):  # Left side of X Crossing
                        # Same working but for the left
                        for j in range(len(Lane_available_for_connection_left)):

                            (x1,y1) = lanes_going_IN_left[q][len(lanes_going_IN_left[q])-1]

                            (x2,y2) = Lane_available_for_connection_left[j][0]

                            (x3,y3) = Intersection_Lines(lanes_going_IN_left[q], Lane_available_for_connection_left[j])

                            k2=0
                            while k2<len(Lane_available_for_connection_left[j]) :
                                p2 = Lane_available_for_connection_left[j][k2]
                                if dist(p2,(x3,y3))<0.5 :
                                    (x2,y2) = Lane_available_for_connection_left[j][k2+1]
                                    k2=len(Lane_available_for_connection_left[j])
                                k2+=1

                            k1=len(lanes_going_IN_left[0])-1
                            while k1>0 :
                                p1 = lanes_going_IN_left[q][k1]
                                if dist(p1,(x3,y3))<0.5 :
                                    (x1,y1) = lanes_going_IN_left[q][k1-1]
                                    k1=-1
                                k1=k1-1

                            xs = [x1, x3, x3, x2]
                            ys = [y1, y3, y3, y2]


                            l1 = Curve(xs, ys, 0)
                            Current_Lane1 = []
                            counter_addLine = -1
                            for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                                if counter_addLine>-1 :
                                    if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                        Current_Lane1.append([x, y])
                                        counter_addLine+=1
                                else :
                                    Current_Lane1.append([x, y])
                                    counter_addLine+=1
                            self.l.append(Current_Lane1)




            count_lanes_going_IN += cs_nbr_of_lanes[m]

        # Edges

        # TO DO

    ##This method returns the starting coordinates of the road's center path. 
    #
    #Returns (Float, Float)
    def getstart(self):
        return (self.x, self.y)

    ##This method returns the last coordinates of the road's center path.
    #
    #Returns (Float, Float)
    def getend(self):
        return (self.x, self.y)

##This a representation of an ycrossing road in Prescan. Each road contains one segment for each arm of the ycrossing.
class YCrossRoad(Road):



    ##The constructor
    #@param self The object pointer.
    #@param id A string. Unique id
    #@param x0 A float. The x coordinate of the center of the start of the road segment.
    #@param y0 A float. The y coordinate of the center of the start of the road segment.
    #@param h A float. Global heading of the road segment at the start point.
    #@param r A float. Distance from the starting point to furthest center point of one of the lanes.
    #@param lw A float. The lane width
    #@param cs_h List (of floats) of headings for each arm of the ycrossing.
    #@param cs_len_till_stop A float. Distance from endpoint of the arms to the arms' stopline.
    #@param cs_nbr_of_lanes List (of integers) of the number of lane for each arm of the ycrossing.
    #@param cs_lanes_going_OUT List (of integers) representing the number of lines at every exit of the crossing
    #@param cs_l List (of floats) of road length for each arm of the ycrossing.
    #@param SpeedL A float. The speed limit
    #@param RefS A float. The reference speed
    #@param Stl List of lists contening relevant points (3 points per list) describing a stopline. Base components are floats.
    #@param cw List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base components are floats.

    def __init__(self, id, x0, y0, h, lw, cs_h, cs_len_till_stop, cs_nbr_of_lanes, cs_lanes_going_OUT, cs_l, SpeedL, RefS, Stl, cw):

        # General Init

        Road.__init__(self, id)
        ##A float. The speed limit
        self.SpeedLimit = SpeedL
        ##A float. The reference speed
        self.RefSpeed = RefS
        ##A float. The x coordinate of the center of the start of the road segment.
        self.x=x0
        ##A float. The y coordinate of the center of the start of the road segment.
        self.y=y0
        ##List of lists contening relevant points (3 points per list) describing a stopline. Base components are floats.
        self.stopline = Stl
        ##A float. Represents the speed that the road has per default (defined by the speedprofile in the Road Class)
        self.DefinedSpeed = self.SpeedProfil[9]
        ##List of lists contening relevant points (3 points per list) describing the 3 lines describing a crosswalk. Base components are floats.
        self.crosswalk = cw

        # Lanes Creation

        # Creation of each "Starting Lane"

        counter = 0

        for c in range(3):  # For each Branch of the Y Crossing


            nb_of_lanes = cs_nbr_of_lanes[c]
            lanes_going_OUT = cs_lanes_going_OUT[c]
            lwi=(cs_nbr_of_lanes[c] -1) * lw/2
            next_first_lane = counter             # Allow us the access to the first lane created that need to be reversed

            for lane in range(nb_of_lanes):

                l1 = Straight(x0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.cos(cs_h[c]+h) + (lwi)*np.cos(cs_h[c]+h+ np.pi / 2), y0 + (cs_l[c]-cs_len_till_stop[c]-1)*np.sin(cs_h[c]+h) + (lwi)*np.sin(cs_h[c]+h+ np.pi / 2), cs_h[c]+h, (cs_len_till_stop[c]+1))

                Current_Lane = []  # This convert the lane from a path obj to a tab of point
                for (x,y) in l1:
                    Current_Lane.append([x, y])

                self.l.append(Current_Lane[1:])

                lwi -= lw
                counter += 1

            # We are creating here the straight part of the lane at the beginning of each crosssection from the stopline to
            # the beggining of the road in the following order (1 : a -> b then 2->3)
            #
            #
            #                ######################
            #                             a) |---->
            #                   2               1
            #                             b)  ---->
            #                #######       ########
            #                      #       #
            #                      #   3   #
            #                      #       #
            #
            # We need now to change the direction of the lanes that drive backwards


            # Changing the direction of the lanes that drive backwards

            if nb_of_lanes-lanes_going_OUT>0:
                for j in range(nb_of_lanes-lanes_going_OUT):
                    l=[]
                    for (x, y) in self.l[next_first_lane + j]:
                        l.append([x, y])
                    l = l[::-1]
                    self.l[next_first_lane + j] = l

        # Stoplines Creation




        # Creating every connections between each starting lanes

        # We will now link each crossections of the y crossing
        #
        #                ######################
        #                <----------------|----
        #                   2    |          1
        #                        |    b)  ---->
        #                ####### |     ########
        #                      # |     #
        #                      # | 3   #
        #                      # |     #
        #
        #
        # In order to understand the implentation of this next part, please read the comment AND the wiki dedicated to this RT



        total_nb_of_lanes = 0   # This will be usefull to create a counter that can circle back to the beggining of the lane list (see below)
        Number_of_lanes_going_IN = [] #lanes heading towards the center of the crossroad
        Index_lanes_going_out = []
        Index_lanes_going_in = []
        for i in range(3):
            Index_lanes_going_out_local = []
            Index_lanes_going_in_local = []
            nb_of_lanes = cs_nbr_of_lanes[i]
            lanes_going_OUT = cs_lanes_going_OUT[i]

            if lanes_going_OUT > 0 : # here we save the index in self.l of the lanes driving in the x dir
                if nb_of_lanes == lanes_going_OUT :
                    for k in range (nb_of_lanes):
                        Index_lanes_going_out_local.append(total_nb_of_lanes+k)
                else :
                    for k in range (lanes_going_OUT) :
                        Index_lanes_going_out_local.append(total_nb_of_lanes+k + (nb_of_lanes-lanes_going_OUT))

            for k in range (nb_of_lanes):
                if (k+total_nb_of_lanes) not in Index_lanes_going_out_local :
                    Index_lanes_going_in_local.append(k + total_nb_of_lanes)

            total_nb_of_lanes += nb_of_lanes

            Number_of_lanes_going_IN.append(nb_of_lanes - lanes_going_OUT)
            Index_lanes_going_in.append(Index_lanes_going_in_local)
            Index_lanes_going_out.append(Index_lanes_going_out_local)

        count_lanes_going_IN =0

        for m in range(3): # For each corssections

            # We will proceed by doing two list for each crossection :
            # The first list will list every lanes going in the right direction on the current crossections
            # The second list will contain every relevant lanes that can be linked to the lane that are in the first list
            #
            #
            #                ######################
            #                ----- (c)        ----- (a)
            #                   2               1
            #                ----- (d)        ----- (b)
            #                #######       ########
            #                      # |   | #
            #                      # | 3 | #
            #                      # |   | #
            #                       (e) (f)
            #
            # So here for instance for crossection one , list 1 = [Lane a]
            # and List 2 = [Lane c,Lane e]
            #

            if Number_of_lanes_going_IN[m] !=0 :  # if there are lanes going in the opposite x direction


                nb_of_lanes = cs_nbr_of_lanes[m]
                lanes_going_OUT = cs_lanes_going_OUT[m]
                counter_remaining_lanes = nb_of_lanes - lanes_going_OUT

                lanes_going_IN = []
                for k in range (len(Index_lanes_going_in[m])):
                    lanes_going_IN.append(self.l[Index_lanes_going_in[m][k]])  # Lanes going in the crossroad that we will link to the roads going out of the crossroad


                Lane_available_for_connection = []
                Lane_available_for_connection_right = []
                Lane_available_for_connection_left = []
                for p in range(3):
                    if p != m :
                        for k in range (len(Index_lanes_going_out[p])) :
                            Lane_available_for_connection.append(self.l[Index_lanes_going_out[p][k]])




                if Number_of_lanes_going_IN[m] == 1 :  # If we have only one lane going in the crossroad

                    for r in range(len(Lane_available_for_connection)): # We connect the Only Lane of interest to EVERY lane avaible for conections

                        (x1,y1) = lanes_going_IN[0][len(lanes_going_IN[0])-1]

                        (x2,y2) = Lane_available_for_connection[r][0]

                        (x3,y3) = Intersection_Lines(lanes_going_IN[0],Lane_available_for_connection[r])

                        # here we check if (x3,y3) is on lanes_going_IN[0] or Lane_available_for_connection[r]
                        # if it is, (x1,y1) (or (x3,y3)) will be the point after (respectively the point before) on the lanes
                        # so that the curve created will be smoother

                        k2=0
                        while k2<len(Lane_available_for_connection[r]) :
                            p2 = Lane_available_for_connection[r][k2]
                            if dist(p2,(x3,y3))<0.5 :
                                (x2,y2) = Lane_available_for_connection[r][k2+1]
                                k2=len(Lane_available_for_connection[r])
                            k2+=1

                        k1=len(lanes_going_IN[0])-1
                        while k1>0 :
                            p1 = lanes_going_IN[0][k1]
                            if dist(p1,(x3,y3))<0.5 :
                                (x1,y1) = lanes_going_IN[0][k1-1]
                                k1=-1
                            k1=k1-1


                        xs = [x1, x3, x3, x2]
                        ys = [y1, y3, y3, y2]

                        l1 = Curve(xs, ys, 0)
                        Current_Lane1 = []
                        counter_addLine = -1
                        for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                            if counter_addLine>-1 :
                                if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                    Current_Lane1.append([x, y])
                                    counter_addLine+=1
                            else :
                                Current_Lane1.append([x, y])
                                counter_addLine+=1
                        self.l.append(Current_Lane1)


                else :

                    Lane_available_for_connection_right = Lane_available_for_connection[0:cs_lanes_going_OUT[(m+1)%3]]
                    Lane_available_for_connection_left = Lane_available_for_connection[cs_lanes_going_OUT[(m+1)%3]:cs_lanes_going_OUT[(m+1)%3]+cs_lanes_going_OUT[(m+2)%3]]

                    if Lane_available_for_connection_left == [] : #If one of the lists is empty then the lanes of interest will be connected to the samme lanes
                        Lane_available_for_connection_left = Lane_available_for_connection_right
                    elif Lane_available_for_connection_right == [] :
                        Lane_available_for_connection_right = Lane_available_for_connection_left

                    # We will create a more specific list out of list 2 (that contains every lanes available for connections
                    # Lane available for connection left in whih you'll have every lane locatrd on the crossection to the left
                    # And Lane available for connection right will is the same but for the lanes located on the corssection to the right

                    if len(lanes_going_IN)%2 !=0: # If there is an odd numbers of lanes then list 2 will be broken into the 2 list right/left and the raminaing lane will be had to the list that have less lanes
                        lanes_going_IN_right = lanes_going_IN[0:(len(lanes_going_IN)//2)+1]
                        lanes_going_IN_left = lanes_going_IN[(len(lanes_going_IN)//2)+1:]

                        if len(Lane_available_for_connection_right) > len(Lane_available_for_connection_left):
                            lanes_going_IN_right.append(lanes_going_IN[int((len(lanes_going_IN)-1)//2)])
                        elif len(Lane_available_for_connection_left) > len(Lane_available_for_connection_right):
                            lanes_going_IN_left.append(lanes_going_IN[int((len(lanes_going_IN)-1)//2)])
                        else :
                            lanes_going_IN_right.append(lanes_going_IN[int((len(lanes_going_IN)-1)//2)])

                    else :
                        lanes_going_IN_right = lanes_going_IN[0:int((len(lanes_going_IN)-1)//2)+1]
                        lanes_going_IN_left = lanes_going_IN[int((len(lanes_going_IN)-1)//2)+1:]



                    for q in range(len(lanes_going_IN_right)):  # Right side of Y Crossing

                        # The list now created we make every connections
                        # And we will proceed that way
                        #
                        #                     |      |       |
                        #                     |      |       |
                        # Lanes in list 2 :   |      |       |
                        #                     |      |       |
                        #                    (a2)   (b2)    (c2)
                        #                        |       |
                        #                        |       |
                        # Lanes in list 1 :      |       |
                        #                        |       |
                        #                       (a1)    (b1)
                        #
                        # a1 to a2, and b1 to b2 and c2
                        # If List 1 had three lanes then a1 to a2, b1 to b2, c1 to c2

                        for j in range(len(Lane_available_for_connection_right)):

                            (x1,y1) = lanes_going_IN_right[q][len(lanes_going_IN_right[q])-1]

                            (x2,y2) = Lane_available_for_connection_right[j][0]

                            (x3,y3) = Intersection_Lines(lanes_going_IN_right[q], Lane_available_for_connection_right[j])

                            k2=0
                            while k2<len(Lane_available_for_connection_right[j]) :
                                p2 = Lane_available_for_connection_right[j][k2]
                                if dist(p2,(x3,y3))<0.5 :
                                    (x2,y2) = Lane_available_for_connection_right[j][k2+1]
                                    k2=len(Lane_available_for_connection_right[j])
                                k2+=1

                            k1=len(lanes_going_IN_right[0])-1
                            while k1>0 :
                                p1 = lanes_going_IN_right[q][k1]
                                if dist(p1,(x3,y3))<0.5 :
                                    (x1,y1) = lanes_going_IN_right[q][k1-1]
                                    k1=-1
                                k1=k1-1

                            xs = [x1, x3, x3, x2]
                            ys = [y1, y3, y3, y2]

                            l1 = Curve(xs, ys, 0)
                            Current_Lane1 = []
                            counter_addLine = -1
                            for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                                if counter_addLine>-1 :
                                    if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                        Current_Lane1.append([x, y])
                                        counter_addLine+=1
                                else :
                                    Current_Lane1.append([x, y])
                                    counter_addLine+=1
                            self.l.append(Current_Lane1)





                    for q in range(len(lanes_going_IN_left)):  # Left side of Y Crossing
                        # Same working but for the left
                        for j in range(len(Lane_available_for_connection_left)):

                            (x1,y1) = lanes_going_IN_left[q][len(lanes_going_IN_left[q])-1]

                            (x2,y2) = Lane_available_for_connection_left[j][0]

                            (x3,y3) = Intersection_Lines(lanes_going_IN_left[q], Lane_available_for_connection_left[j])

                            k2=0
                            while k2<len(Lane_available_for_connection_left[j]) :
                                p2 = Lane_available_for_connection_left[j][k2]
                                if dist(p2,(x3,y3))<0.5 :
                                    (x2,y2) = Lane_available_for_connection_left[j][k2+1]
                                    k2=len(Lane_available_for_connection_left[j])
                                k2+=1

                            k1=len(lanes_going_IN_left[0])-1
                            while k1>0 :
                                p1 = lanes_going_IN_left[q][k1]
                                if dist(p1,(x3,y3))<0.5 :
                                    (x1,y1) = lanes_going_IN_left[q][k1-1]
                                    k1=-1
                                k1=k1-1

                            xs = [x1, x3, x3, x2]
                            ys = [y1, y3, y3, y2]


                            l1 = Curve(xs, ys, 0)
                            Current_Lane1 = []
                            counter_addLine = -1
                            for (x,y) in l1: #we add the new lane but we check in the same time that 2 points aren't the same
                                if counter_addLine>-1 :
                                    if (round(x,4),round(y,4)) != (round(Current_Lane1[counter_addLine][0],4),round(Current_Lane1[counter_addLine][1],4)) :
                                        Current_Lane1.append([x, y])
                                        counter_addLine+=1
                                else :
                                    Current_Lane1.append([x, y])
                                    counter_addLine+=1
                            self.l.append(Current_Lane1)




            count_lanes_going_IN += cs_nbr_of_lanes[m]


    ##This method returns the starting coordinates of the road's center path. 
    #
    #Returns (Float, Float)
    def getstart(self):
        return (self.x, self.y)

    ##This method returns the last coordinates of the road's center path.
    #
    #Returns (Float, Float)
    def getend(self):
        return (self.x, self.y)
