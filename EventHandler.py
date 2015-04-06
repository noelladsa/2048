#!/usr/bin/python
import random
import pickle
import os.path
import pudb

class EventHandler(object):
	"""Handles all key event operations coming in from the 2048 view"""

	def __init__(self, size = 4):	
		""" Starts of a with a default board"""
		self.size = size
		self.grid = [[]]
		self.max_score = 0
		self.occupied_tiles = set()
		if os.path.isfile("2048.p"):
			self.max_score = pickle.load( open( "2048.p", "rb" ) )
		self.start_game()

	def start_game(self):
		self.grid = [[None for x in range(0,self.size)] for y in range(0,self.size)]
		self.score = 0
		self.__add_tile()

	def get_score(self): #Getters in python?
		return self.score

		
	def __add_tile(self): #Thoughts: Optimize function by recording vacant spots in a list during collapse? Rand will choose from said list
		"""Find an empty spot and add new tile"""
		if len(self.occupied_tiles) ==  (self.size * self.size): #Grid is full
			return False

		added_coord = False
		check = 0
		while not added_coord:
			coord = (random.randint(0,self.size - 1),random.randint(0,self.size - 1)) 
			if coord not in self.occupied_tiles:
				self.grid[coord[0]][coord[1]] = random.choice([2,4])
				self.occupied_tiles.add(coord) #Add the list to occupied locations
				added_coord = True

		print self.occupied_tiles
		return added_coord


	def print_board(self):
		""" Printing exising board contents """
		for x in range(0, self.size):
			for y in range(0, self.size):
				if (self.grid[x][y] is None):
					print "-",
				else:
				 print self.grid[x][y],
			print "\r"
	
	def move_left(self): 
		""" Moving numbers to the left extreme of the board """
		was_action_taken = False
		for y in range(0,self.size): #Iterating from top to bottom
			x = 0 # Starting from the left extreme of the board
			pair_x = None
			while x < self.size:
				number_x = self.__find_number_rightwards(y,x)
				if number_x is None: break
				result = self.__move_numbers_horizontally(y,x,pair_x,number_x)
				
				pair_x = result[0]
				addition_successful = result[1]
				moved = result[2]
				
				if was_action_taken is False and (addition_successful is True or moved is True):
					was_action_taken = True
				if addition_successful is False:
					x = x + 1	

		if was_action_taken is True: #If no move was made, do not add a tile.		
			self.__add_tile()


	def move_right(self): 
		""" Moving numbers to the right extreme of the board """
		was_action_taken = False
		for y in range(0,self.size): #Iterating from top to bottom
			x = self.size -1 #Starting from the right extreme of the board
			pair_x = None
			while x >= 0:
				number_x = self.__find_number_leftwards(y,x)
				if number_x is None: break
				result = self.__move_numbers_horizontally(y,x,pair_x,number_x)
				
				pair_x = result[0]
				addition_successful = result[1]
				moved = result[2]
				
				if was_action_taken is False and (addition_successful is True or moved is True):
					was_action_taken = True
				if addition_successful is False:
					x = x - 1
		
		if was_action_taken is True: #If no move was made, do not add a tile.		
			self.__add_tile()
	
	def move_up(self): 
		""" Moving numbers to the top extreme of the board """
		was_action_taken = False
		for x in range(0,self.size): #Iterating from left to right
			y = 0 #Starting from the top extreme of the board
			pair_y = None
			while y < self.size: 
				number_y = self.__find_number_downwards(y,x)
				if number_y is None: break
				result = self.__move_numbers_vertically(y,x,pair_y,number_y)
				
				pair_y = result[0]
				addition_successful = result[1]
				moved = result[2]
				
				if was_action_taken is False and (addition_successful is True or moved is True):
					was_action_taken = True
				if addition_successful is False:
					y = y + 1	

		if was_action_taken is True: #If no move was made, do not add a tile.		
			self.__add_tile()
	
	def move_down(self): 
		""" Moving numbers to the bottom extreme of the board """
		was_action_taken = False
		for x in range(0,self.size): #Iterating from left to right
			y = self.size -1 #Starting from the bottom extreme of the board
			pair_y = None
			while y >= 0: 
				number_y = self.__find_number_upwards(y,x)
				if number_y is None: break
				result = self.__move_numbers_vertically(y,x,pair_y,number_y)
				pair_y = result[0]
				addition_successful = result[1]
				moved = result[2]
				
				if was_action_taken is False and (addition_successful is True or moved is True):
					was_action_taken = True
				if addition_successful is False:
					y = y - 1	

		if was_action_taken is True: #If no move was made, do not add a tile.		
			self.__add_tile()

	def __move_numbers_horizontally(self,y,x,pair_x,next_number_x): #Maybe merge this number
		""" Moves numbers and collapses any if needed. Returns a position at which future numbers collapse"""
		addition_successful = False
		if pair_x is not None:
			addition_successful = self.__pair_addition(y,pair_x,y,next_number_x)
			pair_x = None

		moved = False
		if not addition_successful:
			moved = self.__move_number(y,x,y,next_number_x)
			pair_x = x

		return (pair_x,	addition_successful,moved)

	def __move_numbers_vertically(self,y,x,pair_y,next_number_y): #Maybe merge this number
		""" Moves numbers and collapses any if needed. Returns a position at which future numbers collapse"""
		addition_successful = False
		if pair_y is not None:
			addition_successful = self.__pair_addition(pair_y,x,next_number_y,x)
			pair_y = None

		moved = False
		if not addition_successful:
			moved = self.__move_number(y,x,next_number_y,x)
			pair_y = y

		return (pair_y,	addition_successful,moved)		

	def __pair_addition(self,addto_y,addto_x, addfrom_y,addfrom_x):
		"""Check if two elements are equal and add to one if so"""	
		collapsed = False
		if self.grid[addto_y][addto_x] == self.grid[addfrom_y][addfrom_x]:
			self.grid[addto_y][addto_x] = 2 * self.grid[addfrom_y][addfrom_x]	
			self.score = self.score + self.grid[addto_y][addto_x] 
			self.grid[addfrom_y][addfrom_x] = None
			self.occupied_tiles.remove((addfrom_y,addfrom_x)) #Mark as unoccupied
			collapsed = True
		return collapsed

	def __move_number(self,moveto_y,moveto_x, movefrom_y,movefrom_x):
		""" Moving numbers from one position to another, resetting last position to None"""
		number_moved = False
		if moveto_x != movefrom_x or moveto_y != movefrom_y: #Check that number is not in the same place
			self.grid[moveto_y][moveto_x] = self.grid[movefrom_y][movefrom_x]
			if (moveto_y,moveto_x) not in self.occupied_tiles:
				self.occupied_tiles.add((moveto_y,moveto_x))
			self.grid[movefrom_y][movefrom_x] = None
			self.occupied_tiles.remove((movefrom_y,movefrom_x)) #Mark as unoccupied
			number_moved = True #A number were moved 
		return number_moved 

	def __find_number_rightwards(self,  y, x):
		""" Find the next number to the right  """
		while x < self.size: # Stops when you've found a number
			if self.grid[y][x] is not None: break
			x = x + 1
		result = x if x < self.size	else None
		return result

	def __find_number_leftwards(self,  y, x):
		while x >= 0: # Stops when you've found a number
			if self.grid[y][x] is not None: break
			x = x - 1
		result = x if x >= 0 else None
		return result

	def __find_number_upwards(self,  y, x):
		""" Find the next number in the upward direction  """
		while y >= 0: # Stops when you've found a number
			if self.grid[y][x] is not None: break
			y = y - 1
		result = y if y >= 0 else None
		return result

	def __find_number_downwards(self,  y, x):
		""" Find the next number in the downward direction  """
		while y < self.size: # Stops when you've found a number
			if self.grid[y][x] is not None: break
			y = y + 1
		result = y if y < self.size else None
		return result	
	

	def is_game_over(self):
		""" Checking if number pairs are available in a full grid/ If further moves are possible"""
		if len(self.occupied_tiles) <  (self.size * self.size): #Grid is full
			return False

		for y in range(0,self.size):
			prev_x = None
			x = 0
			while x < self.size:
				if prev_x != None:
					if self.grid[y][prev_x] == self.grid[y][x]:
						return False
				prev_x = x
				x = x + 1

		for x in range(0,self.size):
			prev_y = None
			y = 0
			while y < self.size:
				if prev_y != None:
					if self.grid[prev_y][x] == self.grid[y][x]:
						return False
				prev_y = y
				y = y + 1

		if self.score > self.max_score:
			self.max_score = self.score

		return True