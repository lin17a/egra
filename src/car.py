# basado en: https://www.youtube.com/watch?v=eJDIsFJN4OQ
import glm

import numpy as np


class Vehicle:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        # init car positions
        self.x = 0
        self.y = 0
        self.z = 0
        self.degree = 0
        self.translate = glm.translate(glm.mat4(), glm.vec3(self.x, self.y, self.z))
        self.rotation = glm.rotate(glm.mat4(), glm.radians(self.degree), glm.vec3(0, 1, 0))
        self.vbo = self.get_vbo()
        self.shader_program = self.get_shader_program()
        self.vao = self.get_vao()
        self.m_model = self.get_model_matrix()
        self.on_init()

    def get_model_matrix(self):
        # m_model = glm.mat4()
        """
        Aquí debemos establecer el movimiento del coche con
        una transformación respecto al eje de las Y con desplazamiento
        hacia los ejes X y Z
        """
        m_model = self.rotation * self.translate
        return m_model

    def on_init(self):
        self.shader_program['m_proj'].write(self.app.camera.m_proj)
        self.shader_program['m_view'].write(self.app.camera.m_view)
        self.shader_program['m_model'].write(self.m_model)

    def render(self):
        self.vao.render()

    def destroy(self):
        self.vbo.release()
        self.shader_program.release()
        self.vao.release()

    def get_vao(self):
        vao = self.ctx.vertex_array(self.shader_program, [(self.vbo, '3f 3f', 'in_colors', 'in_position')])
        return vao

    def move_right(self):
        self.degree -= 0.5
        self.rotation = glm.rotate(glm.mat4(), glm.radians(self.degree), glm.vec3(0, 1, 0))
        self.shader_program['m_model'].write(self.get_model_matrix())

    def move_left(self):
        self.degree += 0.5
        self.rotation = glm.rotate(glm.mat4(), glm.radians(self.degree), glm.vec3(0, 1, 0))
        self.shader_program['m_model'].write(self.get_model_matrix())

    def move_forward(self):
        self.z -= 0.05
        self.translate = glm.translate(glm.mat4(), glm.vec3(self.x, self.y, self.z))
        self.shader_program['m_model'].write(self.get_model_matrix())

    def get_vertex_data(self):

        vertices = [(0, 0, 0), (0, 0, 10), (5, 0, 0), (5, 0, 10),  # Car
                    (0.7, 0, 2.5), (4.3, 0, 2.5), (1.2, 0, 4), (3.8, 0, 4),  # front window
                    (0.7, 0, 7.5), (4.3, 0, 7.5), (1.2, 0, 6), (3.8, 0, 6),  # back window
                    (0.7, 0, 2.8), (1.2, 0, 4.3), (0.7, 0, 7.2), (1.2, 0, 5.7),  # left window
                    (4.3, 0, 2.8), (3.8, 0, 4.3), (4.3, 0, 7.2), (3.8, 0, 5.7),  # right window
                    (0.7, 0, 0), (1.2, 0, 0), (0.7, 0, 0.15), (1.2, 0, 0.15),  # left front light
                    (4.3, 0, 0), (3.8, 0, 0), (4.3, 0, 0.15), (3.8, 0, 0.15),  # right front light
                    (0.7, 0, 10), (1.2, 0, 10), (0.7, 0, 9.85), (1.2, 0, 9.85),  # left back light
                    (4.3, 0, 10), (3.8, 0, 10), (4.3, 0, 9.85), (3.8, 0, 9.85)]  # right back light

        indices = [(0, 1, 2), (1, 3, 2),
                   (4, 5, 6), (5, 6, 7),
                   (8, 9, 10), (9, 10, 11),
                   (12, 13, 14), (13, 14, 15),
                   (16, 17, 18), (17, 18, 19),
                   (20, 21, 22), (21, 22, 23),
                   (24, 25, 26), (25, 26, 27),
                   (28, 29, 30), (29, 30, 31),
                   (32, 33, 34), (33, 34, 35)]

        colors = [(0.7, 0, 0.1), (0.7, 0, 0.1),
                  (0, 0, 0), (0, 0, 0),
                  (0, 0, 0), (0, 0, 0),
                  (0, 0, 0), (0, 0, 0),
                  (0, 0, 0), (0, 0, 0),
                  (1, 1, 0), (1, 1, 0),
                  (1, 1, 0), (1, 1, 0),
                  (1, 0, 0), (1, 0, 0),
                  (1, 0, 0), (1, 0, 0)]

        vertex_data = self.get_data(vertices, indices, colors)

        return vertex_data

    @staticmethod
    def get_data(vertices, indices, colors):
        data = []
        for t, triangle in enumerate(indices):
            for ind in triangle:
                data.append(colors[t] + vertices[ind])
        data_np = np.array(data, dtype='f4')
        return data_np

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo

    def get_shader_program(self):
        program = self.ctx.program(
            vertex_shader='''
                #version 330
                layout (location = 0) in vec3 in_position;
                layout (location = 1) in vec3 in_colors;
                out vec3 color;
                uniform mat4 m_proj;
                uniform mat4 m_view;
                uniform mat4 m_model;
                void main() {
                    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
                    color = in_colors;
                }
            ''',
            fragment_shader='''
                #version 330
                #extension GL_ARB_separate_shader_objects : require
                layout (location = 0) out vec4 fragColor;
                in vec3 color;
                void main() {
                    fragColor = vec4(color, 1.0);
                }
            ''',
        )
        return program
