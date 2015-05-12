import pygame
from pygame.locals import *
import time
import ListOps

WIN_CLR = (250, 248, 239)
EMPTY_TILE_CLR = (204, 192, 179)
NUM_TILE_CLR = (238, 228, 218)
BRAND_CLR = (255, 108, 120)
BOARD_CLR = (187, 173, 160)
TILE_FT_CLR = (143, 122, 102)
BORDER = 20
DB_HEIGHT = 100
WIN_WIDTH = 600
WIN_HEIGHT = 700
FSIZES = [6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 21, 24, 28, 32, 36, 42, 48, 55, 63, 73, 84, 96]
FONT_CLR = (0, 0, 0)


def get_text_surf(text, height, width, font_clr):
    pygame.font.init()
    font = None
    for x in range(len(FSIZES) - 1, 0, -1):
        font = pygame.font.Font(None, FSIZES[x])
        size = font.size(text)
        if size[0] < width and size[1] < height:
            break

    text_surf = font.render(text, 1, font_clr)
    return text_surf


class TileSprite(pygame.sprite.DirtySprite):
    """ Tile that handles tile movement"""
    POPPING = 0
    MOVING = 1
    COLLAPSING = 2
    NONE = 3
    SHRUNK = 10

    def _draw_sprite_tile(self, x, y, h, w):
        self.image = pygame.Surface([h,w])
        self.image.fill(NUM_TILE_CLR)
        text_surf = get_text_surf(str(self.state_data["val"]), h, w, TILE_FT_CLR)
        self.rect = self.image.get_rect()
        self.image.blit(text_surf,self.rect)
        self.rect.x = x
        self.rect.y = y

    def __init__(self, dimens, state_data):

        pygame.sprite.DirtySprite.__init__(self)
        self.state = TileSprite.NONE
        self.state_data = state_data
        self._draw_sprite_tile(dimens[0], dimens[1], dimens[2], dimens[3])

    def set_state(self, state):
        self.state_data = state
        self.dirty = 1

    def update(self):
        if self.state == TileSprite.POPPING:
            self.pop_tile()

    def pop_tile(self, dimens, number):
        pygame.transform.scale(self.rect)


class View(object):
    """2048 ng Window"""

    def __init__(self, size=4):
        """ Initializing colors and start drawing the background"""
        self.num_per_edge = size
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.screen.fill(WIN_CLR)
        self.allsprites = pygame.sprite.LayeredDirty()
        pygame.display.set_caption('2048')
        db_width = (WIN_WIDTH - BORDER * 4)/3

# Drawing the logo
        self._draw_text_rect("2048", BORDER, BORDER,DB_HEIGHT,db_width,FONT_CLR, BRAND_CLR)
# Drawing the Score Board
        self.sc_dimens = ( db_width + 2 * BORDER, BORDER, int(DB_HEIGHT/2), db_width)
        self._draw_text_rect("SCORE", self.sc_dimens[0], self.sc_dimens[1],self.sc_dimens[2],self.sc_dimens[3], FONT_CLR, BOARD_CLR)
        self.draw_score(0)
# Drawing Max Score Board
        self.mx_dimens = ( 2 * db_width + 3 * BORDER, BORDER, int(DB_HEIGHT/2), db_width)
        self._draw_text_rect(" MAX ", self.mx_dimens[0], self.mx_dimens[1],
                             self.mx_dimens[2],self.mx_dimens[3], FONT_CLR, BOARD_CLR)
        self.draw_max_score(0)
# Drawing Board
        self.board_dimens = (BORDER, DB_HEIGHT + 2 * BORDER, WIN_WIDTH - 2 * BORDER,
                             WIN_HEIGHT - 3 * BORDER - DB_HEIGHT)
        pygame.draw.rect(self.screen, BOARD_CLR, (self.board_dimens[0],self.board_dimens[1],                          self.board_dimens[2],self.board_dimens[3]),0)

        for y in range(self.num_per_edge):
            for x in range(self.num_per_edge):
                self._draw_empty_tile(y, x)

    def _draw_text_rect(self, text, x, y, h, w, font_clr, bg_clr):
        pygame.draw.rect(self.screen, bg_clr, (x, y, w, h), 0)
        text_surf = get_text_surf(text, h, w, font_clr)
        textpos = text_surf.get_rect(centerx=x + w/2, centery=y + h/2)
        self.screen.blit(text_surf, textpos)

    def draw_score(self,score):
        self._draw_text_rect(str(score), self.sc_dimens[0] , self.sc_dimens[1]+ self.sc_dimens[2],self.sc_dimens[2],self.sc_dimens[3], FONT_CLR, BOARD_CLR)

    def draw_max_score(self,max_score):
        self._draw_text_rect(str(max_score), self.mx_dimens[0] , self.mx_dimens[1]+ self.mx_dimens[2],
                             self.mx_dimens[2],self.mx_dimens[3], FONT_CLR, BOARD_CLR)

    def set_controller(self,controller):
        self.controller = controller

    def _get_tile_size(self, x, y):
        t_width = (self.board_dimens[2] - BORDER * (self.num_per_edge + 1))/self.num_per_edge
        t_height = (self.board_dimens[3] - BORDER * (self.num_per_edge + 1))/self.num_per_edge
        t_x = (x + 2) * BORDER + x * t_width
        t_y = DB_HEIGHT + BORDER + (y + 2) * BORDER + y * t_height
        return t_x, t_y, t_width, t_height

    def _draw_empty_tile(self, coord_x, coord_y):
        tile_x, tile_y, tile_width, tile_height = self._get_tile_size(coord_x, coord_y)
        pygame.draw.rect(self.screen, EMPTY_TILE_CLR, (tile_x, tile_y , tile_width, tile_height), 0)

    def number_moved(self,moved_from_x,moved_from_y,moved_to_x,moved_to_y, number):
        self.__slide_tile(moved_from_x,moved_from_y,moved_to_x,moved_to_y, number)
        pass

    def notify(self, data):
        if data["state"] == ListOps.NEW:
            dimens = self._get_tile_size(data["to_x"],data["to_y"])
            print dimens
            tile = TileSprite(dimens,data)
            tile.set_state(data)
            self.allsprites.add(tile)

    def load_view(self):
        """ Starts the game loop """
        pygame.init()
        run = True
        while run:
                # Display some text
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    key = pygame.key.get_pressed()
                    if key[pygame.K_LEFT]:
                        self.controller.handle_key_left()
                    if key[pygame.K_RIGHT]:
                        self.controller.handle_key_right()
                    if key[pygame.K_UP]:
                        self.controller.handle_key_up()
                    if key[pygame.K_DOWN]:
                        self.controller.handle_key_down()

                if event.type == pygame.QUIT:
                    run = False
            self.allsprites.update()
            rect = self.allsprites.draw(pygame.display.get_surface())
            pygame.display.update(rect)

        self.controller.handle_quit()
        pygame.quit()
        sys.exit()

