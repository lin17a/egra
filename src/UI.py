import pygame as pg
import pygame_menu


class menu:
    def __init__(self, app):
        self.app = app
        self.players = None
        self.menu = pygame_menu.Menu(   height = 300, 
                                        theme = pygame_menu.themes.THEME_BLUE, 
                                        title = 'Menu', 
                                        width = 400
                                    )
        self.menu.add.button('Play One Player', self.set_player, 1)
        self.menu.add.button('Play Two Player', self.set_player, 2)
        self.menu.add.button('Quit', pygame_menu.events.EXIT)

    def set_player(self, players):
        self.players = players

    def render(self):
        self.menu.mainloop(self.app.surface, disable_loop = True)
        return self.players

