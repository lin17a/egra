# basado en: https://www.youtube.com/watch?v=eJDIsFJN4OQ
import pygame as pg
import moderngl as mgl
import glm
import sys

import numpy as np


class Camera:
    def __init__(self, app):
        self.app = app
        self.aspect_ratio = app.WIN_SIZE[0] / app.WIN_SIZE[1]
        self.position = glm.vec3(0, 100, 0)
        self.up = glm.vec3(0, 0, -1)
        # view_matrix
        self.m_view = self.get_view_matrix()
        # projection matrix
        self.m_proj = self.get_projection_matrix()

    def get_view_matrix(self):
        return glm.lookAt(self.position, glm.vec3(0), self.up)

    def get_projection_matrix(self):
        return glm.perspective(glm.radians(20), self.aspect_ratio, 10, 100)


class Object:
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
        self.move = False
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

    def update(self):
        if self.move:
            self.z -= 0.05
        self.translate = glm.translate(glm.mat4(), glm.vec3(self.x,
                                                            self.y,
                                                            self.z))
        self.shader_program['m_model'].write(self.get_model_matrix())

    def render(self):
        self.update()
        self.vao.render()

    def destroy(self):
        self.vbo.release()
        self.shader_program.release()
        self.vao.release()

    def get_vao(self):
        vao = self.ctx.vertex_array(self.shader_program, [(self.vbo, '3f 3f', 'in_colors', 'in_position')])
        return vao

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


class GraphicsEngine:
    def __init__(self, win_size=(600, 600)):
        # init pygame modules
        pg.init()
        # window size
        self.WIN_SIZE = win_size
        # set opengl attr
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        # create opengl context
        pg.display.set_mode(self.WIN_SIZE, flags=pg.OPENGL | pg.DOUBLEBUF)
        # detect and use exixting opengl context
        self.ctx = mgl.create_context()
        # clock
        self.clock = pg.time.Clock()
        self.time = 0
        # camera
        self.camera = Camera(self)
        # scene
        self.scene = Object(self)

    def get_time(self):
        self.time = pg.time.get_ticks() * 0.001

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.scene.destroy()
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.scene.move = not self.scene.move
            if event.type == pg.KEYDOWN and event.key == pg.K_UP:
                # UP
                self.scene.z -= 0.5
                self.scene.translate = glm.translate(glm.mat4(), glm.vec3(self.scene.x,
                                                                          self.scene.y,
                                                                          self.scene.z))
                self.scene.shader_program['m_model'].write(self.scene.get_model_matrix())
            """
            if event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
                # DOWN
                self.scene.z += 0.5
                self.scene.translate = glm.translate(glm.mat4(), glm.vec3(self.scene.x,
                                                                          self.scene.y,
                                                                          self.scene.z))
                self.scene.shader_program['m_model'].write(self.scene.get_model_matrix())
            """
            if event.type == pg.KEYDOWN and event.key == pg.K_RIGHT:
                # RIGHT
                self.scene.degree -= 5
                self.scene.rotation = glm.rotate(glm.mat4(), glm.radians(self.scene.degree), glm.vec3(0, 1, 0))
                """
                self.scene.x += 0.5
                self.scene.translate = glm.translate(glm.mat4(), glm.vec3(self.scene.x,
                                                                          self.scene.y,
                                                                          self.scene.z))
                """
                self.scene.shader_program['m_model'].write(self.scene.get_model_matrix())
            if event.type == pg.KEYDOWN and event.key == pg.K_LEFT:
                # LEFT
                self.scene.degree += 5
                self.scene.rotation = glm.rotate(glm.mat4(), glm.radians(self.scene.degree), glm.vec3(0, 1, 0))
                """
                self.scene.x -= 0.5
                self.scene.translate = glm.translate(glm.mat4(), glm.vec3(self.scene.x,
                                                                          self.scene.y,
                                                                          self.scene.z))
                """
                self.scene.shader_program['m_model'].write(self.scene.get_model_matrix())

    def render(self):
        # clear framebuffer
        self.ctx.clear(color=(0, 0, 0))
        # render scene
        self.scene.render()
        # swap buffers
        pg.display.flip()

    def run(self):
        while True:
            self.get_time()
            self.check_events()
            self.render()
            self.clock.tick(60)


if __name__ == '__main__':
    app = GraphicsEngine()
    app.run()
