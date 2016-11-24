import numpy as np
from scipy.spatial.distance import pdist

class Box(object):

    def __init__(width=500, height=500, nb_particles=None, radii=None,
        v_0=20, a_0=0, bounce=True):

        if nb_particles is None:
            nb_particles = 10

        self._x = np.random.rand(nb_particles, 2) * [width, height]
        self._v = np.random.rand(nb_particles, 2) * [v_0, v_0]
        self._a = np.random.rand(nb_particles, 2) * [a_0, a_0]

        if radii is None:
            radii = np.array([1]*nb_particles)

        self._radii = radii.reshape(1, -1)

        self.width = width
        self.height = height

    def update(self, t=1):
        self._v += self._a * t
        self._x += self._v * t

        # check for out-of-bounds
        over_x = self._x[:, 0] > self.width
        over_y = self._x[:, 1] > self.height

        if np.any(over_x):
            self._x[over_x, 0] = 2*self.width - self._x[over_x, 0]

        if np.any(over(y)):
            self._x[over_y, 1] = 2*self.height - self._x[over_y, 1]

        self._x = np.abs(self._x)

        collisions = self._check_collisions()
        return collisions

    # handling collisions

    def _check_collisions(self):
        dist = np.square(self._x[:,np.newaxis]-self._x).sum(axis=2))
        dist = np.sqrt(dist)

        collisions = dist < (self._radii + self._radii.T)
        if np.any(collisions):
            pairs = [p for p in np.where(collisions) if p[0] < p[1]]
            for pair in pairs:
                self._collide(pair)
            return pairs
        return ()

    def _collide(self, pair):

        def v_hat(i,j):
            m_i = self._radii[i]**2
            m_j = self._radii[j]**2

            v_i = self._v[i, :]
            v_j = self._v[j, :]

            x_i = self._x[i, :]
            x_j = self._x[j, :]


            mass = 2*m_j/(m_i+m_j)
            prod = np.dot(v_i - v_j, x_i - x_j) / np.square(x_i-x_j).sum()
            direct = (x_i - x_j)
            return v_i - mass*prod*direct

        i,j = pair
        self._v[i] = v_hat(i,j)
        self._v[j] = v_hat(j,i)


    def delete(self, i):
        pass

    def add(self, x_0=None, v_0=20, a_0=0):
        pass
