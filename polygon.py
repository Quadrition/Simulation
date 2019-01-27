import math
import pygame
import numpy as np
from runge_kutta import runge_kutta_4


class Polygon:
    C = 3

    def __init__(self, centroid, radius, degree, mass, color=(255, 0, 0)):
        # Basic attributes
        self.centroid = centroid
        self.degree = degree
        self.radius = radius
        self.reference_vector = np.array([0, -radius])
        self.color = color
        self.time = pygame.time.get_ticks()

        # Physics
        self.forces = np.array([np.array([0., 0.]), np.array([0., 0.])])
        self.mass = mass

        # Translation
        self.translational_forces = np.array([np.array([0., 0.]), np.array([0., 0.])])
        self.translational_speed = np.array([0., 0.])
        # Rotation
        self.torques = np.array([0.])
        self.rotational_speed = np.array([0.])
        self.moment_area = (math.pi / 4.) * self.radius #jer je 2D telo, pa nema masu, korisceno za krug, jer poligon kako raste stepen, tezi krugu

    def rotate_reference_vector(self, theta):
        self.reference_vector = np.array(self.reference_vector * np.matrix(
            [[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])).ravel()

    @property
    def theta(self):
        return 2 * math.pi / self.degree

    @property
    def vertices(self):
        theta = self.theta
        vertices = [self.centroid + self.reference_vector]
        for i in range(1, self.degree):
            self.rotate_reference_vector(theta)
            vertices.append(self.centroid + self.reference_vector)
        self.rotate_reference_vector(theta)
        return vertices

    def rotate(self, theta):
        self.reference_vector = self.reference_vector * np.matrix(
            [[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])

    def draw(self, win):
        vertices = self.vertices
        for i in range(len(vertices)):
            vertices[i] = tuple(vertices[i].tolist())
        pygame.draw.polygon(win, self.color, vertices)

    # Calculates how much the polygon should move (translation)(
    def movement_function(self, t, y):
        force = np.array([0, 0])
        for f in self.translational_forces:
            force = force + f
        return np.array([y[1], (force - self.C * y[1]) / self.mass])

    # Calculates how much the polygon should rotate
    def rotation_function(self, t, y):
        torque = np.array([0, 0])
        for f in self.torques:
            torque = torque + f
        return np.array([y[1], (torque - self.C * y[1]) / self.moment_area])

    # Adds a force acting on the polygon and calculates torque and translational force
    def add_force(self, force):
        f = force[0] + force[1]
        point = force[2]
        moment_arm = point - self.centroid
        f_parallel = moment_arm * (np.dot(f, moment_arm) / np.dot(moment_arm, moment_arm))
        f_angular = f - f_parallel
        theta = math.atan(f_angular[1] / f_angular[0])
        torque = np.linalg(moment_arm) * np.linalg.norm(f_angular) * math.sin(theta)
        self.torques = np.concatenate(self.torques, torque)
        self.translational_forces = np.concatenate(self.translational_forces, f_parallel)
        #self.forces = np.concatenate((self.forces, force))

    # Clears all forces acting on the polygon
    def clear_forces(self):
        #self.forces = np.delete(self.forces, np.s_[2::], axis = 0)
        self.torques = np.array([0.])
        self.translational_forces = np.delete(self.translational_forces, np.s_[2::], axis = 0)

    def move(self, dt):
        self.start = np.array([self.centroid, self.translational_speed])
        t = self.time * 0.001 + dt * 0.001
        y = runge_kutta_4(self.movement_function, dt * 0.001, self.start, self.time * 0.001)
        self.time = t
        self.start = y
        self.centroid = y[0]
        self.translational_speed = y[1]

        #self.add_force(np.array([np.array([10000.,0.]),np.array([0.,1324.])]))
        self.clear_forces()

    def update(self, dt):
        self.move(dt)
        print self.torques
        #self.rotate(math.pi * dt * 0.001)
