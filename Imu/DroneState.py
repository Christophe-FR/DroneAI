import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import matplotlib.pyplot as plt
import Quaternion

class DroneState():
    def __init__(self):
        self.time=0
        self.pos=[0, 0, 0]
        self.dposdt=[0, 0, 0]
        self.d2posdt2=[0, 0, 0]
        self.ang=[0, 0, 0] #psi, theta , phi
        self.dangdt=[0, 0, 0]
        self.d2angdt2=[0, 0, 0]

    def plot(self):
        Lx=1
        Ly=1
        Lz=0.1
        coordinates_3D_drone_frame = 0.5*np.array([[-Lx, -Ly, -Lz],
                           [Lx, -Ly, -Lz],
                           [Lx, Ly, -Lz],
                           [-Lx, Ly, -Lz],
                           [-Lx, -Ly, Lz],
                           [Lx, -Ly, Lz],
                           [Lx, Ly, Lz],
                           [-Lx, Ly, Lz]])

        coordinates_3D_galilean_frame_

        for coordinates in coordinates_3D_drone_frame:
            print(coordinates)
            print('NExt')

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlim3d(-10, 10)
        ax.set_ylim3d(-10, 10)
        ax.set_zlim3d(-10, 10)

        # plot vertices
        ax.scatter3D(coordinates_3D_drone_frame[:, 0], coordinates_3D_drone_frame[:, 1], coordinates_3D_drone_frame[:, 2])

        # list of sides' polygons of figure
        verts = [[coordinates_3D_drone_frame[0], coordinates_3D_drone_frame[1], coordinates_3D_drone_frame[2], coordinates_3D_drone_frame[3]],
                 [coordinates_3D_drone_frame[4], coordinates_3D_drone_frame[5], coordinates_3D_drone_frame[6], coordinates_3D_drone_frame[7]],
                 [coordinates_3D_drone_frame[0], coordinates_3D_drone_frame[1], coordinates_3D_drone_frame[5], coordinates_3D_drone_frame[4]],
                 [coordinates_3D_drone_frame[2], coordinates_3D_drone_frame[3], coordinates_3D_drone_frame[7], coordinates_3D_drone_frame[6]],
                 [coordinates_3D_drone_frame[1], coordinates_3D_drone_frame[2], coordinates_3D_drone_frame[6], coordinates_3D_drone_frame[5]],
                 [coordinates_3D_drone_frame[4], coordinates_3D_drone_frame[7], coordinates_3D_drone_frame[3], coordinates_3D_drone_frame[0]]]

        # plot sides
        ax.add_collection3d(Poly3DCollection(verts,facecolors='grey', linewidths=1, edgecolors='k', alpha=.25))

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        plt.show()



if __name__ == '__main__':
    drone_state=DroneState()
    drone_state.plot()

