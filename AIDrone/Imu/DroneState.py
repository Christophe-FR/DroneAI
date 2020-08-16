import Quaternion as qtn
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt

class DroneState():
    def __init__(self):
        self.time=0
        self.pos=[0, 0, 0]
        self.dposdt=[0, 0, 0]
        self.d2posdt2=[0, 0, 0]
        self.ang=[0, 0, 0] #psi, theta , phi
        self.dangdt=[0, 0, 0]
        self.d2angdt2=[0, 0, 0]

    def x(self):
        return self.pos[0]

    def y(self):
        return self.pos[1]

    def z(self):
        return self.pos[2]

    def psi(self):
        return self.ang[0]

    def theta(self):
        return self.ang[1]

    def phi(self):
        return self.ang[2]

    def plot(self):
        Lx=0.5
        Ly=0.5
        Lz=0.05
        drone = np.array([[-Lx, -Ly, -Lz],
                  [Lx, -Ly, -Lz ],
                  [Lx, Ly, -Lz],
                  [-Lx, Ly, -Lz],
                  [-Lx, -Ly, Lz],
                  [Lx, -Ly, Lz ],
                  [Lx, Ly, Lz],
                  [-Lx, Ly, Lz]])/2

        drone_galilean_frame=np.zeros(drone.shape)

        for idx, point in enumerate(drone):
            drone_galilean_frame[idx] = qtn.rot(-self.phi(), [1, 0, 0], point)
            drone_galilean_frame[idx] = qtn.rot(-self.theta(), [0, 1, 0], drone_galilean_frame[idx])
            drone_galilean_frame[idx] = qtn.rot(-self.psi(), [0, 0, 1], drone_galilean_frame[idx])

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # plot vertices
        ax.scatter3D(drone_galilean_frame[:, 0], drone_galilean_frame[:, 1], drone_galilean_frame[:, 2],'green')

        # list of sides' polygons of figure
        verts = [[drone_galilean_frame[0],drone_galilean_frame[1],drone_galilean_frame[2],drone_galilean_frame[3]],
                [drone_galilean_frame[4],drone_galilean_frame[5],drone_galilean_frame[6],drone_galilean_frame[7]],
                [drone_galilean_frame[0],drone_galilean_frame[1],drone_galilean_frame[5],drone_galilean_frame[4]],
                [drone_galilean_frame[2],drone_galilean_frame[3],drone_galilean_frame[7],drone_galilean_frame[6]],
                [drone_galilean_frame[1],drone_galilean_frame[2],drone_galilean_frame[6],drone_galilean_frame[5]],
                [drone_galilean_frame[4],drone_galilean_frame[7],drone_galilean_frame[3],drone_galilean_frame[0]]]

        # plot sides
        ax.add_collection3d(Poly3DCollection(verts, facecolors='black', linewidths=1, edgecolors='blue', alpha=.25))
        ax.set_xlim([-10,10])
        ax.set_ylim([-10, 10])
        ax.set_zlim([-10, 10])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        plt.show()


if __name__ == '__main__':
    drone_state=DroneState()
    drone_state.plot()

