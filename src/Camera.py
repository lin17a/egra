import glm
import numpy as np
import moderngl as mgl


class Camera:
    def __init__(self, app, player = None):
        self.app = app
        self.player = player
        if self.player == 1 or self.player == 2:
            self.aspect_ratio = app.WIN_SIZE[0]/(app.WIN_SIZE[1]/2)
        elif self.player == None:
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
    def __init__(self, app, player = None):
        self.app = app
        self.player = player
        if self.player == 1 or self.player == 2:
            self.aspect_ratio = app.WIN_SIZE[0]/(app.WIN_SIZE[1]/2)
        elif self.player == None:
            self.aspect_ratio = app.WIN_SIZE[0]/app.WIN_SIZE[1]          
        self.cam_dist = 5
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
        if self.player == 1 or self.player == None:
            car_x, car_z, car_y = self.app.car.position
            view_dir = self.app.car.direction_vector(self.app.car.rotation)
        elif self.player == 2:
            car_x, car_z, car_y = self.app.car_2.position
            view_dir = self.app.car_2.direction_vector(self.app.car_2.rotation)
        # TODO the cam dist needs to match the direction_vector dividing factor
        position = glm.vec3(car_x - self.cam_dist * view_dir[0], 1, car_y - self.cam_dist * view_dir[2])
        #print("--> get camera position")
        #print("rotation:", self.app.car.rotation)
        #print("car position:", self.app.car.position)
        #print('direction:', view_dir)
        #print('camera position:', position)
        return position

    def get_look_at(self):
        if self.player == 1 or self.player == None:
            return self.app.car.position
        elif self.player == 2:
            return self.app.car_2.position

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
