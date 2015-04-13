#!/usr/bin/env python

import pygame, time
from pygame.locals import *
import pudb

class View(object):
    """2048 Viewing Window"""
    def __init__(self,controller,size = 4):
        """ Initializing colors and start drawing the background"""

        self.WINDOW_COLOR = (250, 248, 239)
        self.EMPTY_TILE_COLOR = (204,192,179)
        self.FILLED_TILE_COLOR = (238,228,218)
        self.BRAND_COLOR = (255, 108, 120)
        self.BOARD_COLOR = (187,173, 160)
        self.TILE_FONT_COLOR = (143,122,102)

        self.BORDER_WIDTH = 20
        self.DASH_BOARD_HEIGHT = 100
        self.WINDOW_WIDTH = 600
        self.WINDOW_HEIGHT = 700
        self.font_sizes = [6,7,8,9,10,11,12,14,16,18,21,24,28,32,36,42,48,55,63,73,84,96]


        self.grow_by = 6
        self.numbers_per_edge = size
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.screen.fill(self.WINDOW_COLOR)
        self.controller = controller
        self.fpsTime = pygame.time.Clock()
        self.FPS = 30 #Any lower than this doesn't make a difference

        pygame.display.set_caption('2048')
        rect_width = (self.WINDOW_WIDTH - self.BORDER_WIDTH * 4)/3
        
        #Dimensions are stored with starting x and y coordinates and board dimensions
        self.logo_board_dimensions = (0,0,rect_width,self.DASH_BOARD_HEIGHT) 
        self.score_board_dimensions = (rect_width + 1 * self.BORDER_WIDTH,0,rect_width,self.DASH_BOARD_HEIGHT)
        self.maxscore_board_dimensions = (2 * rect_width + 2 * self.BORDER_WIDTH,0,rect_width,self.DASH_BOARD_HEIGHT)
        self.main_board_dimensions = (0,self.DASH_BOARD_HEIGHT + self.BORDER_WIDTH,self.WINDOW_WIDTH - 2 * self.BORDER_WIDTH, self.WINDOW_HEIGHT - 3 * self.BORDER_WIDTH - self.DASH_BOARD_HEIGHT)
       
        self.__draw_logo()
        self.__draw_scoreboard()
        self.__draw_maxscoreboard()
        self.__draw_mainboard()

    def __get_fitting_font(self,text,height,width):
        default_size = 10
        for x in range(len(self.font_sizes) - 1,0,-1):
            font = pygame.font.Font(None,self.font_sizes[x])
            font_size = font.size(text)
            if font_size[0] < width  and font_size[1] < height:
                return font

        return default_size #Should never have to come here really

    def __draw_board_with_string(self,text,startx,starty,height,width,font_color,bg_color):
        pygame.draw.rect(self.screen, bg_color, (startx + self.BORDER_WIDTH,starty + self.BORDER_WIDTH,width,height),0)
        pygame.font.init()
        font = self.__get_fitting_font(text,height - (self.BORDER_WIDTH),width - (self.BORDER_WIDTH))
        rendered_text = font.render(text, 1, font_color)
        textpos = rendered_text.get_rect(centerx = startx + self.BORDER_WIDTH + width/2, centery = starty + self.BORDER_WIDTH + height/2)
        self.screen.blit(rendered_text, textpos)

    def __draw_logo(self):     
        #Background Rect for the 2048 branding
        startx = self.logo_board_dimensions[0]
        starty =  self.logo_board_dimensions[1]
        rect_width =  self.logo_board_dimensions[2]
        height =  self.logo_board_dimensions[3]
        font_color = (255,255,255)

        self.__draw_board_with_string("2048",startx,starty,height,rect_width,font_color,self.BRAND_COLOR)
        
    def __draw_scoreboard(self,score = 0):
        #Background Rect for the 2048 branding
        startx = self.score_board_dimensions[0]
        starty =  self.score_board_dimensions[1]
        rect_width =  self.score_board_dimensions[2]
        height =  self.score_board_dimensions[3]
        text = str(score)
        font_color = (255,255,255)
        bg_color = self.BOARD_COLOR

        self.__draw_board_with_string("SCORE", startx, starty, int(height/2.0), rect_width, font_color,bg_color)
        self.__draw_board_with_string(text, startx, starty +  int(height/2.0), int(height/2.0), rect_width, font_color,bg_color)

    def __draw_maxscoreboard(self,max_score = 0):
        startx = self.maxscore_board_dimensions[0]
        starty =  self.maxscore_board_dimensions[1]
        rect_width =  self.maxscore_board_dimensions[2]
        height =  self.maxscore_board_dimensions[3]
        text = str(max_score)
        font_color = (255,255,255)
        bg_color = self.BOARD_COLOR
        
        self.__draw_board_with_string("MAX SCORE", startx, starty, int(height/2.0), rect_width, font_color,bg_color)
        self.__draw_board_with_string(text, startx, starty +  int(height/2.0), int(height/2.0), rect_width, font_color,bg_color)

    def __draw_mainboard(self):
        startx = self.main_board_dimensions[0]
        starty =  self.main_board_dimensions[1]
        width =  self.main_board_dimensions[2]
        height =  self.main_board_dimensions[3]
        font_color = (0,0,0)
        bg_color = self.BOARD_COLOR

        pygame.draw.rect(self.screen, bg_color, (startx + self.BORDER_WIDTH,starty + self.BORDER_WIDTH,width,height),0)      
        self.__draw_emptytiles()

    def __draw_emptytiles(self):
        startx = self.main_board_dimensions[0]
        starty =  self.main_board_dimensions[1]
        width =  self.main_board_dimensions[2]
        height =  self.main_board_dimensions[3]

        for y in range(0,self.numbers_per_edge):
            for x in range(0,self.numbers_per_edge):
                self.__draw_empty_tile(y,x)



    def __calculate_tile_dimensions(self,coord_x,coord_y):

        tile_width = (self.main_board_dimensions[2] - self.BORDER_WIDTH * (self.numbers_per_edge + 1))/self.numbers_per_edge
        tile_height = (self.main_board_dimensions[3] - self.BORDER_WIDTH * (self.numbers_per_edge + 1))/self.numbers_per_edge

        tile_x = (coord_x + 1) * self.BORDER_WIDTH + coord_x * tile_width
        tile_y = self.DASH_BOARD_HEIGHT + self.BORDER_WIDTH+ (coord_y + 1) * self.BORDER_WIDTH + coord_y * tile_height

        return (tile_x,tile_y,tile_width,tile_height)


    # def __check_tile_bounds(self,topleft_x,topleft_y):
    #     within_bounds = False
    #     if topleft_x > self.BORDER_WIDTH and topleft_x < self.boar





    def __draw_empty_tile(self,coord_x,coord_y):
        result = self.__calculate_tile_dimensions(coord_x,coord_y)

        tile_x = result[0]
        tile_y = result[1]

        tile_width = result[2]
        tile_height = result[3]

        pygame.draw.rect(self.screen, self.EMPTY_TILE_COLOR, 
                (tile_x + self.BORDER_WIDTH,tile_y + self.BORDER_WIDTH,tile_width,tile_height),0)

    def __pop_tile(self,coord_x,coord_y,number):

        result = self.__calculate_tile_dimensions(coord_x,coord_y)

        final_tile_x = result[0]
        final_tile_y = result[1]
        final_tile_width = result[2]
        final_tile_height = result[3]

        zoom_from = final_tile_width/3 # Arbitrary value
       
        

        x = result[0] + zoom_from
        y = result[1] + zoom_from
        width = result[2] - 2 * zoom_from
        height = result[3] - 2 * zoom_from
        
        while x > final_tile_x and y > final_tile_y and width < final_tile_width and height < final_tile_height:
            self.__draw_board_with_string(str(number),x,y, height, width, self.TILE_FONT_COLOR,self.FILLED_TILE_COLOR)
            pygame.display.update()
            self.fpsTime.tick(self.FPS)
            x = x - self.grow_by
            y = y - self.grow_by
            width = width + self.grow_by * 2
            height = height + self.grow_by * 2

    def __slide_tile(self,moved_from_x,moved_from_y,moved_to_x,moved_to_y, number):

        result = self.__calculate_tile_dimensions(moved_from_x,moved_from_y)

        final_tile_x = result[0]
        final_tile_y = result[1]
        
        tile_width = result[2]
        tile_height = result[3]

        result = self.__calculate_tile_dimensions(moved_to_x,moved_to_y)

        x = result[0]
        y = result[1]

        delta_move_x = 0        
        delta_move_y = 0

        if x < final_tile_x: 
            delta_move_x = +1 * self.grow_by 
        elif x > final_tile_x:
            delta_move_x = -1 * self.grow_by 

        if y < final_tile_y: 
            delta_move_y = +1 * self.grow_by 
        elif y > final_tile_y:
            delta_move_y = -1 * self.grow_by 

        while x != final_tile_x or y != final_tile_y:
            self.__draw_mainboard()
            self.__draw_board_with_string(str(number),x,y, tile_height, tile_width, self.TILE_FONT_COLOR,self.FILLED_TILE_COLOR)
            pygame.display.update()
            self.fpsTime.tick(self.FPS)
            x = x + delta_move_x
            y = y + delta_move_y                




    def update_scoreboard(self):
        pass    

    def update_max_scoreboard(self):
        pass    


    def added_tiles(self,x1,y1,number1,x2,y2,number2):
        #Animate to move under
        pass

    def number_added(self,x1,y1,number1):
        self.__pop_tile(x1,y1,str(number1))

    def number_moved(self,moved_from_x,moved_from_y,moved_to_x,moved_to_y, number):
        self.__slide_tile(moved_from_x,moved_from_y,moved_to_x,moved_to_y, number)
        pass


    def load_view(self):
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
                    self.controller.handle_quit()
                    pygame.quit()
                    sys.exit()

            pygame.display.update()
