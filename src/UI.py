import pygame as pg
import pygame_menu
from pygame_menu import Theme
import moderngl as mgl

class menu:
    def __init__(self, app):
        self.app = app
        self.players = 1
        self.play = False
        self.map = "field"
        self.set_menu(0)
        self.players_color = {1: "red", 2: "blue"}
        self.colors_avaibles = ["Red", "Blue", "Green", "Purple", "Turquoise", "White"]

    def set_menu(self, select):
        font = pygame_menu.font.FONT_MUNRO
        mytheme = Theme(background_color = (0, 0, 0, 0), 
                        widget_font = font, 
                        title_font = font,
                        widget_font_size = 50)
        myimage = pygame_menu.baseimage.BaseImage(
                    image_path=r"./textures/sb.jpg",
                    drawing_mode=pygame_menu.baseimage.IMAGE_MODE_REPEAT_XY
                )
        mytheme.background_color = myimage
        X = 0
        Y = 60
        self.menu = pygame_menu.Menu(   height = self.app.WIN_SIZE[1], 
                                            theme = mytheme, 
                                            title = 'Race Driving Simulator', 
                                            width = self.app.WIN_SIZE[0], 
                                            center_content=False,
                                            mouse_motion_selection=True
                                        )
        if select == 0:
            pg.display.set_caption("Menu")
            self.menu.add.selector('Players:', [("1", 1), ("vs AI", 2)], onchange=self.set_player).translate(X, Y)
            self.menu.add.selector('Maps:', [("Field", 1), ("Sunset", 2), ("Desert", 3)], onchange=self.set_map).translate(X, Y)    
            self.menu.add.button('Start', self.next).translate(X, Y)
            self.menu.add.button('Quit', pygame_menu.events.EXIT).translate(X, Y)
        
        elif select == 1:
            pg.display.set_caption("Menu")
            self.menu.add.selector('Select Color Car:', [(color, 1) for color in self.colors_avaibles], onchange=self.set_color).translate(X, Y)
            self.menu.add.button('Start', self.start).translate(X, Y)
            self.menu.add.button('Back', self.back).translate(X, Y)
        
        elif select == 2:
            pg.display.set_caption("Menu")
            self.menu.add.selector('Select Color Player 1:', [(color, 1) for color in self.colors_avaibles], onchange=self.set_color).translate(X, Y)
            colors = [(color, 2) for color in self.colors_avaibles]
            colors.append(colors.pop(0))
            self.menu.add.selector('Select Color AI:', colors, onchange=self.set_color).translate(X, Y)    
            self.menu.add.button('Start', self.start).translate(X, Y)
            self.menu.add.button('Back', self.back).translate(X, Y)

        elif select == 3:
            self.menu.add.label('Game Over', font_size=80).translate(X, Y)
            self.menu.add.button('See stats', self.app.open_stats_dshb).translate(X, Y)
            self.menu.add.button('Back', self.back).translate(X, Y)
            self.menu.add.button('Quit', pygame_menu.events.EXIT).translate(X, Y)

    def set_color(self, color, player):
        self.players_color[player] = color[0][0].lower()

    def set_player(self, _, players):
        self.players = players

    def set_map(self, map, _):
        self.map = map[0][0].lower()

    def next(self):
        if self.players == 1:
            self.set_menu(1)
        else:
            self.set_menu(2)

    def start(self):
        self.play = True
    
    def back(self):
        self.set_menu(0)

    def render(self):
        self.menu.mainloop(self.app.surface, disable_loop = True)
        return self.players, self.play, self.map, self.players_color
