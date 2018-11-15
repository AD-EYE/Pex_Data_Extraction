from matplotlib import pyplot as plt
import numpy as np

# Visualizes a VectorMap object. See vmap.py.
def vmplot(vm):

    # Create the figure.
    plt.figure('Vector Map')
    plt.axis('equal')
    plt.grid(True)

    # Plot the lane data as arrows.
    for x, y, m, d in vm.get_all_vectors():
        plt.arrow(
            x, y, m * np.cos(d), m * np.sin(d),
            head_width=0.25, head_length=0.2, fc='w', ec='k',
            width=0.1, length_includes_head=True
        )

    # Plot the center lines.
    for line in vm.get_all_lines():
        plt.plot(line[:,0], line[:,1], 'y-')

    # Plot the road edges.
    for edge in vm.get_all_edges():
        plt.plot(edge[:,0], edge[:,1], 'b-')

    plt.show()
