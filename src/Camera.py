import glm
import numpy as np
from overrides import overrides
from scipy.spatial.distance import cdist


class Camera:
    def __init__(self, app):
        self.app = app
        self.aspect_ratio = app.WIN_SIZE[0]/app.WIN_SIZE[1]
        self.position = glm.vec3(0,60,0)
        self.up = glm.vec3(1,0,0)
        self.lookat = glm.vec3(0)
        self.radians = 100
        # view_matrix
        self.m_view = self.get_view_matrix()
        # projection matrix
        self.m_proj = self.get_projection_matrix()
        
    def get_view_matrix(self):
        return glm.lookAt(self.position, self.lookat, self.up)
    
    def get_projection_matrix(self):
        return glm.perspective(glm.radians(self.radians), self.aspect_ratio, 0.1, 100)

    def zoom(self, scroll):
        if 99 >= self.position[1]+scroll*0.5 >= 0:
            self.lookat = self.lookat + glm.vec3((0, scroll, 0))
            self.position = self.position + glm.vec3((0, scroll, 0))
            self.m_view = self.get_view_matrix()
    
    def move_right(self):
        self.lookat = self.lookat + glm.vec3((0, 0, 0.01*self.radians))
        self.position = self.position + glm.vec3((0, 0, 0.01*self.radians))
        self.m_view = self.get_view_matrix()

    def move_left(self):
        self.lookat = self.lookat + glm.vec3((0, 0, -0.01*self.radians))
        self.position = self.position + glm.vec3((0, 0, -0.01*self.radians))
        self.m_view = self.get_view_matrix()

    def move_up(self):
        self.lookat = self.lookat + glm.vec3((0.01*self.radians, 0, 0))
        self.position = self.position + glm.vec3((0.01*self.radians, 0, 0))
        self.m_view = self.get_view_matrix()
    
    def move_down(self):
        self.lookat = self.lookat + glm.vec3((-0.01*self.radians, 0, 0))
        self.position = self.position + glm.vec3((-0.01*self.radians, 0, 0))
        self.m_view = self.get_view_matrix()


class DriverCamera(Camera):
    def __init__(self, app, all_vertex, car_position):
        self.app = app
        self.aspect_ratio = app.WIN_SIZE[0] / app.WIN_SIZE[1]

        self.all_vertex = all_vertex
        self.car_position = np.array(car_position)
        self.camera_d = 25

        car_vertex, camera_vertex = self.get_camera_from_car(self.car_position)
        self.car_vertex = car_vertex
        self.camera_vertex = camera_vertex

        self.position = glm.vec3(self.camera_vertex[0], 0.5, self.camera_vertex[2])
        self.up = glm.vec3(0, 1, 0)
        self.lookat = glm.vec3(self.car_vertex[0], 0.3, self.car_vertex[2])
        self.radians = 110
        # view_matrix
        self.m_view = self.get_view_matrix()
        # projection matrix
        self.m_proj = self.get_projection_matrix()

    def move_right(self):
        self.lookat = self.lookat + glm.vec3((0, 0, 0.01 * self.radians))
        self.position = self.position + glm.vec3((0, 0, 0.01 * self.radians))
        self.m_view = self.get_view_matrix()

    def move_left(self):
        self.lookat = self.lookat + glm.vec3((0, 0, -0.01 * self.radians))
        self.position = self.position + glm.vec3((0, 0, -0.01 * self.radians))
        self.m_view = self.get_view_matrix()

    @overrides(check_signature=False)
    def move_up(self, new_car_position):
        car_vertex, camera_vertex = self.get_camera_from_car(new_car_position, move="up")
        self.car_vertex = car_vertex
        self.camera_vertex = camera_vertex
        print("up:", self.car_vertex, self.camera_vertex)
        self.position = glm.vec3(self.camera_vertex[0], 0.5, self.camera_vertex[2])
        self.lookat = glm.vec3(self.car_vertex[0], 0.3, self.car_vertex[2])
        self.m_view = self.get_view_matrix()

    @overrides(check_signature=False)
    def move_down(self, new_car_position):
        print("new car pos:", new_car_position)
        current_vertex, next_vertex = self.get_camera_from_car(new_car_position, move="down")
        self.current_vertex = current_vertex
        self.next_vertex = next_vertex
        print("down:", self.current_vertex, self.next_vertex)
        self.position = glm.vec3(self.current_vertex[0], 0.5, self.current_vertex[2])
        self.lookat = glm.vec3(self.next_vertex[0], 0.3, self.next_vertex[2])
        self.m_view = self.get_view_matrix()

    def get_camera_from_car(self, car_position, move="up"):
        car_position = np.array(car_position).reshape(1,3)
        print("new car pos:", car_position)
        d = cdist(car_position, self.all_vertex)
        idx_car = np.argmin(d)
        print("--> new idx:", idx_car)
        if move == "up":
            print("car vertex:", idx_car, (idx_car + 1) % len(self.all_vertex))
            car_vertex = self.get_center_vertex(self.all_vertex[idx_car],
                                                self.all_vertex[(idx_car + 1) % len(self.all_vertex)])
            print("camera vertex:", (idx_car - self.camera_d) % len(self.all_vertex), (idx_car - (self.camera_d + 1)) % len(self.all_vertex))
            camera_vertex = self.get_center_vertex(self.all_vertex[(idx_car - self.camera_d) % len(self.all_vertex)],
                                                   self.all_vertex[(idx_car - (self.camera_d + 1)) % len(self.all_vertex)])
            return car_vertex, camera_vertex
        elif move == "down":
            car_vertex = self.get_center_vertex(self.all_vertex[(idx_car - 1) % len(self.all_vertex)],
                                                self.all_vertex[idx_car])
            camera_vertex = self.get_center_vertex(self.all_vertex[(idx_car - self.camera_d - 1) % len(self.all_vertex)],
                                                   self.all_vertex[(idx_car - self.camera_d) % len(self.all_vertex)])
            return car_vertex, camera_vertex

    @staticmethod
    def get_center_vertex(vertex, next_vertex):
        y_mid_point = (next_vertex[0].max() + vertex[0].min()) / 2
        x_mid_point = (next_vertex[2].max() + vertex[2].min()) / 2
        return np.array([y_mid_point, 0, x_mid_point], dtype='f4')
