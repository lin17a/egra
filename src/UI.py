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


class InGameText:
    def __init__(self, app):
        self.app = app
        self.window_size = app.WIN_SIZE
        self.display_surface = pg.display.set_mode(self.window_size, pg.DOUBLEBUF | pg.OPENGL)
        # create a font object.
        # 1st parameter is the font file
        # which is present in pygame.
        # 2nd parameter is size of the font
        self.font = pg.font.Font('freesansbold.ttf', 32)
        # create a text surface object,
        # on which text is drawn on it.
        self.text = self.font.render('GeeksForGeeks', True, (0,0,0), (1,1,1))
        textRect = self.text.get_rect()
        # set the center of the rectangular object.
        textRect.center = (self.window_size[0] // 2, self.window_size[1] // 2)

    def display_checkpoints(self):
        self.text = self.font.render('GeeksForGeeks', True, (0,0,0), (1,1,1))
        # create a rectangular object for the
        # text surface object
        textRect = self.text.get_rect()
        # set the center of the rectangular object.
        textRect.center = (self.window_size[0] // 2, self.window_size[1] // 2)
        self.display_surface.blit(self.text, textRect)
        pg.display.update()

    def drawText(self, text):
        textSurface = self.font.render(text, True, (255, 255, 66, 255), (0, 66, 0, 255))
        textData = pg.image.tostring(textSurface, "RGBA", True)
        mgl.glWindowPos2d(self.window_size[0] // (4/3), self.window_size[1] // 2)
        mgl.glDrawPixels(textSurface.get_width(), textSurface.get_height(), mgl.GL_RGBA, mgl.GL_UNSIGNED_BYTE, textData)

    def draw_text(self):
        self.ctx = self.app.ctx
        self.pg_res = self.app.WIN_SIZE
        self.pg_screen = pg.Surface(self.pg_res, flags=pg.SRCALPHA)
        # 24 bit (rgba) moderngl texture
        self.pg_texture = self.ctx.texture(self.pg_res, 4)
        self.pg_texture.filter = mgl.NEAREST, mgl.NEAREST

        self.text = self.font.render('GeeksForGeeks', True, (0, 0, 0), (1, 1, 1))
        # create a rectangular object for the
        # text surface object
        textRect = self.text.get_rect()
        # set the center of the rectangular object.
        textRect.center = (self.window_size[0] // 2, self.window_size[1] // 2)
        self.pg_screen.fill((0, 0, 0, 0))

        self.pg_screen.blit(self.text, textRect)
        texture_data = self.pg_screen.get_view('1')
        self.pg_texture.write(texture_data)

        #self.ctx.enable(mgl.BLEND)
        self.pg_texture.use()
        #self.ctx.disable(mgl.BLEND)


