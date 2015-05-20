import pygame
from pygame.locals import *
import os
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
    ALPHA_DELTA = 25
    MOVE_DELTA = 80
    MOVE = 0
    UPDATE = 1
    MOVE_OUT = 2
    FADE_IN = 3

    def __init__(self, w, h, work_finished):
        pygame.sprite.DirtySprite.__init__(self)
        self.w = w
        self.h = h
        self.image = pygame.Surface([w,h])
        self.image.fill(NUM_TILE_CLR)
        self.rect = self.image.get_rect()
        self.image.set_alpha(0)
        self.working = False
        self.callback = work_finished

    def set_state(self, state):
        self.state_data = state
        self.working = True


    def update(self):
        if not self.working:
            return
        new_state = self.state_data["state"]
        if new_state == self.FADE_IN:
            self.fade_in_tile()
        elif new_state == self.MOVE:
            self.move_tile()
        self.dirty = 1

    def _get_next_pos(self):
        cal_diff_x = self.state_data["pos"][0] - self.rect.x
        cal_diff_y = self.state_data["pos"][1] - self.rect.y
        delta = self.MOVE_DELTA
        if cal_diff_x != 0:
            if  abs(cal_diff_x) - delta < 0:
                delta =  abs(cal_diff_x)
            return (cal_diff_x * delta/(abs(cal_diff_x)),0)
        elif cal_diff_y != 0:
            if  abs(cal_diff_y) - delta < 0:
                delta = abs(cal_diff_y)
            return (0,cal_diff_y * delta/(abs(cal_diff_y)))

    def move_tile(self):
        newpos = self._get_next_pos()
        if newpos:
            self.rect = self.rect.move(newpos)
        else:
            self.working = False
            self.callback(self)

    def fade_in_tile(self):
        alpha = self.image.get_alpha()
        if alpha == 255:
            self.working = False
            self.callback(self)
            return
        if alpha == 0:
            text_surf = get_text_surf(self.state_data["val"], self.h, self.w,TILE_FT_CLR)
            self.image.blit(text_surf,(self.w/3,self.h/4))
            self.rect.x = self.state_data["pos"][0]
            self.rect.y = self.state_data["pos"][1]
        alpha = alpha + self.ALPHA_DELTA
        self.image.set_alpha(alpha)


class View(object):
    """2048 ng Window"""

    def __init__(self, size=4):
        """ Initializing colors and start drawing the background"""
        self.num_per_edge = size
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        background = pygame.Surface(self.screen.get_size())
        self.background = background.convert()
        self.background.fill(WIN_CLR)
        self.allsprites = pygame.sprite.LayeredDirty()
        # Maintaining a collection of current tiles
        self.coord_tiles = {}
        self.working_tiles = {}
        self.notifications = []
        self._draw_game()

    def _draw_game(self):
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
        pygame.draw.rect(self.background, BOARD_CLR, (self.board_dimens[0],self.board_dimens[1],                          self.board_dimens[2],self.board_dimens[3]),0)
# Drawing Tile Size

        self.t_width = (self.board_dimens[2] - BORDER * (self.num_per_edge + 1))/self.num_per_edge
        self.t_height = (self.board_dimens[3] - BORDER * (self.num_per_edge + 1))/self.num_per_edge

        for y in range(self.num_per_edge):
            for x in range(self.num_per_edge):
                self._draw_empty_tile(y, x)
        self.screen.blit(self.background,(0,0))
        pygame.display.flip()

    def _draw_text_rect(self, text, x, y, h, w, font_clr, bg_clr):
        pygame.draw.rect(self.background, bg_clr, (x, y, w, h), 0)
        text_surf = get_text_surf(text, h, w, font_clr)
        textpos = text_surf.get_rect(centerx=x + w/2, centery=y + h/2)
        self.background.blit(text_surf, textpos)

    def draw_score(self,score):
        self._draw_text_rect(str(score), self.sc_dimens[0] , self.sc_dimens[1]+ self.sc_dimens[2],self.sc_dimens[2],self.sc_dimens[3], FONT_CLR, BOARD_CLR)

    def draw_max_score(self,max_score):
        self._draw_text_rect(str(max_score), self.mx_dimens[0] , self.mx_dimens[1]+ self.mx_dimens[2],
        self.mx_dimens[2],self.mx_dimens[3], FONT_CLR, BOARD_CLR)
    def set_controller(self,controller):
        self.controller = controller

    def _get_tile_pos(self,x,y):
        t_x = (x + 2) * BORDER + x * self.t_width
        t_y = DB_HEIGHT + BORDER + (y + 2) * BORDER + y * self.t_height
        return t_x,t_y

    def _draw_empty_tile(self, coord_x, coord_y):
        tile_x, tile_y = self._get_tile_pos(coord_x,coord_y)
        pygame.draw.rect(self.background, EMPTY_TILE_CLR, (tile_x, tile_y , self.t_width, self.t_height), 0)

    def notify(self, data):
        self.notifications.append(data)

    def _get_tile_coord(self,axis,log_list,index,pos_name):
        return  (log_list[pos_name],index) if axis == "y" else (index,log_list[pos_name])

    def get_tile_transition(self,data):
        tile_state = {}
        if ListOps.NEW == data["state"]:
            tile_state["state"] = TileSprite.FADE_IN
        elif ListOps.MOVE == data["state"]:
            tile_state["state"] = TileSprite.MOVE
        else:
            tile_state["state"] = TileSprite.MOVE_OUT
        return tile_state

    def _sprite_finished_work(self,sprite):
        self.coord_tiles[self.working_tiles[sprite]] = sprite
        del self.working_tiles[sprite]

    def _do_prev_move(self):
        if self.notifications and not self.working_tiles:
            print "Before Notifications",self.notifications
            axis,logs = self.notifications[0]
            print "Before Axis,logs",axis,logs
            for index,log_list in logs.items():
                log = log_list.pop(0)
                tile = None
                to_pos = self._get_tile_coord(axis,log,index,"x")
                if log["state"] == ListOps.NEW:
                    print "NEW TILE"
                    tile = TileSprite(self.t_width,self.t_height,self._sprite_finished_work)
                    self.allsprites.add(tile)
                elif log["state"] == ListOps.MOVE:
                    print "MOVE TILE"
                    from_pos = self._get_tile_coord(axis,log,index,"from_x")
                    print "Retrieving from",from_pos
                    print "Moving to",to_pos
                    tile = self.coord_tiles[from_pos]
                    del self.coord_tiles[from_pos]
                self.working_tiles[tile] = to_pos
                tile_state = self.get_tile_transition(log)
                tile_state["pos"] = self._get_tile_pos(to_pos[0],to_pos[1])
                tile_state["val"] = str(log["val"])
                tile.set_state(tile_state)
                if not log_list:
                    del logs[index]

            if logs:
                self.notifications[0] = axis,logs
            else:
                self.notifications.pop(0)

        if not self.notifications and not self.working_tiles:
            return False
        return True

    def load_view(self):
        """ Starts the game loop """
        pygame.init()
        run = True
        clock = pygame.time.Clock()
        self.allsprites.clear(self.screen,self.background)
        while run:
                # Display some text
            for event in pygame.event.get():
                if event.type == KEYDOWN and not self.working_tiles:
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

            while self._do_prev_move():
                self.allsprites.update()
                rects = self.allsprites.draw(self.screen)
                pygame.display.update(rects)
                clock.tick(60)

        self.controller.handle_quit()
        pygame.quit()
        sys.exit()

