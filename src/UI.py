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
                        widget_font=font, 
                        widget_font_size=50)
        myimage = pygame_menu.baseimage.BaseImage(
                    image_path=r"./textures/sb.jpg",
                    drawing_mode=pygame_menu.baseimage.IMAGE_MODE_REPEAT_XY
                )
        mytheme.background_color = myimage
        self.menu = pygame_menu.Menu(   height = self.app.WIN_SIZE[1], 
                                        theme = mytheme, 
                                        title = 'Race Driving Simulator', 
                                        width = self.app.WIN_SIZE[0], 
                                        center_content=False
                                    )
        X = 0
        Y = 85
        self.menu.add.selector('Players:', ["1", "2"], onchange=self.set_player).translate(X, Y)
        self.menu.add.selector('Maps:', [("Field", 1), ("Sunset", 2), ("Desert", 3)], onchange=self.set_map).translate(X, Y)    
        self.menu.add.button('Start', self.start).translate(X, Y)
        self.menu.add.button('Quit', pygame_menu.events.EXIT).translate(X, Y)

    def set_player(self, players):
        self.players = int(players[0])

    def set_map(self, map, _):
        self.map = map[0][0].lower()

    def start(self):
        self.play = True

    def render(self):
        self.menu.mainloop(self.app.surface, disable_loop = True)
        return self.players, self.play, self.map

