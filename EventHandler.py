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
		if os.path.isfile("2048.p"):
			self.max_score = pickle.load( open( "2048.p", "rb" ) )
		self.start_game()

	def start_game(self):
		self.grid = [[None for x in range(0,self.size)] for y in range(0,self.size)]
		self.score = 0
		self.__add_tile()

	def get_score(self): #Getters in python?
		return self.score

	def __generate_coord(self):
		coord = {}
		coord["x"] = random.randint(0,self.size - 1) #Assuming X start from the top left and increases as you go right
		coord["y"] = random.randint(0,self.size - 1) #Assuming Y start from the top left and increases as you go to the bottom
		return coord
		
	def __add_tile(self): #Thoughts: Optimize function by recording vacant spots in a list during collapse? Rand will choose from said list
		"""Find an empty spot and add new tile"""
		added_coord = False
		check = 0
		while not added_coord and check < (self.size * self.size):
			coord = self.__generate_coord()
			if self.grid[coord["y"]][coord["x"]] is None: #Checking if tile is empty and adding a choice of 2 or 4
				self.grid[coord["y"]][coord["x"]] = random.choice([2,4])
				added_coord = True
			check = check + 1

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
		for y in range(0,self.size): #Iterating from top to bottom
			x = 0 # Starting from the left extreme of the board
			pair_x = None
			while x < self.size:
				number_x = self.__find_number_rightwards(y,x)
				if number_x is None: break
				pair_x = self.__move_numbers_horizontally(y,x,pair_x,number_x)
				x = x + 1	

		return  self.__next_move()


	def move_right(self): 
		""" Moving numbers to the right extreme of the board """
		for y in range(0,self.size): #Iterating from top to bottom
			x = self.size -1 #Starting from the right extreme of the board
			pair_x = None
			while x >= 0:
				number_x = self.__find_number_leftwards(y,x)
				if number_x is None: break
				pair_x = self.__move_numbers_horizontally(y,x,pair_x,number_x)
				x = x - 1
		
		return  self.__next_move()
	
	def move_up(self): 
		""" Moving numbers to the top extreme of the board """
		for x in range(0,self.size): #Iterating from left to right
			y = 0 #Starting from the top extreme of the board
			pair_y = None
			while y < self.size: 
				number_y = self.__find_number_downwards(y,x)
				if number_y is None: break
				pair_y = self.__move_numbers_vertically(y,x,pair_y,number_y)
				y = y + 1	

		return  self.__next_move()
	
	def move_down(self): 
		""" Moving numbers to the bottom extreme of the board """
		for x in range(0,self.size): #Iterating from left to right
			y = self.size -1 #Starting from the bottom extreme of the board
			pair_y = None
			while y >= 0: 
				number_y = self.__find_number_upwards(y,x)
				if number_y is None: break
				pair_y = self.__move_numbers_vertically(y,x,pair_y,number_y)
				y = y - 1	
		
		return  self.__next_move()
	

	def __move_numbers_horizontally(self,y,x,pair_x,next_number_x): #Maybe merge this number
		""" Moves numbers and collapses any if needed. Returns a position at which future numbers collapse"""
		add_successful = False
		if pair_x is not None:
			add_successful = self.__pair_addition(y,pair_x,y,next_number_x)
			pair_x = None

		if not add_successful:
			self.__move_number(y,x,y,next_number_x)
			pair_x = x

		return pair_x	

	def __move_numbers_vertically(self,y,x,pair_y,next_number_y): #Maybe merge this number
		""" Moves numbers and collapses any if needed. Returns a position at which future numbers collapse"""
		add_successful = False
		if pair_y is not None:
			add_successful = self.__pair_addition(pair_y,x,next_number_y,x)
			pair_y = None

		if not add_successful:
			self.__move_number(y,x,next_number_y,x)
			pair_y = y

		return pair_y		

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

	def __pair_addition(self,addto_y,addto_x, addfrom_y,addfrom_x):
		"""Check if two elements are equal and add to one if so"""	
		collapsed = False
		if self.grid[addto_y][addto_x] == self.grid[addfrom_y][addfrom_x]:
			self.grid[addto_y][addto_x] = 2 * self.grid[addfrom_y][addfrom_x]	
			self.score = self.score + self.grid[addto_y][addto_x] 
			self.grid[addfrom_y][addfrom_x] = None
			collapsed = True
		return collapsed

	def __move_number(self,moveto_y,moveto_x, movefrom_y,movefrom_x):
		""" Moving numbers from one position to another, resetting last position to None"""
		if moveto_x != movefrom_x or moveto_y != movefrom_y: #Check that number is not in the same place
			self.grid[moveto_y][moveto_x] = self.grid[movefrom_y][movefrom_x]
			self.grid[movefrom_y][movefrom_x] = None
	
	def __next_move(self):
		game_over = False
		if self.__add_tile() is False:
			print "Could not add more Tiles"
			return self.__any_pairs_left()
		return game_over	

	def __any_pairs_left(self):
		#pudb.set_trace()
		""" Checking if pairs are available in a full grid"""
		prev_x = None
		x = 0
		for y in range(0,self.size):
			while x < self.size:
				if prev_x != None:
					if self.grid[y][prev_x] == self.grid[y][x]:
						print "Some items are equal",y,x,y,prev_x
						return False
				prev_x = x
				x = x + 1

		prev_y = None
		y = 0
		for x in range(0,self.size):
			while y < self.size:
				if prev_y != None:
					if self.grid[prev_y][x] == self.grid[y][x]:
						print "Some items are equal",y,x,prev_y,x
						return False
				prev_y = y
				y = y + 1

		if self.score > self.max_score:
			self.max_score = self.score
			#Need to save score

		return True