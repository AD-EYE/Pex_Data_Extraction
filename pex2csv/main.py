from matplotlib import pyplot as plt
import parse
import inspect

if __name__ == '__main__':
    roads = parse.get_roads()

    cx, cy = [], []
    ex, ey = [], []
    lx, ly = [], []
    xx, xy = [], []
    xlx, xly = [], []

    for id in roads.keys():
        for (x, y) in roads[id].c:
            cx.append(x)
            cy.append(y)
        try:
            if(not type(roads[id].e1) is list):
                for (x, y) in roads[id].e1:
                    ex.append(x)
                    ey.append(y)
            else:
                for p in roads[id].e1:
                    for (x, y) in p:
                        ex.append(x)
                        ey.append(y)
            for (x, y) in roads[id].e2:
                ex.append(x)
                ey.append(y)
            for (x, y) in roads[id].l1:
                lx.append(x)
                ly.append(y)
            for (x, y) in roads[id].l2:
                lx.append(x)
                ly.append(y)
            for exit in roads[id].x:
                for (x, y) in exit:
                    xx.append(x)
                    xy.append(y)
            for xlane in roads[id].xl:
                for (x, y) in xlane:
                    xlx.append(x)
                    xly.append(y)
        except Exception as e: print(e)

    plt.plot(cx, cy, 'bo')
    plt.plot(ex, ey, 'ro')
    plt.plot(lx, ly, 'ko')
    plt.plot(xx, xy, 'ro')
    plt.plot(xlx, xly, 'ko')
    plt.legend(['center', 'edge', 'lane'])
    plt.axis('equal')
    plt.grid(True)
    plt.show()
