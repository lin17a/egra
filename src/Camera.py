import glm
import moderngl as mgl
import numpy as np


class Camera:
    def __init__(self, app):
        self.app = app
        self.aspect_ratio = app.WIN_SIZE[0]/app.WIN_SIZE[1]
        self.position = glm.vec3(0,60,0)
        self.up = glm.vec3(1,0,0)
        self.lookat = glm.vec3(0)
        self.FOV = 100
        # view_matrix
        self.m_view = self.get_view_matrix()
        # projection matrix
        self.m_proj = self.get_projection_matrix()
        
    def get_view_matrix(self):
        return glm.lookAt(self.position, self.lookat, self.up)
    
    def get_projection_matrix(self):
        return glm.perspective(glm.radians(self.FOV), self.aspect_ratio, 0.1, 100)

    def zoom(self, scroll):
        if 99 >= self.position[1]+scroll*0.5 >= 0:
            self.lookat = self.lookat + glm.vec3((0, scroll, 0))
            self.position = self.position + glm.vec3((0, scroll, 0))
            self.m_view = self.get_view_matrix()
    
    def move_right(self):
        self.lookat = self.lookat + glm.vec3((0, 0, 0.01*self.FOV))
        self.position = self.position + glm.vec3((0, 0, 0.01*self.FOV))
        self.m_view = self.get_view_matrix()

    def move_left(self):
        self.lookat = self.lookat + glm.vec3((0, 0, -0.01*self.FOV))
        self.position = self.position + glm.vec3((0, 0, -0.01*self.FOV))
        self.m_view = self.get_view_matrix()

    def move_up(self):
        self.lookat = self.lookat + glm.vec3((0.01*self.FOV, 0, 0))
        self.position = self.position + glm.vec3((0.01*self.FOV, 0, 0))
        self.m_view = self.get_view_matrix()
    
    def move_down(self):
        self.lookat = self.lookat + glm.vec3((-0.01*self.FOV, 0, 0))
        self.position = self.position + glm.vec3((-0.01*self.FOV, 0, 0))
        self.m_view = self.get_view_matrix()


class DriverCamera(Camera):
    def __init__(self, app, all_vertex, current_vertex_idx):
        self.app = app
        self.aspect_ratio = app.WIN_SIZE[0] / app.WIN_SIZE[1]
        self.all_vertex = all_vertex
        self.current_vertex_idx = (current_vertex_idx//2)*2
        self.current_vertex = self.get_center_vertex(self.all_vertex[self.current_vertex_idx],
                                                     self.all_vertex[self.current_vertex_idx+1])
        self.next_vertex_idx = ((self.current_vertex_idx+2)//2)*2
        self.next_vertex = self.get_center_vertex(all_vertex[self.next_vertex_idx],
                                                  self.all_vertex[self.next_vertex_idx+1])
        self.position = glm.vec3(self.current_vertex[0], 0.5, self.current_vertex[2])
        self.up = glm.vec3(0, 1, 0)
        self.lookat = glm.vec3(self.next_vertex[0], 0.4, self.next_vertex[2])
        self.FOV = 110
        # view_matrix
        self.m_view = self.get_view_matrix()
        # projection matrix
        self.m_proj = self.get_projection_matrix()

    def move_right(self):
        self.lookat = self.lookat + glm.vec3((0, 0, 0.01 * self.FOV))
        self.position = self.position + glm.vec3((0, 0, 0.01 * self.FOV))
        self.m_view = self.get_view_matrix()

    def move_left(self):
        self.lookat = self.lookat + glm.vec3((0, 0, -0.01 * self.FOV))
        self.position = self.position + glm.vec3((0, 0, -0.01 * self.FOV))
        self.m_view = self.get_view_matrix()

    def move_up(self):
        self.current_vertex_idx = ((self.current_vertex_idx + 2) % len(self.all_vertex))
        self.current_vertex = self.get_center_vertex(self.all_vertex[self.current_vertex_idx],
                                                     self.all_vertex[self.current_vertex_idx + 1])
        self.next_vertex_idx = ((self.current_vertex_idx + 2) % len(self.all_vertex))
        self.next_vertex = self.get_center_vertex(self.all_vertex[self.next_vertex_idx],
                                                  self.all_vertex[self.next_vertex_idx + 1])
        self.position = glm.vec3(self.current_vertex[0], 0.5, self.current_vertex[2])
        self.lookat = glm.vec3(self.next_vertex[0], 0.4, self.next_vertex[2])
        self.m_view = self.get_view_matrix()

    def move_down(self):
        self.current_vertex_idx = ((self.current_vertex_idx - 2) % len(self.all_vertex))
        self.current_vertex = self.get_center_vertex(self.all_vertex[self.current_vertex_idx],
                                                     self.all_vertex[self.current_vertex_idx + 1])
        self.next_vertex_idx = ((self.current_vertex_idx - 2) % len(self.all_vertex))
        self.next_vertex = self.get_center_vertex(self.all_vertex[self.next_vertex_idx],
                                                  self.all_vertex[self.next_vertex_idx + 1])
        self.position = glm.vec3(self.current_vertex[0], 0.5, self.current_vertex[2])
        self.lookat = glm.vec3(self.next_vertex[0], 0.4, self.next_vertex[2])
        self.m_view = self.get_view_matrix()

    @staticmethod
    def get_center_vertex(vertex, next_vertex):
        y_mid_point = (next_vertex[0].max() + vertex[0].min()) / 2
        x_mid_point = (next_vertex[2].max() + vertex[2].min()) / 2
        return np.array([y_mid_point, 0, x_mid_point], dtype='f4')
