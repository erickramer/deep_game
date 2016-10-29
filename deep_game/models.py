from deep_game import app
import numpy as np

class Particle(object):

    def __init__(self, name, max_pos, pos=None, vel=None, acc=None, r=25):
        self.name = name
        self.max_pos = max_pos
        self.r = r

        if pos is None:
            self._pos = np.zeros(2)
        else:
            self._pos = np.array(pos)

        if vel is None:
            self._vel = np.zeros(2)
        else:
            self._vel = np.array(vel)

        if acc is None:
            self._acc = np.zeros(2)
        else:
            self._acc = np.array(acc)

    def update(self, step=1.0):
        self._vel += self._acc*step
        self._pos += self._vel*step

        for i in range(2):
            if self._pos[i] > self.max_pos[i]:
                self._pos[i] = 2*self.max_pos[i] - self._pos[i]
                self._vel[i] = -self._vel[i]
            elif self._pos[i] < 0:
                self._pos[i] = -self._pos[i]
                self._vel[i] = -self._vel[i]

    def to_dict(self):
        return {'id': self.name, 'x': self.x, 'y': self.y, 'r': self.r}

    @property
    def pos(self):
        return self._pos

    @property
    def x(self):
        return float(self._pos[0])

    @property
    def y(self):
        return float(self._pos[1])

    @classmethod
    def collided(cls, x, y):
        dist = np.sqrt(np.sum((x.pos - y.pos)**2))
        return dist < (x.r + y.r)

class Dot(Particle):
    pass

class Triangle(Particle):
    pass

class Circle(Particle):

    def turn(self, direction):

        if direction in ["left", "right"]:
            theta = 0
            if direction == "left":
                theta = -15
            elif direction == "right":
                theta = 15

            phi = theta / 360. * 2 * np.pi
            sin = np.sin(phi)
            cos = np.cos(phi)

            r = np.array([[cos, -sin], [sin, cos]])
            self._vel = np.dot(self._vel, r)
        elif direction in ["up", "down"]:
            if direction == "up":
                self._vel *= 1.1
            elif direction == "down":
                self._vel *= 0.9


class Board(object):

    def __init__(self, height=400, width=600,
                    nb_dots=10, nb_circles=1, nb_triangles=2):

        self.height = height
        self.width = width
        self.nb_dots = nb_dots
        self.nb_circles = nb_circles
        self.nb_triangles = nb_triangles

        self.reset()

    def reset(self):
        self.score = 0
        self.alive = True

        self._dot_count = 0
        self._triangle_count = 0
        self._circle_count = 0

        self._circles = {}
        self._triangles = {}
        self._dots = {}

        for i in range(self.nb_dots):
            self._add_dot()

        for i in range(self.nb_circles):
            self._add_circle()

        for i in range(self.nb_triangles):
            self._add_triangle()

    def _add_dot(self):
        pos = np.random.rand(2) * [self.width, self.height]
        vel = np.random.rand(2) * [10, 10]
        dot = Dot(self._dot_count, self.max_pos, pos=pos, vel=vel, r=3)
        self._dots[self._dot_count] = dot
        self._dot_count += 1

    def _add_triangle(self):
        pos = np.random.rand(2) * [self.width, self.height]
        vel = np.random.rand(2) * [10, 10]
        triangle = Triangle(self._triangle_count, self.max_pos, pos=pos, vel=vel, r=3)
        self._triangles[self._triangle_count] = triangle
        self._triangle_count += 1

    def _add_circle(self):
        pos = np.random.rand(2) * [self.width, self.height]
        vel = np.random.rand(2) * [10, 10]
        circle = Circle(self._circle_count, self.max_pos, pos=pos, vel=vel, r=10)
        self._circles[self._circle_count] = circle
        self._circle_count += 1

    def _detect_collisions(self):

        circle = self._circles[0]

        for triangle in self._triangles.values():
            if Particle.collided(circle, triangle):
                self.alive = False

        for dot in self._dots.values():
            if Particle.collided(circle, dot):
                self.score += 1
                del self._dots[dot.name]

                self._add_dot()
                if self.score % 5 == 0:
                    if self._triangle_count < 20:
                        self._add_triangle()


    def update(self, ctrls=None):
        self._detect_collisions()

        if self.alive:
            if ctrls is not None:
                for ctrl in ctrls:
                    circle = self.circle(ctrl['name'])
                    circle.turn(ctrl['direction'])

            for dot in self._dots.values():
                dot.update()

            for circle in self._circles.values():
                circle.update()

            for triangle in self._triangles.values():
                triangle.update()


    def circle(self, name):
        return self._circles[name]

    @property
    def state(self):
        def to_dict(d):
            return {'id': d.name, 'x': d.x, 'y': d.y}

        dots = [to_dict(d) for d in self._dots.values()]
        circles = [to_dict(d) for d in self._circles.values()]
        triangles = [to_dict(d) for d in self._triangles.values()]

        return {'alive': self.alive,
                'score': self.score,
                'dots': dots,
                'circles': circles,
                'triangles': triangles}

    @property
    def dimensions(self):
        return {'height': self.height, 'width': self.width}

    @property
    def max_pos(self):
        return np.array([self.width, self.height])
