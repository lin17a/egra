# basado en: https://www.youtube.com/watch?v=eJDIsFJN4OQ
import pygame as pg
import moderngl as mgl
import glm
import sys
import random
import itertools as it
import numpy as np
from generation import generation_track
import time
from OpenGL.GL import *


class Camera:
    def __init__(self, app):
        self.app = app
        self.aspec_ratio = app.WIN_SIZE[0]/app.WIN_SIZE[1]
        self.position =glm.vec3(0,10,0)
        self.up = glm.vec3(1,0,0)
        self.lookat = glm.vec3(0)
        self.radians = 170
        # view_matrix
        self.m_view = self.get_view_matrix()
        # projection matrix
        self.m_proj = self.get_projection_matrix()
        
    def get_view_matrix(self):
        return glm.lookAt(self.position, self.lookat, self.up)
    
    def get_projection_matrix(self):
        return glm.perspective(glm.radians(self.radians), self.aspec_ratio, 0.1, 100)

    def rotate(self, vec):
        if 180 > self.radians + vec[0] + vec[1] > 0:
            self.radians = self.radians + vec[0] + vec[1]
            self.m_proj = self.get_projection_matrix()

    """    def move_forward(self):
        self.position = self.position + glm.vec3((0, 0.1/self.radians, 0))
        self.m_view = self.get_view_matrix()
    
    def move_backward(self):
        self.position = self.position + glm.vec3((0, -0.1/self.radians, 0))
        self.m_view = self.get_view_matrix()"""
    
    def move_right(self):
        self.lookat = self.lookat + glm.vec3((0, 0, 0.0001*self.radians))
        self.position = self.position + glm.vec3((0, 0, 0.0001*self.radians))
        self.m_view = self.get_view_matrix()

    def move_left(self):
        self.lookat = self.lookat + glm.vec3((0, 0, -0.0001*self.radians))
        self.position = self.position + glm.vec3((0, 0, -0.0001*self.radians))
        self.m_view = self.get_view_matrix()

    def move_up(self):
        self.lookat = self.lookat + glm.vec3((0.0001*self.radians, 0, 0))
        self.position = self.position + glm.vec3((0.0001*self.radians, 0, 0))
        self.m_view = self.get_view_matrix()
    
    def move_down(self):
        self.lookat = self.lookat + glm.vec3((-0.0001*self.radians, 0, 0))
        self.position = self.position + glm.vec3((-0.0001*self.radians, 0, 0))
        self.m_view = self.get_view_matrix()

class Object:
    def __init__(self,app):
        self.app = app
        self.ctx = app.ctx
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
        self.vao.render(mgl.LINE_LOOP)
        
    def destroy (self):
        self.vbo.release()
        self.shader_program.release()
        self.vao.release()
    
    def get_vao(self):
        vao = self.ctx.vertex_array(self.shader_program, [(self.vbo, '3f', 'in_position')])
        return vao

    def get_vertex_data(self):
        #Cubic Hermite spline
        #Finite difference
        vertices, indices = generation_track()
        vertices = [(29, 42), (65, 66), (8, 56), (5, 77), (50, 60), (59, 32), (92, 52), (13, 6), (17, 61), (6, 54)]
        indices = [(0, 8), (0, 7), (1, 4), (1, 6), (2, 8), (2, 9), (3, 9), (3, 4), (5, 6), (5, 7)]

        v = []
        sig = 0
        for _ in range(len(indices)):
            for indice in indices:
                if sig in indice:
                    if sig == indice[0]:
                        sig = indice[1]
                    else:
                        sig = indice[0]
                    indices.remove(indice)
                    break
            v.append(np.array(vertices[sig]))
        vertices = v+v[:3]

        vertex_data = []
        for k in range(1, len(vertices)-2):
            xk, xk1 = 0, 10000
            mk = 1/2*((vertices[k+1]-vertices[k])/(xk1-xk) + (vertices[k]-vertices[k-1])/(xk1-xk))
            mk1 = 1/2*((vertices[k+2]-vertices[k+1])/(xk1-xk) + (vertices[k+1]-vertices[k])/(xk1-xk))
            for t_int in range(0, 1000):
                t = t_int/1000
                h00 = (1+2*t)*(1-t)**2
                h10 = t*(1-t)**2
                h01 = t**2*(3-2*t)
                h11 = t**2*(t-1)
                p = h00*vertices[k] + h10*(xk1-xk)*mk + h01*vertices[k+1] + h11*(xk1-xk)*mk1
                vertex_data.append([p[0], 0, p[1]])

        vertex_data = np.array(vertex_data, dtype='f4')
        return vertex_data
    
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
    
        
class GraphicsEngine:
    def __init__(self, win_size=(900,900)):
        # init pygame modules
        pg.init()
        # window size
        self.WIN_SIZE = win_size
        # set opengl attr
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION,3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION,3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        # create opengl context
        pg.display.set_mode(self.WIN_SIZE, flags=pg.OPENGL | pg.DOUBLEBUF)
        # detect and use exixting opengl context
        self.ctx = mgl.create_context()
        # camera
        self.camera = Camera(self)
        # scene
        self.scene = Object(self)

        
        
    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.scene.destroy()
                pg.quit()
                sys.exit()

        left, middle, right = pg.mouse.get_pressed()
        keys = pg.key.get_pressed()
        if left:
            mouseMove = pg.mouse.get_rel()
            self.camera.rotate(mouseMove)
        if keys[pg.K_w]:
            self.camera.move_up()
        if keys[pg.K_s]:
            self.camera.move_down()
        if keys[pg.K_d]:
            self.camera.move_right()
        if keys[pg.K_a]:
            self.camera.move_left()
        self.scene.on_init()

    def render(self):
        # clear framebuffer
        self.ctx.clear(color=(1,1,1))
        # render scene
        self.scene.render()
        # swap buffers
        pg.display.flip()


    def run(self):
        while True:
            self.check_events()
            self.render()


if __name__ == '__main__':
    app = GraphicsEngine()
    app.run()
