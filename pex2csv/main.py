from matplotlib import pyplot as plt
import parse

if __name__ == '__main__':
    roads = parse.get_roads()
    xs, ys = [], []
    for id in roads.keys():
        for (x, y) in roads[id].center:
            xs.append(x)
            ys.append(y)
    plt.plot(xs, ys, '.')
    plt.axis('equal')
    plt.grid(True)
    plt.show()
