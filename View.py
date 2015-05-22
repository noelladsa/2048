import pygame
from pygame.locals import *
import os
import ListOps

WIN_COL = (250, 248, 239)
TILE_BCK_CLR = (204, 192, 179)
NUM_TILE_COL = (238, 228, 218)
BRND_COL = (255, 108, 120)
BRD_COL = (187, 173, 160)
TILE_FT_COL = (143, 122, 102)
PDNG = 20
DB_H = 100
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


class TileSprite(pygame.sprite.DirtySprite):
    """ Each Tile on the board is represented as a sprite"""
    ALPHA_DELTA = 25
    MOVE_DELTA = 80
    MOVE = 0
    UPDATE = 1
    POP = 2
    MOVE_OUT = 3

    def __init__(self, w, h):
        pygame.sprite.DirtySprite.__init__(self)
        self.w = w
        self.h = h
        self.image = pygame.Surface([w, h])
        self.image.fill(NUM_TILE_COL)
        self.rect = self.image.get_rect()
        self.image.set_alpha(0)
        self.update_jobs = []

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
        if action == TileSprite.UPDATE:
            is_complete = self._update_text(args)
        elif action == TileSprite.POP:
            is_complete = self._pop_tile(args)
        elif action == self.MOVE:
            is_complete = self._move_tile(args)
        if is_complete:
            self.update_jobs.pop(0)

    def _update_text(self, args):
        text, = args
        self.image.fill(NUM_TILE_COL)
        text_surf = get_text_surf(text, self.h, self.w, TILE_FT_COL)
        self.image.blit(text_surf, (self.w/3, self.h/4))
        return True

    def _get_move_delta(self, distance):
        abs_dist = abs(distance)
        delta = abs_dist if abs_dist - self.MOVE_DELTA < 0 else self.MOVE_DELTA
        return distance * delta / abs_dist

    def _move_tile(self, args):
        topleft_corner, = args
        diff_x = topleft_corner[0] - self.rect.x
        diff_y = topleft_corner[1] - self.rect.y
        if not diff_x and not diff_y:
            return True
        delta = (self._get_move_delta(diff_x) if diff_x != 0 else 0,
                 self._get_move_delta(diff_y) if diff_y != 0 else 0)
        self.rect = self.rect.move(delta)
        return False

    def _pop_tile(self, args):
        topleft_corner, = args
        alpha = self.image.get_alpha()
        if alpha == 255:
            return True
        self.rect.x, self.rect.y = topleft_corner
        alpha = alpha + self.ALPHA_DELTA
        self.image.set_alpha(alpha)
        return False

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
        self.working_tiles = []
        self._draw_game()

    def _draw_game(self):
        pygame.display.set_caption('2048')
        db_w = (WIN_W - PDNG * 4)/3

# Drawing the logo
        self._draw_text_rect("2048", PDNG, PDNG, DB_H, db_w, FNT_COL, BRND_COL)

# Drawing the Score Board
        self.sc_d = (db_w + 2 * PDNG, PDNG, int(DB_H/2), db_w)
        self._draw_text_rect("SCORE", self.sc_d[0], self.sc_d[1], self.sc_d[2],
                             self.sc_d[3], FNT_COL, BRD_COL)
        self.draw_score(0)

# Drawing Max Score Board
        self.mx_d = (2 * db_w + 3 * PDNG, PDNG, int(DB_H/2), db_w)
        self._draw_text_rect(" MAX ", self.mx_d[0], self.mx_d[1], self.mx_d[2],
                             self.mx_d[3], FNT_COL, BRD_COL)
        self.draw_max_score(0)

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

    def _draw_text_rect(self, text, x, y, h, w, font_clr, bg_clr):
        pygame.draw.rect(self.background, bg_clr, (x, y, w, h), 0)
        text_surf = get_text_surf(text, h, w, font_clr)
        textpos = text_surf.get_rect(centerx=x + w/2, centery=y + h/2)
        self.background.blit(text_surf, textpos)

    def draw_score(self, score):
        self._draw_text_rect(str(score), self.sc_d[0], self.sc_d[1] + self.sc_d[2],
                             self.sc_d[2], self.sc_d[3], FNT_COL, BRD_COL)

    def draw_max_score(self, max_score):
        self._draw_text_rect(str(max_score), self.mx_d[0], self.mx_d[1] + self.mx_d[2],
                             self.mx_d[2], self.mx_d[3], FNT_COL, BRD_COL)

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

    def notify(self, data):
        axis, logs = data
        print "Before Axis,logs", axis, logs
        for axis_index, log in logs.items():
            for action in log:
                self._process_action(axis, axis_index, action)

    def _process_action(self, axis, axis_index, action):
        to_coord = self._get_tile_coord(axis, axis_index, action, "x")
        from_coord = self._get_tile_coord(axis, axis_index, action, "from_x")
        from_tile = self.coord_tiles[from_coord] if from_coord in self.coord_tiles else None
        to_tile = self.coord_tiles[to_coord] if to_coord in self.coord_tiles else None
        val = str(action["val"])
        print "Log,from_tile,to_tile,to_coord,from_coord",
        action, from_tile, to_tile, to_coord, from_coord
        if action["state"] == ListOps.NEW:
            tile = TileSprite(self.t_w, self.t_h)
            tile.add_jobs(TileSprite.UPDATE, val)
            tile.add_jobs(TileSprite.POP, self._get_tile_pos(to_coord))
            self.allsprites.add(tile)
            self.coord_tiles[to_coord] = tile
        elif action["state"] == ListOps.MOVE:
            from_tile.add_jobs(TileSprite.MOVE, self._get_tile_pos(to_coord))
            del self.coord_tiles[from_coord]
            self.coord_tiles[to_coord] = from_tile
        elif action["state"] == ListOps.ADD:
            from_tile.add_jobs(TileSprite.MOVE, self._get_tile_pos(to_coord))
            to_tile.add_jobs(TileSprite.UPDATE,val)

    def load_view(self):
        """ Starts the game loop """
        pygame.init()
        run = True
        clock = pygame.time.Clock()
        self.allsprites.clear(self.screen, self.background)
        while run:
                # Display some text
            for event in pygame.event.get():
                if any([self.coord_tiles[coord].has_jobs() for coord in self.coord_tiles]):
                    break;

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
            rects = self.allsprites.draw(self.screen)
            pygame.display.update(rects)
            clock.tick(60)

        self.controller.handle_quit()
        pygame.quit()
        sys.exit()

