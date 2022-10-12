import glm
import moderngl as mgl
from generation import generation_track
import numpy as np


class Circuito:
    def __init__(self,app):
        self.app = app
        self.ctx = app.ctx
        self.edgy = 0.1
        self.rad = 0.1
        self.vbo = self.get_vbo()
        self.shader_program = self.get_shader_program()
        self.vao = self.get_vao()
        self.m_model = self.get_model_matrix()
        self.on_init()
        
    def get_model_matrix(self):
        m_model = glm.rotate(glm.mat4(),glm.radians(0),glm.vec3(0,1,0))
        return m_model
        
    def on_init(self):
        self.shader_program['m_proj'].write(self.app.camera.m_proj)
        self.shader_program['m_view'].write(self.app.camera.m_view)
        self.shader_program['m_model'].write(self.m_model)

    def render(self):
        self.vao.render(mgl.TRIANGLE_STRIP)
        #self.vao.render(mgl.POINTS)
        
    def destroy (self):
        self.vbo.release()
        self.shader_program.release()
        self.vao.release()
    
    def get_vao(self):
        vao = self.ctx.vertex_array(self.shader_program, [(self.vbo, '3f', 'in_position')])
        return vao

    def get_vertex_data(self):
        xs, ys = generation_track(10, self.rad, self.edgy)

        vertex_data = np.array([np.array([x, 0, y]) for x, y in zip(xs, ys)], dtype='f4')
        print(vertex_data)

        vertex_2d = []
        weight = 1
        for i in range(len(vertex_data)-1):
            vec = vertex_data[i]-vertex_data[i+1]
            vec1 = np.array([-vec[2], 0, vec[0]])
            vec2 = np.array((vec[2], 0, -vec[0]))
            module = sum(vec1**2)**(1/2)+sum(vec2**2)**(1/2)
            if module==0:
                continue
            vertex_2d.append(vertex_data[i]+vec1/module*weight)
            vertex_2d.append(vertex_data[i]+vec2/module*weight)
        vertex_2d = vertex_2d + vertex_2d[:-2]
        vertex_2d = np.array(vertex_2d, dtype='f4')
        return vertex_2d

    def new_road(self):
        print("edgy",self.edgy,"rad",self.rad)
        self.vbo = self.get_vbo()
        self.vao = self.get_vao()
        self.render()

    
    @staticmethod
    def get_data(vertices, indices): 
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo
    
    def get_shader_program(self):
        program = self.ctx.program(    
            vertex_shader='''
                #version 330
                #extension GL_PROGRAM_POINT_SIZE: enable
                layout (location = 0) in vec3 in_position;
                uniform mat4 m_proj;
                uniform mat4 m_view;
                uniform mat4 m_model;
                void main() {
                    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                layout (location = 0) out vec4 fragColor;
                void main() { 
                    vec3 color = vec3(0,0,0);
                    fragColor = vec4(color,1.0);
                }
            ''',
        )
        return program