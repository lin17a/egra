import pygame as pg
import pygame_menu
from pygame_menu import Theme

class menu:
    def __init__(self, app):
        self.app = app
        self.players = 1
        self.play = False
        self.map = "field"
        font = pygame_menu.font.FONT_MUNRO
        mytheme = Theme(background_color=(0, 0, 0, 0), 
                        widget_font=font)
        myimage = pygame_menu.baseimage.BaseImage(
                    image_path=r"./textures/sb.jpg",
                    drawing_mode=pygame_menu.baseimage.IMAGE_MODE_REPEAT_XY
                )
        mytheme.background_color = myimage
        self.menu = pygame_menu.Menu(   height = 960, 
                                        theme = mytheme, 
                                        title = 'Race Driving Simulator', 
                                        width = 1280
                                    )
        self.menu.add.selector('Players:', ["1", "2"], onchange=self.set_player)
        self.menu.add.selector('Maps:', [("Field", 1), ("Sunset", 2), ("Desert", 3)], onchange=self.set_map)
        self.menu.add.button('Start', self.start)
        self.menu.add.button('Quit', pygame_menu.events.EXIT)

    def set_player(self, players):
        self.players = int(players[0])

    def set_map(self, map, _):
        self.map = map[0][0].lower()

    def start(self):
        self.play = True

    def render(self):
        self.menu.mainloop(self.app.surface, disable_loop = True)
        return self.players, self.play, self.map

