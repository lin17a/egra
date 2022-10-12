import pygame as pg
import moderngl as mgl
import glm
import sys
import itertools as it
import numpy as np
from OpenGL.GL import *
from Camera import Camera
from Circuito import Circuito
        
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
        self.scene = Circuito(self)
        # clock
        self.clock = pg.time.Clock()
        self.time = 0

    def get_time(self):
        self.time =pg.time.get_ticks() * 0.001

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
        if keys[pg.K_r]:
            self.scene.new_road()
        self.scene.on_init()

    def render(self):
        # clear framebuffer
        self.ctx.clear(color=(86/256,125/256,70/256))
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