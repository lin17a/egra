import pygame as pg
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
from texturing import *
import time
from UI import menu
from Music import MusicPlayer
import glcontext


class GraphicsEngine:
    def __init__(self, win_size=(1280, 960)):
        # init pygame modules
        pg.init()
        # window sizeq
        self.WIN_SIZE = win_size
        # clock
        self.clock = pg.time.Clock()
        self.time = 0
        self.start_menu()
        self.map = None
        self.players = None

        # Sounds
        self.ingame_music = MusicPlayer("musica1", volume=0.5)
        self.menu_music = MusicPlayer("menu", volume=0.3)
        self.menu_music.play()

    def start_menu(self):
        self.surface = pg.display.set_mode(self.WIN_SIZE)
        self.menu = menu(self)
        self.menu_active = True
        
    def one_player(self):
        # set opengl attr
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION,3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION,3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        # create opengl context
        self.surface = pg.display.set_mode(self.WIN_SIZE, flags=pg.OPENGL | pg.DOUBLEBUF)
        # detect and use exixting opengl context
        self.ctx = mgl.create_context()
        # camera
        self.camera = Camera(self)
        self.camera_mode = "bird"
        # scene
        self.scene = Circuito(self)
        self.skybox = Skybox(self, self.map)
        self.grass = Grass(self, self.map)
        # Car
        self.light = Light(self.map)
        self.car = Car(self)
        # axis
        #self.axis = Axis(self)

        self.change_camera()

    def two_players(self):
        # set opengl attr
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION,3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION,3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        # create opengl context
        self.surface = pg.display.set_mode(self.WIN_SIZE, flags=pg.OPENGL | pg.DOUBLEBUF)
        # detect and use exixting opengl context
        self.ctx = mgl.create_context()
        # camera
        self.camera = Camera(self, player = 1)
        self.camera_2 = Camera(self, player = 2)
        self.camera_mode = "bird"
        # scene
        self.scene = Circuito(self)
        self.skybox = Skybox(self, self.map)
        self.grass = Grass(self, self.map)
        # Car
        self.light = Light(self.map)
        self.car = Car(self, player = 1)
        self.car_2 = Car(self, player = 2)
        # axis
        #self.axis = Axis(self)

        self.change_camera()

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
        if self.menu_active:
            return
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.scene.destroy()
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_c:
                self.change_camera()
            if event.type == pg.KEYDOWN and event.key == pg.K_m:
                self.start_menu()
            if event.type == pg.MOUSEWHEEL:
                self.camera.zoom(-event.y*3)
                self.camera_2.zoom(-event.y*3)

        keys = pg.key.get_pressed()

        # if self.camera_mode == "bird":
        #     if keys[pg.K_w]:
        #         self.camera.move_up()
        #     if keys[pg.K_a]:
        #         self.camera.move_left()
        #     if keys[pg.K_s]:
        #         self.camera.move_down()
        #     if keys[pg.K_d]:
        #         self.camera.move_right()

        if self.players == 2:
            if keys[pg.K_w]:
                self.car_2.move_forward()
            if keys[pg.K_d]:
                self.car_2.move_right()
            if keys[pg.K_a]:
                self.car_2.move_left()
            if keys[pg.K_s]:
                self.car_2.move_backward()
            self.car_2.up()
            self.car_2.on_init()


        if keys[pg.K_r]:
            self.scene.new_road()
            self.car.move_to_start()
            if self.players == 2:
                self.car_2.move_to_start()

        if keys[pg.K_UP]:
            self.car.move_forward()
        if keys[pg.K_RIGHT]:
            self.car.move_right()
        if keys[pg.K_LEFT]:
            self.car.move_left()
        if keys[pg.K_DOWN]:
            self.car.move_backward()            
        
        self.car.up()
        self.car.on_init()
        self.grass.on_init()
        self.skybox.on_init()
        self.scene.on_init()
        
    def render(self):
        if self.menu_active:
            self.players, play, self.map = self.menu.render()
            if play:
                self.menu_active = False
                self.menu_music.stop()
                self.ingame_music.load("musica1")
                self.ingame_music.play()
                if self.players == 1:
                    self.one_player()
                elif self.players == 2:
                    self.two_players()
        else:
            # clear framebuffer
            self.ctx.clear(color=(0, 0, 0))
            if self.players == 1:
                self.camera.update()
                self.skybox.render(player = 1)
                # render scene
                self.grass.render(player = 1)
                #self.asphalt.render()
                self.scene.render(player = 1)
                # render car
                self.ctx.enable(mgl.DEPTH_TEST | mgl.CULL_FACE)
                self.car.render(player = 1)
                self.ctx.disable(mgl.DEPTH_TEST | mgl.CULL_FACE)
                # render axis
                #self.axis.render()
                # swap buffers
                pg.display.flip()

            if self.players == 2:                
                self.ctx.viewport = (0, self.WIN_SIZE[1]//2, self.WIN_SIZE[0], self.WIN_SIZE[1]//2)
                self.camera.update()
                # render scene
                self.skybox.render(player = 2)
                self.grass.render(player = 2)
                #self.asphalt.render()
                self.scene.render(player = 1)
                # render car
                self.ctx.enable(mgl.DEPTH_TEST | mgl.CULL_FACE)
                self.car.render(player=1)
                self.car_2.render(player=1)
                self.ctx.disable(mgl.DEPTH_TEST | mgl.CULL_FACE)
                # render axis
                #self.axis.render()

                self.ctx.viewport = (0, 0, self.WIN_SIZE[0], self.WIN_SIZE[1]//2)
                self.camera_2.update()
                # render scene
                self.skybox.render(player = 1)
                self.grass.render(player = 1)
                #self.asphalt.render()
                self.scene.render(player = 2)
                # render car
                self.ctx.enable(mgl.DEPTH_TEST | mgl.CULL_FACE)
                self.car.render(player=2)
                self.car_2.render(player=2)
                self.ctx.disable(mgl.DEPTH_TEST | mgl.CULL_FACE)
                # render axis
                #self.axis.render()

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