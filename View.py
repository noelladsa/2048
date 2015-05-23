import pygame
from pygame.locals import *
import random
import os
import ListOps

WIN_COL = (250, 248, 239)
TILE_BCK_CLR = (204, 192, 179)
TILE_COL = (238, 228, 218)
BRND_COL = (255, 108, 120)
BRD_COL = (187, 173, 160)
TILE_FT_COL = (143, 122, 102)
PDNG = 10
DB_H = 150
WIN_W = 600
WIN_H = 700
FSIZES = [6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 21, 24, 28, 32, 36, 42, 48, 55, 63, 73, 84, 96]
FNT_COL = (0, 0, 0)


def get_text_surf(text, h, w, font_clr):
    pygame.font.init()
    font = None
    for x in range(len(FSIZES) - 1, 0, -1):
        font = pygame.font.Font(None, FSIZES[x])
        size = font.size(text)
        if size[0] < w and size[1] < h:
            break

    text_surf = font.render(text, 1, font_clr)
    return text_surf

def draw_text_rect( text, surf, x, y, h, w, font_clr, bg_clr):
    text_back = pygame.draw.rect(surf, bg_clr, (x, y, w, h), 0)
    text_surf = get_text_surf(text, h - PDNG, w - PDNG, font_clr)
    textpos = text_surf.get_rect(centerx=x + w/2, centery=y + h/2)
    surf.blit(text_surf, textpos)
    return text_back

class DashBoardSprite(pygame.sprite.DirtySprite):

    def __init__(self, x, y, h, w):
        pygame.sprite.DirtySprite.__init__(self)
        self.image = pygame.Surface([w, h])
        self.rect = self.image.get_rect()
        self.w, self.h = w, h
        self.rect.x, self.rect.y = x, y

    def change_text(self,text):
        draw_text_rect(text, self.image, 0, 0, self.h, self.w, TILE_COL, BRD_COL)
        self.dirty = 1

    def update(self):
        self.dirty = 1


class TileSprite(pygame.sprite.DirtySprite):
    """ Each Tile on the board is represented as a sprite"""
    POP_DELTA = 30
    MOVE_DELTA = 120
    ALPHA_DELTA = 5
    MOVE = 0
    POP = 2
    KILL = 3
    ZOOM_UPDATE = 4

    def __init__(self, w, h):
        pygame.sprite.DirtySprite.__init__(self)
        self.w, self.h =  w, h
        self.image = pygame.Surface([w, h])
        self.rect = self.image.get_rect()
        self.update_jobs = []
        self.job_state = None

    def add_jobs(self, action, *args):
        self.update_jobs.append((action, args))
        self.dirty = 1

    def has_jobs(self):
        return len(self.update_jobs)

    def update(self):
        if not self.update_jobs:
            return
        self.dirty = 1
        action,args = self.update_jobs[0]
        is_complete = False
        if action == self.ZOOM_UPDATE:
            is_complete = self._zoom_update(args)
        elif action == self.POP:
            is_complete = self._pop_tile(args)
        elif action == self.MOVE:
            is_complete = self._move_tile(args)
        elif action == self.KILL:
            is_complete = self._fade_kill_tile(args)
        if is_complete:
            self.update_jobs.pop(0)

    def _gen_zoom_val(self):
        value = 0
        while value < PDNG * 1/3 :
            value = value + 1
            yield value
        while value > 0:
            value = value - 1
            yield value

    def _zoom_update(self, args):
        num, = args
        zoom_num = 0
        zoom_complete = False
        if not self.job_state:
            self.job_state = self._gen_zoom_val()
        try:
            zoom_num = next(self.job_state)
        except StopIteration:
            zoom_complete = True
            self.job_state = None
        num_text = str(num)
        self.image, self.rect = self._update_text(num_text,self.w + 2 * zoom_num,
                        self.h + 2 * zoom_num,self.x - zoom_num, self.y - zoom_num,TILE_COL )
        return zoom_complete

    def _update_text(self, text, w, h, x, y, color):
        image = pygame.Surface([w, h])
        rect = image.get_rect()
        draw_text_rect( text, image, 0, 0, h, w, TILE_FT_COL, color)
        rect.x = x
        rect.y = y
        return image, rect

    def _pop_tile(self, args):
        topleft_corner,num= args
        self.x, self.y = topleft_corner
        pop_state = False
        self.job_state = 30 if not self.job_state else  self.job_state - 5
        self.image, self.rect = self._update_text(str(num),self.w - 2 * self.job_state,
                                self.h - 2 * self.job_state,self.x + self.job_state,
                                self.y + self.job_state, TILE_COL)
        if self.job_state == 0:
            pop_state = True
            self.job_state = None
        return pop_state

    def _get_move_delta(self, distance):
        abs_dist = abs(distance)
        delta = abs_dist if abs_dist - self.MOVE_DELTA < 0 else self.MOVE_DELTA
        return distance * delta / abs_dist

    def _move_tile(self, args):
        topleft_corner, = args
        diff_x = topleft_corner[0] - self.rect.x
        diff_y = topleft_corner[1] - self.rect.y
        if not diff_x and not diff_y:
            self.x ,self.y = topleft_corner
            return True
        delta = (self._get_move_delta(diff_x) if diff_x != 0 else 0,
                 self._get_move_delta(diff_y) if diff_y != 0 else 0)
        self.rect = self.rect.move(delta)
        return False

    def _fade_kill_tile(self,args):
        alpha = self.image.get_alpha()
        pygame.sprite.Sprite.kill(self)
        return True

class View(object):
    """2048 ng Window"""

    def __init__(self, size=4):
        """ Initializing colors and start drawing the background"""
        self.edge_num = size
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        background = pygame.Surface(self.screen.get_size())
        self.background = background.convert()
        self.background.fill(WIN_COL)
        self.allsprites = pygame.sprite.LayeredDirty()
        # Maintaining a collection of current tiles
        self.coord_tiles = {}
        self.deleted_tiles = []
        self._draw_game()
        self.error_sprite = None

    def _draw_game(self):
        pygame.display.set_caption('2048')
        db_w = (WIN_W - PDNG * 4)/3

# Drawing the logo
        draw_text_rect("2048",self.background, PDNG, PDNG, DB_H, db_w, TILE_FT_COL, BRND_COL)

# Drawing the Score Board
        score_h = int(DB_H * 2/3)
        draw_text_rect("SCORE", self.background, db_w + 2 * PDNG, PDNG, int(score_h/3),
                       db_w,TILE_COL, BRD_COL)
        self.score_sprite = DashBoardSprite(db_w + 2 * PDNG, PDNG + int(score_h/3),
                            int(score_h * 2/3), db_w)
        self.allsprites.add(self.score_sprite)
# Drawing Max Score Board
        draw_text_rect("MAX", self.background, 2 * db_w + 3 * PDNG, PDNG, int(score_h/3),
                       db_w, TILE_COL, BRD_COL)
        self.mx_score_sprite = DashBoardSprite(2 * db_w + 3 * PDNG, PDNG + int(score_h/3),
                            int(score_h * 2/3), db_w)
        self.allsprites.add(self.mx_score_sprite)

        self.new_button = draw_text_rect("NEW GAME", self.background,
                          db_w + 2 * PDNG, score_h + 2 * PDNG, DB_H/3 - PDNG,
                          2 * db_w + PDNG, TILE_COL, BRD_COL)
# Drawing Board
        self.brd_d = (PDNG, DB_H + 2 * PDNG, WIN_W - 2 * PDNG,WIN_H - 3 * PDNG - DB_H)
        pygame.draw.rect(self.background, BRD_COL, (self.brd_d[0], self.brd_d[1],
                         self.brd_d[2], self.brd_d[3]), 0)
# Drawing Tile Size

        self.t_w = (self.brd_d[2] - PDNG * (self.edge_num + 1))/self.edge_num
        self.t_h = (self.brd_d[3] - PDNG * (self.edge_num + 1))/self.edge_num

# Drawing Tile Slots
        for y in range(self.edge_num):
            for x in range(self.edge_num):
                self._draw_empty_tile(y, x)

        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

    def set_controller(self, controller):
        self.controller = controller

    def _get_tile_pos(self, coord):
        x, y = coord
        t_x = (x + 2) * PDNG + x * self.t_w
        t_y = DB_H + PDNG + (y + 2) * PDNG + y * self.t_h
        return t_x, t_y

    def _draw_empty_tile(self, coord_x, coord_y):
        t_x, t_y = self._get_tile_pos((coord_x, coord_y))
        pygame.draw.rect(self.background, TILE_BCK_CLR, (t_x, t_y, self.t_w, self.t_h), 0)


    def _get_tile_coord(self, axis,axis_index, log_list, pos_name):
        if pos_name in log_list:
            return (log_list[pos_name], axis_index) if axis == "y" else \
                   (axis_index, log_list[pos_name])

    def notify(self,*args):
        score,max_score,axis, logs = args
        for axis_index, log in logs.items():
            for action in log:
                self._process_action(axis, axis_index, action)
        self.score_sprite.change_text(str(score))
        self.mx_score_sprite.change_text(str(max_score))

    def _process_action(self, axis, axis_index, action):
        to_coord = self._get_tile_coord(axis, axis_index, action, "x")
        from_coord = self._get_tile_coord(axis, axis_index, action, "from_x")
        from_tile = self.coord_tiles[from_coord] if from_coord in self.coord_tiles else None
        to_tile = self.coord_tiles[to_coord] if to_coord in self.coord_tiles else None
        val = str()
        action, from_tile, to_tile, to_coord, from_coord
        if action["state"] == ListOps.NEW:
            tile = TileSprite(self.t_w, self.t_h)
            tile.add_jobs(TileSprite.POP, self._get_tile_pos(to_coord), action["val"])
            self.allsprites.add(tile)
            self.coord_tiles[to_coord] = tile
        elif action["state"] == ListOps.MOVE:
            from_tile.add_jobs(TileSprite.MOVE, self._get_tile_pos(to_coord))
            del self.coord_tiles[from_coord]
            self.coord_tiles[to_coord] = from_tile
        elif action["state"] == ListOps.ADD:
            from_tile.add_jobs(TileSprite.MOVE, self._get_tile_pos(to_coord))
            from_tile.add_jobs(TileSprite.ZOOM_UPDATE,action["val"])
            to_tile.add_jobs(TileSprite.KILL)
            del self.coord_tiles[to_coord]
            del self.coord_tiles[from_coord]
            self.coord_tiles[to_coord] = from_tile

    def new_game(self):
        if self.error_sprite:
            print "Removing error"
            self.allsprites.remove(self.error_sprite)
            pygame.sprite.Sprite.kill(self.error_sprite)
            self.error_sprite = None

        for coord,sprite in self.coord_tiles.items():
            pygame.sprite.Sprite.kill(sprite)
            del self.coord_tiles[coord]

        self.controller.start()

    def show_message(self, message):
        self.error_sprite = DashBoardSprite(PDNG, DB_H + 2 * PDNG, WIN_H - 3 * PDNG - DB_H,
                                            WIN_W - 2 * PDNG)
        self.error_sprite.change_text(message)
        self.allsprites.add(self.error_sprite)

    def load_view(self):
        """ Starts the game loop """
        pygame.init()
        run = True
        clock = pygame.time.Clock()
        self.allsprites.clear(self.screen, self.background)
        self.controller.start()
        while run:
            for event in pygame.event.get():
                if any([self.coord_tiles[coord].has_jobs() for coord in self.coord_tiles]):
                    break;
                try:
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

                except Exception as e:
                    self.show_message(e.strmessage)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.new_button.collidepoint(pos):
                        self.new_game()
                if event.type == pygame.QUIT:
                    run = False

            self.allsprites.update()
            rects = self.allsprites.draw(self.screen)
            pygame.display.update(rects)
            clock.tick(30)

        self.controller.handle_quit()
        pygame.quit()
        sys.exit()

