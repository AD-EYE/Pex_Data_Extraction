from matplotlib import pyplot as plt
import parse

if __name__ == '__main__':
    roads = parse.get_roads()

    cx, cy = [], []
    ex, ey = [], []
    lx, ly = [], []

    for id in roads.keys():
        for (x, y) in roads[id].c:
            cx.append(x)
            cy.append(y)
        try:
            for (x, y) in roads[id].e1:
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
        except: pass

    plt.plot(cx, cy, 'bo')
    plt.plot(ex, ey, 'ro')
    plt.plot(lx, ly, 'ko')
    plt.legend(['center', 'edge', 'lane'])
    plt.axis('equal')
    plt.grid(True)
    plt.show()
