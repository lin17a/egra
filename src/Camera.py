import math

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

    def update(self):
        pass


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
    def update(self):
        pass

    @staticmethod
    def get_center_vertex(vertex, next_vertex):
        y_mid_point = (next_vertex[0].max() + vertex[0].min()) / 2
        x_mid_point = (next_vertex[2].max() + vertex[2].min()) / 2
        return np.array([y_mid_point, 0, x_mid_point], dtype='f4')

class FollowCarCamera(Camera):
    def __init__(self, app):
        self.app = app
        self.aspect_ratio = app.WIN_SIZE[0] / app.WIN_SIZE[1]
        self.position = self.get_position()
        self.up = glm.vec3(0, 1, 0)
        self.lookat = self.get_look_at()
        self.radians = 110
        # view_matrix
        self.m_view = self.get_view_matrix()
        # projection matrix
        self.m_proj = self.get_projection_matrix()

    def update(self):
        self.position = self.get_position()
        self.lookat = self.get_look_at()
        self.m_view = self.get_view_matrix()
        self.m_proj = self.get_projection_matrix()

    def get_position(self):
        car_y, car_z, car_x = self.app.car.position
        car_rot = np.pi - self.app.car.rotation
        cam_rot = - ((car_rot % np.pi) - np.pi / 2) * 2 + np.pi # formula by experiment, doesn't work
        view_dir = glm.vec3(math.sin(cam_rot), 0, math.cos(cam_rot)) # y, z, x  # usually cam_rot, should be car_rot
        print('view dir:', view_dir)
        position = glm.vec3(car_y - 2 * view_dir[0], 1, car_x - 2 * view_dir[2]) # y, z, x
        print('camera: ', position)
        return position

    def get_look_at(self):
        car_rot = self.app.car.rotation
        #view_dir = glm.vec3(math.sin(car_rot), 0, math.cos(car_rot))
        cam_rot = -(car_rot - np.pi / 2) * 2
        view_dir = glm.vec3(math.sin(cam_rot), 0, math.cos(cam_rot))  # y, z, x
        return self.app.car.position


class Axis:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.scale = 100
        self.vbo = self.get_vbo()
        self.shader_program = self.get_shader_program()
        self.vao = self.get_vao()
        self.rotation = glm.radians(45)
        self.m_model = self.get_model_matrix()
        self.on_init()

    def get_model_matrix(self):
        m_model = glm.rotate(glm.mat4(), glm.radians(self.rotation), glm.vec3(0, 1, 0))
        return m_model

    def on_init(self):
        self.shader_program['m_proj'].write(self.app.camera.m_proj)
        self.shader_program['m_view'].write(self.app.camera.m_view)
        self.shader_program['m_model'].write(self.m_model)

    def destroy(self):
        self.vbo.release()
        self.shader_program.release()
        self.vao.release()

    def get_vao(self):
        vao = self.ctx.vertex_array(self.shader_program, [(self.vbo, '3f', 'in_position')])
        return vao

    @staticmethod
    def get_data(vertices, indices):
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo

    def render(self):
        self.vao.render(mgl.LINES)

    def get_vertex_data(self):
        vertices = [(0, 0, 0), (0, 0, self.scale), (0, self.scale, 0), (self.scale, 0, 0)]
        indices = [(0, 1), (0, 2), (0, 3)]
        vertex_data = self.get_data(vertices, indices)
        return vertex_data

    def get_shader_program(self):
        program = self.ctx.program(
            vertex_shader='''
                #version 330 core
                layout (location = 0) in vec3 in_position;
                layout (location = 1) in vec3 aColor;
                out vec3 ourColor;

                uniform mat4 m_proj;
                uniform mat4 m_view;
                uniform mat4 m_model;
                void main() {
                    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
                    ourColor = vec3(1 * vec4(in_position, 1.0).x, 1 * vec4(in_position, 1.0).y, 1 * vec4(in_position, 1.0).z );
                }
            ''',
            fragment_shader='''
                #version 330
                layout (location = 0) out vec4 fragColor;
                in vec3 ourColor;
                void main() { 
                    fragColor = vec4(ourColor,1.0);
                }
            ''',
        )
        return program
