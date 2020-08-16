import numpy as np
from scipy.optimize import minimize

class quaternion:
    def __init__(self):
        self.coordef(0, 0, 0, 0)

    def coordef(self, r, i, j, k):  # defines a quaternion by its 4 coordinates
        self.r = r
        self.i = i
        self.j = j
        self.k = k

    def rotdef(self, theta,
               vector):  # defines a rotation quaternion : rotation of angle theta (rad) around the 3D vector (counter-clk)
        vector = vector / np.linalg.norm(vector)
        self.r = np.cos(theta / 2)
        self.i = vector[0] * np.sin(theta / 2)
        self.j = vector[1] * np.sin(theta / 2)
        self.k = vector[2] * np.sin(theta / 2)

    def pointdef(self,
                 coordinates):  # defines a point quaternion : representation of a point from its 3D cartesian coordinates
        self.r = 0
        self.i = coordinates[0]
        self.j = coordinates[1]
        self.k = coordinates[2]

    def show(self):  # display a quaternion
        print(self.r, "\t", self.i, "i\t", self.j, "j\t", self.k, "k")


def addqtn(qtn1: quaternion, qtn2: quaternion):  # quaternion sum qtn1+qtn2
    qtn = quaternion()
    qtn.r = qtn1.r + qtn2.r
    qtn.i = qtn1.i + qtn2.i
    qtn.j = qtn1.j + qtn2.j
    qtn.k = qtn1.k + qtn2.k
    return qtn


def subqtn(qtn1: quaternion, qtn2: quaternion):  # quaternion difference qtn1-qtn2
    qtn = quaternion()
    qtn.r = qtn1.r - qtn2.r
    qtn.i = qtn1.i - qtn2.i
    qtn.j = qtn1.j - qtn2.j
    qtn.k = qtn1.k - qtn2.k
    return qtn


def scaleqtn(alpha, qtn1: quaternion):  # scales a quaternion qtn1 by a scalar alpha
    qtn = quaternion()
    qtn.r = alpha * qtn1.r
    qtn.i = alpha * qtn1.i
    qtn.j = alpha * qtn1.j
    qtn.k = alpha * qtn1.k
    return qtn


def multqtn(qtn1: quaternion, qtn2: quaternion):  # quaternions multiplication: qtn1 left-multiplies qtn2
    qtn = quaternion()
    qtn.r = qtn1.r * qtn2.r - qtn1.i * qtn2.i - qtn1.j * qtn2.j - qtn1.k * qtn2.k
    qtn.i = qtn1.r * qtn2.i + qtn1.i * qtn2.r + qtn1.j * qtn2.k - qtn1.k * qtn2.j
    qtn.j = qtn1.r * qtn2.j - qtn1.i * qtn2.k + qtn1.j * qtn2.r + qtn1.k * qtn2.i
    qtn.k = qtn1.r * qtn2.k + qtn1.i * qtn2.j - qtn1.j * qtn2.i + qtn1.k * qtn2.r
    return qtn


def conjqtn(qtn1: quaternion):  # quaternion conjugate
    qtn = quaternion()
    qtn.r = qtn1.r
    qtn.i = -qtn1.i
    qtn.j = -qtn1.j
    qtn.k = -qtn1.k
    return qtn


def invqtn(qtn1: quaternion):  # quaternion multiplication inverse
    return scaleqtn(1 / modqtn(qtn1) ** 2, conjqtn(qtn1))


def modqtn(qtn1: quaternion):  # quaternion modulus
    return np.linalg.norm([qtn1.r, qtn1.i, qtn1.j, qtn1.k])

def normalizeqtn(qtn: quaternion):
    return scaleqtn(1/modqtn(qtn),qtn)


def qtn2pt(qtn1: quaternion):  # convert back a point quaternion in 3D coordinates
    return np.array([qtn1.i, qtn1.j, qtn1.k])


def qtnrot(qtnr: quaternion, qtnp: quaternion):  # applies a qtnr rotation on a qtnp point
    return multqtn(qtnr, multqtn(qtnp, invqtn(qtnr)))

def rot(angle,vector,point): # performs a rotation with quaternion algebra
    qtnr = quaternion()
    qtnp = quaternion()
    qtnr.rotdef(angle, vector)
    qtnp.pointdef(point)
    return qtn2pt(qtnrot(qtnr, qtnp))


def qtn2rotmatrix(q):  # display the 3x3 matrix representing a rotation quaternion
    q = normalizeqtn(q)
    return np.array([[1 - 2 * (q.j ** 2 + q.k ** 2), 2 * (q.i * q.j - q.k * q.r), 2 * (q.i * q.k + q.j * q.r)], [
        2 * (q.i * q.j + q.k * q.r), 1 - 2 * (q.i ** 2 + q.k ** 2), 2 * (q.j * q.k - q.i * q.r)], [
                2 * (q.i * q.k - q.j * q.r), 2 * (q.j * q.k + q.i * q.r), 1 - 2 * (q.i ** 2 + q.j ** 2)]])


def qtn2rot(qtn):  # extract the unit vector and angle from a rotation quaternion
    qtn = normalizeqtn(qtn)
    angle = np.arccos(qtn.r)
    vector = qtn2pt(qtn)/np.sqrt(1-qtn.r**2)
    return angle, vector


def qtn2euler(qtn):  # extract the euler angles describing the rotation
    qtn = scaleqtn(1 / modqtn(qtn), qtn)
    psi = np.arctan2(2 * (qtn.r * qtn.k + qtn.i * qtn.j), 1 - 2 * (qtn.j ** 2 + qtn.k ** 2))
    theta = np.arcsin(2 * (qtn.r * qtn.j - qtn.k * qtn.i))
    phi = np.arctan2(2 * (qtn.r * qtn.i + qtn.j * qtn.k), 1 - 2 * (qtn.i ** 2 + qtn.j ** 2))
    return np.rad2deg(psi), np.rad2deg(theta), np.rad2deg(phi)

def basis2qtn(basis1, basis2):
    return 0


if __name__ == "__main__":
    #print("Define a general quaternion from its coordinates, e.g. a=1 + 2i + 3j + 4k")
    #a = quaternion()
    #a.coordef(1, 2, 3, 4)
    #a.show()
    #print("Define a rotation quaternion (angle=90°, vector=[1,1,1])")
    #b = quaternion()
    #b.rotdef(90*3.14/180, [1, 1, 1])
    #b.show()
    #print("Add the two previous quaternions")
    #c = addqtn(a, b)
    #c.show()
    #print("Conjuguate the previous quaternions")
    #c = conjqtn(c)
    #c.show()
    #print("Compute its modulus")
    #print(modqtn(c))
    #print("")
    #angle = 120
    #vector = [2, 0, 0]
    #point = [1, 0, 0]
    #print("Quaternion associated to a ", angle, "° rotation along ", vector, " is:")
    #rotation = quaternion()
    #rotation.rotdef(angle*3.14/180, vector)
    #rotation.show()
    #print("Quaternion associated to point (", point, ") is:")
    #pointq = quaternion()
    #pointq.pointdef(point)
    #pointq.show()
    #print("Apply rotation on point")
    #out = qtn2pt(qtnrot(rotation, pointq))
    #print("Result=", out)
    #print("Equivalent rotation matrix")
    #print(qtn2rotmatrix(rotation))
    #print("Rotation parameters extracted from quaternion")
    #print(qtn2rot(rotation))
    #print("Equivalent euler angles extracted from quaternion [psi,theta,phi]")
    #print(qtn2euler(rotation))
    basis1 = np.array([[1, 0, 0],
                       [0, 1, 0],
                       [0, 0, 1]])
    basis2 = np.array([[0, -1, 0],
                       [1, 0, 0],
                       [0, 0, 1]])

    def qtn_square_error(qtn_vect):
        error = 0
        qtnr = quaternion()
        qtnr.coordef(qtn_vect[0], qtn_vect[1], qtn_vect[2], qtn_vect[3])
        # qtnr.show()
        # print('Quaternion modulus = ', modqtn(qtnr))
        qtnp = quaternion()
        for col in range(3):
            qtnp.pointdef(basis1[:, col])
            qtnp = qtnrot(qtnr, qtnp)
            error = error+np.linalg.norm(qtn2pt(qtnp)-basis2[:, col])**2
        # print('Error = ', error)
        return error
    qtn_coor_sol = minimize(qtn_square_error, np.array([1, 0, 0, 0]))
    qtn_coor_sol = qtn_coor_sol.x
    qtn_sol = quaternion()
    qtn_sol.coordef(qtn_coor_sol[0], qtn_coor_sol[1], qtn_coor_sol[2], qtn_coor_sol[3])
    qtn_sol = normalizeqtn(qtn_sol)
    # return qtn_sol
    qtn_sol.show()
    print(qtn2rotmatrix(qtn_sol))