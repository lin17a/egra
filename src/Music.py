import pygame as pg
from pygame import mixer


class MusicPlayer:
    def __init__(self, song, volume):
        self.music = pg.mixer.music.load(f"./sounds/{song}.mp3")
        self.volume = volume
    
    def load(self, song):
        pg.mixer.music.load(f"./sounds/{song}.mp3")

    def play(self):
        pg.mixer.music.play(-1)
        pg.mixer.music.set_volume(self.volume)

    def stop(self):
        pg.mixer.music.stop()