import math

def get_coords(x, y, radius, angle_rad):
    x2 = 0
    y2 = 0

    if(angle_rad > 0):
        x2 = x + radius * math.cos(-math.pi/2 + angle_rad)
        y2 = y + (radius + radius * math.sin(-math.pi/2 + angle_rad))
    else:
        x2 = x + radius * math.cos((math.pi/2) + angle_rad)
        y2 = y - (radius + radius * math.sin(-(math.pi/2) + angle_rad))

    return [x2, y2]

def create_bend_road(x, y, radius, angle_rad):
    arc_len = abs(angle_rad) * radius
    point_nbr = math.ceil(arc_len)
    coords = []
    coords.append([x,y])
    angle_incr = angle_rad/point_nbr
    angle = 0

    for _ in range(point_nbr):
        angle = angle + angle_incr
        coords.append(get_coords(x, y, radius, angle))

    return coords
