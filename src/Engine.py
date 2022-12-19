import pygame as pg
import moderngl as mgl
import glm
import sys
import itertools as it
import numpy as np
from OpenGL.GL import *
from Camera import Camera, Axis, DriverCamera, Minimap
from Circuito import Circuito, MinimapCircuito
from car import Car, MinimapCar
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
        self.end_game = False
        self.start_game_phase = False

        # Sounds
        self.ingame_music = MusicPlayer("musica1", volume=0.5)
        self.menu_music = MusicPlayer("menu", volume=0.3)
        self.menu_music.play()

    def start_menu(self):
        self.surface = pg.display.set_mode(self.WIN_SIZE)
        self.menu = menu(self)
        self.menu_active = True
        
    def one_player(self, players_color):
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
        self.camera_2 = None
        self.camera_mode = "bird"
        # scene
        self.scene = Circuito(self)
        self.skybox = Skybox(self, self.map)
        self.grass = Grass(self, self.map)
        # Car
        self.light = Light(self.map)
        self.car = Car(self, color = players_color[1])
        # Minimap
        self.minimap = Minimap(self)
        self.minimap_car = MinimapCar(self)
        self.minimap_scene = MinimapCircuito(self, self.scene.all_vertex, self.scene.color_vertex)
        # Music
        self.ingame_music.load("musica1")
        self.ingame_music.play()

        self.change_camera()

    def two_players(self, players_color):
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
        self.car = Car(self, player = 1, color = players_color[1])
        self.car_2 = Car(self, player = 2, color = players_color[2])
        # Minimap
        self.minimap = Minimap(self, player = 1)
        self.minimap_2 = Minimap(self, player = 2)
        self.minimap_car = MinimapCar(self, player = 1, color = players_color[1])
        self.minimap_car_2 = MinimapCar(self, player = 2, color = players_color[2])
        self.minimap_scene = MinimapCircuito(self, self.scene.all_vertex, self.scene.color_vertex)
        # Music
        self.ingame_music.load("musica1")
        self.ingame_music.play()

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
                self.camera = DriverCamera(self, player = 1, radians = 82)
                self.camera_2 = DriverCamera(self, player = 2, radians = 82)
            else:
                self.camera_mode = "bird"
                self.camera = Camera(self, player = 1)
                self.camera_2 = Camera(self, player = 2)

    def check_events(self):
        if self.menu_active:
            return
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.scene.destroy()
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_c:
                self.change_camera()
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.menu_music.load("menu")
                self.menu_music.play()
                self.start_menu()
            if event.type == pg.MOUSEWHEEL:
                self.camera.zoom(-event.y*3)
                if self.players == 2:
                    self.camera_2.zoom(-event.y*3)

        if self.start_game_phase:
            return

        keys = pg.key.get_pressed()

        if self.players == 2:
            if keys[pg.K_w]:
                self.car_2.move_forward()
                self.minimap_car_2.move_forward()
            if keys[pg.K_d]:
                self.car_2.move_right()
                self.minimap_car_2.move_right()
            if keys[pg.K_a]:
                self.car_2.move_left()
                self.minimap_car_2.move_left()
            if keys[pg.K_s]:
                self.car_2.move_backward()
                self.minimap_car_2.move_backward()
            self.car_2.up()
            self.car_2.on_init()
            self.car_2.check_if_on_checkpoint()
            if self.camera_mode == "drive":
                self.minimap_car_2.up()
                self.minimap_car_2.on_init(player = 2)
                self.minimap_scene.render(player = 2)

        if keys[pg.K_r]:
            self.scene.new_road()
            self.minimap_scene.new_road(self.scene.all_vertex, self.scene.color_vertex)
            self.car.move_to_start()
            self.minimap_car.move_to_start()
            if self.players == 2:
                self.car_2.move_to_start()
                self.minimap_car_2.move_to_start()
            # NOTE: Start again
            self.end_game = False
            self.start_timer = time.time()

        if keys[pg.K_UP]:
            self.car.move_forward()
            self.minimap_car.move_forward()
        if keys[pg.K_RIGHT]:
            self.car.move_right()
            self.minimap_car.move_right()
        if keys[pg.K_LEFT]:
            self.car.move_left()
            self.minimap_car.move_left()
        if keys[pg.K_DOWN]:
            self.car.move_backward()
            self.minimap_car.move_backward()
        
        if self.camera_mode == "drive":
            self.minimap_car.up()
            self.minimap_car.on_init()
            self.minimap_scene.render()

        self.car.up()
        self.car.check_if_on_checkpoint()
        self.car.on_init()
        self.grass.on_init()
        self.skybox.on_init()
        self.scene.on_init()

    def render(self):
        if self.menu_active:
            self.players, play, self.map, players_color = self.menu.render()
            if play:
                self.menu_active = False
                self.menu_music.stop()
                loading_screen(self.surface)
                # FIXME: start time
                self.start_timer = time.time()
                if self.players == 1:
                    self.one_player(players_color)
                elif self.players == 2:
                    self.two_players(players_color)
                self.start_game_phase = 2
        else:
            # clear framebuffer
            self.ctx.clear(color=(0, 0, 0))
            if self.players == 1:
                self.ctx.viewport = (0, 0, self.WIN_SIZE[0], self.WIN_SIZE[1])
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
                if self.camera_mode == "drive":
                    # render minimap
                    self.ctx.viewport = (int(self.WIN_SIZE[0] * 0.65), int(self.WIN_SIZE[1] * 0.6), int(self.WIN_SIZE[0] * 0.4), int(self.WIN_SIZE[1] * 0.4))
                    self.minimap.update()
                    self.minimap_scene.render(player = 1)
                    self.ctx.enable(mgl.DEPTH_TEST | mgl.CULL_FACE)
                    self.minimap_car.render()
                    self.ctx.disable(mgl.DEPTH_TEST | mgl.CULL_FACE)
                # swap buffers
                pg.display.flip()

            if self.players == 2:                
                self.ctx.viewport = (0, int(self.WIN_SIZE[1]//2), self.WIN_SIZE[0], int(self.WIN_SIZE[1]//2))
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
                if self.camera_mode == "drive":
                    # FIXME: Move minmap a little bit more to the left?
                    self.ctx.viewport = (0, int(self.WIN_SIZE[1] * 0.60), int(self.WIN_SIZE[0] * 0.4),
                                        int(self.WIN_SIZE[1]* 0.4))
                    self.minimap.update()
                    self.minimap_scene.render(player=1)
                    self.ctx.enable(mgl.DEPTH_TEST | mgl.CULL_FACE)
                    self.minimap_car.render()
                    self.minimap_car_2.render()
                    self.ctx.disable(mgl.DEPTH_TEST | mgl.CULL_FACE)

                self.ctx.viewport = (0, 0, self.WIN_SIZE[0], int(self.WIN_SIZE[1]//2))
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
                if self.camera_mode == "drive":
                    # render minimap
                    self.ctx.viewport = (int(self.WIN_SIZE[0] * 0.65), int(self.WIN_SIZE[1] * 0.1), int(self.WIN_SIZE[0] * 0.4),
                                        int(self.WIN_SIZE[1] * 0.4))
                    self.minimap_2.update()
                    self.minimap_scene.render(player=1)
                    self.ctx.enable(mgl.DEPTH_TEST | mgl.CULL_FACE)
                    self.minimap_car.render()
                    self.minimap_car_2.render()
                    self.ctx.disable(mgl.DEPTH_TEST | mgl.CULL_FACE)

                # swap buffers
                pg.display.flip()

            if self.start_game_phase:
                self.start_game()

            # Check if the game is over
            self.end_game_logic()
            # calculate stats
            self.stats()

    def run(self):
        while True:
            self.get_time()
            self.check_events()
            self.render()
            self.clock.tick(60)

    def start_game(self):
        if self.start_game_phase == 2:
            self.start_game_phase = 1
        else:
            time.sleep(1)
            print(3)
            time.sleep(1)
            print(2)
            time.sleep(1)
            print(1)
            time.sleep(1)
            print('Go')
            self.start_time = time.time()
            self.start_game_phase = False

    def end_game_logic(self):

        # If all checkpoints are completed, end game
        # FIXME: It only works the frist time, if you press R
        #        it stops working
        if self.players == 1:
            print(np.count_nonzero(self.car.completed_checkpoints))
            print(all(self.car.completed_checkpoints))
            if all(self.car.completed_checkpoints) and self.car.crossed_finish:
                self.end_game = True

        elif self.players == 2:
            if (all(self.car.completed_checkpoints) and self.car.crossed_finish) or \
                    (all(self.car_2.completed_checkpoints) and self.car_2.crossed_finish):
                    self.end_game = True
    
        if self.end_game:
            lap_time = time.time() - self.start_time
            print(lap_time)

            current_n_checkpoints = np.count_nonzero(self.car.completed_checkpoints)
            total_n_checkpoints = len(self.car.completed_checkpoints)
            print(f"\n\n--------------- END ----------------")

            if self.players == 2:
                # check who has completed more checkpoints
                chk_car_1 = np.count_nonzero(self.car.completed_checkpoints)
                chk_car_2 = np.count_nonzero(self.car_2.completed_checkpoints)
                if chk_car_1 > chk_car_2:
                    self.winner = self.car.color
                else:
                    self.winner = self.car_2.color

                print(f"======== {str(self.winner).upper()} player wins!  ========")
        

    def stats(self):
        """
        avg_car1_vel = 
        n_off_track_car1 =

        if self.players == 2:
            avg_car2_vel =
            n_off_track_car2 =

        self.winner.timer = 
        """

if __name__ == '__main__':
    app = GraphicsEngine()
    app.run()