import pygame as pg
import pygame_menu
import moderngl as mgl
import glm
import sys
import itertools as it
import numpy as np
from OpenGL.GL import *
from Camera import Camera, Axis, DriverCamera
from Circuito import Circuito
from car import Car
from Light import Light
from texturing import Grass, RaceTrackTexture
import time


class GraphicsEngine:
    def __init__(self, win_size=(1280, 960)):
        self.players = 0
        # init pygame modules
        pg.init()
        # clock
        self.clock = pg.time.Clock()
        self.time = 0
        # window sizeq
        self.WIN_SIZE = win_size
        self.iniciar_menu()

    def iniciar_menu(self):
        self.surface = pg.display.set_mode(self.WIN_SIZE)
        self.menu = pygame_menu.Menu(   height = 300, 
                                        theme = pygame_menu.themes.THEME_BLUE, 
                                        title = 'Menu', 
                                        width = 400
                                    )
        self.menu.add.button('Play One Player', self.play_one_player)
        self.menu.add.button('Play Two Player', self.play_two_player)
        self.menu.add.button('Quit', pygame_menu.events.EXIT)
        self.menu_activate = True


    def play_one_player(self):
        self.players = 1
        self.menu_activate = False
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
        self.camera_mode = "bird"
        # scene
        self.scene = Circuito(self)
        self.asphalt = RaceTrackTexture(self)
        self.grass = Grass(self)
        # Car
        self.light = Light()
        self.car = Car(self)
        # axis
        self.axis = Axis(self)

    def play_two_player(self):
        self.players = 2
        self.menu_activate = False
        # set opengl attr
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION,3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION,3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        # create opengl context
        pg.display.set_mode(self.WIN_SIZE, flags=pg.OPENGL | pg.DOUBLEBUF)
        # detect and use exixting opengl context
        self.ctx = mgl.create_context()
        # camera
        self.camera = Camera(self, player = 1)
        self.camera_mode = "bird"
        self.camera_2 = Camera(self, player = 2)
        # scene
        self.scene = Circuito(self)
        self.asphalt = RaceTrackTexture(self)
        self.grass = Grass(self)
        # Car
        self.light = Light()
        self.car = Car(self)
        self.car_2 = Car(self)
        # axis
        self.axis = Axis(self)

    def get_time(self):
        self.time = pg.time.get_ticks() * 0.001

    def change_camera(self):
        if self.players == 1:
            if self.camera_mode == "bird":
                self.camera_mode = "drive"
                self.camera = DriverCamera(self)
            else:
                self.camera_mode = "bird"
                self.camera = Camera(self)
        if self.players == 2:
            if self.camera_mode == "bird":
                self.camera_mode = "drive"
                self.camera = DriverCamera(self, player = 1)
                self.camera_2 = DriverCamera(self, player = 2)
            else:
                self.camera_mode = "bird"
                self.camera = Camera(self, player = 1)
                self.camera_2 = Camera(self, player = 2)


    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.scene.destroy()
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_c:
                self.change_camera()
            if event.type == pg.MOUSEWHEEL:
                self.camera.zoom(-event.y*3)
            if event.type == pg.KEYDOWN and event.key == pg.K_m:
                self.menu_activate = True
                self.surface = pg.display.set_mode(self.WIN_SIZE)

        keys = pg.key.get_pressed()
        if keys[pg.K_r]:
            self.scene.new_road()
            self.car.move_to_start()
            if self.players == 2:
                self.car_2.move_to_start()

        if self.players == 2:
            if keys[pg.K_w]:
                self.car_2.move_forward()
            if keys[pg.K_d]:
                self.car_2.move_right()
            if keys[pg.K_a]:
                self.car_2.move_left()
            if keys[pg.K_s]:
                self.car_2.move_backward()
            self.car_2.on_init()

        if keys[pg.K_UP]:
            self.car.move_forward()
        if keys[pg.K_RIGHT]:
            self.car.move_right()
        if keys[pg.K_LEFT]:
            self.car.move_left()
        if keys[pg.K_DOWN]:
            self.car.move_backward()

        self.car.on_init()
        if any(keys):
            self.camera.update()
        if any(keys) and self.players == 2:
            self.camera_2.update()
        self.asphalt.on_init()
        self.grass.on_init()
        self.scene.on_init()
        
    def render(self):
        # clear framebuffer
        self.ctx.clear(color=(0, 0, 0))
        if self.players == 1:
            # render scene
            self.grass.render()
            #self.asphalt.render()
            self.scene.render()
            # render car
            self.ctx.enable(mgl.DEPTH_TEST | mgl.CULL_FACE)
            self.car.render()
            self.ctx.disable(mgl.DEPTH_TEST | mgl.CULL_FACE)
            # render axis
            self.axis.render()
            # swap buffers
            pg.display.flip()

        if self.players == 2:
            self.camera.update()
            # render scene
            self.grass.render()
            #self.asphalt.render()
            self.scene.render()
            # render car
            self.ctx.enable(mgl.DEPTH_TEST | mgl.CULL_FACE)
            self.car.render()
            self.car_2.render()
            self.ctx.disable(mgl.DEPTH_TEST | mgl.CULL_FACE)
            # render axis
            self.axis.render()

            self.camera_2.update()
            # render scene
            self.grass.render()
            #self.asphalt.render()
            self.scene.render()
            # render car
            self.ctx.enable(mgl.DEPTH_TEST | mgl.CULL_FACE)
            self.car_2.render()
            self.car.render()
            self.ctx.disable(mgl.DEPTH_TEST | mgl.CULL_FACE)
            # render axis
            self.axis.render()
            # swap buffers
            pg.display.flip()


    def run(self):
        while True:
            while self.menu_activate:
                self.get_time()
                self.menu.mainloop(self.surface, disable_loop=True)
                self.clock.tick(60)

            while not self.menu_activate:
                self.get_time()
                self.check_events()
                self.render()
                self.clock.tick(60)


if __name__ == '__main__':
    app = GraphicsEngine()
    app.run()