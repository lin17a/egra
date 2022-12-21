import pygame as pg
import moderngl as mgl
import glm
import sys
import itertools as it
import numpy as np
from OpenGL.GL import *


from Camera import Camera, Axis, DriverCamera, Minimap
from Circuito import Circuito, MinimapCircuito
from car_IA_2 import Car, MinimapCar


from Light import Light
from texturing import *
import time
from UI import menu
from Music import MusicPlayer
import glcontext

from AI import ai

import pandas as pd
import os



class GraphicsEngine:
    def __init__(self, win_size=(1280, 960)):
        # init pygame modules
        self.start = False
        pg.init()
        # window sizeq
        self.WIN_SIZE = win_size
        # clock
        self.clock = pg.time.Clock()
        self.time = 0
        self.start_menu()
        self.map = None
        self.players = None
        
        # Se crea la instancia
        
        self.end_game = False
        self.start_game_phase = False

        self.ingame_music = MusicPlayer("musica1", volume=0.0)
        self.menu_music = MusicPlayer("menu", volume=0.0)
        self.menu_music.play()

        self.off_track = []
        self.vel_data = []

    
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

        self.ai = ai(self, test = True)        
        # axis
        #self.axis = Axis(self)
        # Minimap
        
        self.minimap = Minimap(self)
        self.minimap_car = MinimapCar(self)
        self.minimap_scene = MinimapCircuito(self, self.scene.all_vertex, self.scene.color_vertex)
        
        self.ingame_music.load("musica1")
        self.ingame_music.play()
        self.winner = None

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
        self.winner = None

        self.change_camera()

    def get_time(self):
        self.time = pg.time.get_ticks() * 0.001
    
    def start_timer(self):
        self.start_time = self.time

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
            self.car_2.check_if_on_start_line()
            if self.camera_mode == "drive":
                self.minimap_car_2.up()
                self.minimap_car_2.on_init(player = 2)
                self.minimap_scene.render(player = 2)

        if keys[pg.K_r]:
            self.scene.zero_checkpoints()
            self.scene.new_road()
            self.minimap_scene.new_road(self.scene.all_vertex, self.scene.color_vertex)
            self.car.move_to_start()
            self.start_timer()
            self.minimap_car.move_to_start()
            
            if self.players == 2:
                self.car_2.move_to_start()
                self.minimap_car_2.move_to_start()

            # NOTE: Start again
            self.end_game = False

        if keys[pg.K_UP]:
            self.car.move_forward()
            radar = self.car.distance_to_off_circuit()
            radar.append(self.car.velocity)
            radar.append("-")
            radar = np.array(radar)
            
            #self.car.values.append(radar)
            self.start = True
            self.minimap_car.move_forward()
            
        if keys[pg.K_RIGHT]:
            self.car.move_right()
            self.minimap_car.move_right()
            radar = self.car.distance_to_off_circuit()
            radar.append(self.car.get_curviness())
            radar.append(2)
            radar = np.array(radar)
            
            self.car.values.append(radar)
            self.start = True
            
        if keys[pg.K_LEFT]:
            self.minimap_car.move_left()
            self.car.move_left()
            radar = self.car.distance_to_off_circuit()
            radar.append(self.car.get_curviness())
            radar.append(1)
            radar = np.array(radar)
            
            self.car.values.append(radar)
            self.start = True
            
        if keys[pg.K_DOWN]:
            self.car.move_backward()
            #self.car.move_backward()
            
        if (not keys[pg.K_UP]) and (not keys[pg.K_RIGHT]) and (not keys[pg.K_LEFT]):
            if self.start:
                radar = self.car.distance_to_off_circuit()
                radar.append(self.car.get_curviness())
                radar.append(0)
                radar = np.array(radar)
                
                self.car.values.append(radar)
            
        if keys[pg.K_g]:
            self.car.save()
            
        
        if self.camera_mode == "drive":
            self.minimap_car.up()
            self.minimap_car.on_init()
            self.minimap_scene.render()

        self.car.up()
        self.car.check_if_on_checkpoint()
        self.car.check_if_on_start_line()
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
                if self.players == 1:
                    self.one_player(players_color)
                elif self.players == 2:
                    self.two_players(players_color)
                self.start_game_phase = 2
        else:
            # clear framebuffer
            self.ctx.clear(color=(0, 0, 0))
            if self.players == 1:
                #"""
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
                #"""
                self.ai.run_car()
                
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

    def run(self):
        
        while True:
            self.get_time()
            self.check_events()
            self.render()
            
            self.clock.tick(60)

    def start_game(self):
        if self.start_game_phase == 2:
            self.start_timer()
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
            self.start_game_phase = False
            self.start_timer()

    #Change title of pygame window
    def change_title(self, time, checkpoint, velocity):
        if self.players == 1:
            if self.end_game:
                pg.display.set_caption("Time: {:.2f} - Game Over".format(self.last_time, checkpoint, velocity))
            else:
                self.last_time = time
                pg.display.set_caption("Time: {:.2f} - Checkpoint: {} - Velocity: {:.2f}".format(time, checkpoint, velocity))
        if self.players == 2:
            if self.end_game:
                pg.display.set_caption("Time: {:.2f} - Winner {}".format(self.last_time, self.winner.upper()))
            else:
                self.last_time = time
                pg.display.set_caption("Time: {:.2f} - Checkpoint: {} - Velocity: {:.2f} - Checkpoint: {} - Velocity: {:.2f}".format(time, checkpoint[0], velocity[0], checkpoint[1], velocity[1]))


    def end_game_logic(self):
        # NOTE: EVERYTHING inside this function is running inside a loop (game)

        # If all checkpoints are completed, end game
        if self.players == 1:
            current_n_checkpoints = np.count_nonzero(self.car.completed_checkpoints)
            total_n_checkpoints = len(self.car.completed_checkpoints)
            self.change_title(self.time - self.start_time, 
                            "{}/{}".format(current_n_checkpoints, total_n_checkpoints), 
                            self.car.physics.Vel[0])

            self.off_track.append(self.car.on_circuit())
            self.vel_data.append((round(self.car.physics.Vel[0], 2), round(self.time, 2)))

            if all(self.car.checkpoints_l) and self.car.crossed_finish:
                self.end_game = True
                # back to menu
                self.ingame_music.stop()
                self.start_menu()
                # save game stats
                self.save_stats()
                self.menu.set_menu(3)
                
        elif self.players == 2:
            current_n_checkpoints_1 = np.count_nonzero(self.car.completed_checkpoints)
            current_n_checkpoints_2 = np.count_nonzero(self.car_2.completed_checkpoints)
            total_n_checkpoints = len(self.car.completed_checkpoints)
            self.change_title(self.time - self.start_time, 
                            ("{}/{}".format(current_n_checkpoints_1, total_n_checkpoints), 
                            "{}/{}".format(current_n_checkpoints_2, total_n_checkpoints)), 
                            (self.car.physics.Vel[0], self.car_2.physics.Vel[0]))

            # TODO: Add off track stats for multiplayer

            if (all(self.car.completed_checkpoints) and self.car.crossed_finish) or \
                (all(self.car_2.completed_checkpoints) and self.car_2.crossed_finish):
                    self.end_game = True
                    # back to menu
                    self.ingame_music.stop()
                    self.start_menu()
                    # save game stats
                    self.save_stats()
                    

        if self.end_game:
            if self.players == 2:
                # check who has completed more checkpoints
                current_n_checkpoints = np.count_nonzero(self.car.completed_checkpoints)
                total_n_checkpoints = len(self.scene.checkpoints)
                if (current_n_checkpoints == total_n_checkpoints):
                    self.winner = self.car.color
                else:
                    self.winner = self.car_2.color
        
        
    def save_stats(self):
        if self.players == 1:
            vel_n_time = self.vel_data
            off_track_percent_car1 = round((self.off_track.count(False) / len(self.off_track)) * 100, 2)
            race_time = self.last_time

            # save data
            time_data = {'time':  [race_time]}
            off_track_percent_data = {'off_track_percent':  [off_track_percent_car1]}
            vel_n_time_data = {'time':  list(map(lambda x : x[1], vel_n_time)), 
                                'velocity' : list(map(lambda x : x[0], vel_n_time))}

            race_time_df = pd.DataFrame(time_data)
            off_track_df = pd.DataFrame(off_track_percent_data)
            vel_n_time_df = pd.DataFrame(vel_n_time_data)
            vel_n_time_df = vel_n_time_df.groupby(np.arange(len(vel_n_time_df)) // 4).mean()

            race_time_df.to_csv("./stats_data/race_time.csv")
            off_track_df.to_csv("./stats_data/off_track.csv")
            vel_n_time_df.to_csv("./stats_data/vel_n_time.csv")


        # TODO: Stats for multiplayer
        elif self.players == 2:
            #avg_car1_vel =
            #n_off_track_car1 =
            #race_time1 = self.ftime

            #avg_car2_vel =
            #n_off_track_car2 =
            #race_time2 = self.ftime
            pass

    def open_stats_dshb(self):
        pg.quit()
        file1 = "./stats_dashboard.py"
        os.system(f'streamlit run {file1}')

    def stopwatch(self, multi: bool):
        # TODO:

        # if not multi:
            # if not self.end_game and car is not moving and car in the start line:
                # start the timer
            # elif if self.end_game:
                # stop the timer

        # if multi:
            # if not self.end_game and car_1 is not moving and car_1 in the start line:
                # start car_1 timer
            # elif not self.end_game and car_2 is not moving and car_2 in the start line:
                # start car_2 timer
            # elif if self.end_game:
                # stop both cars timers and the lowest one is the winner
        pass

if __name__ == '__main__':
    app = GraphicsEngine()
    app.run()