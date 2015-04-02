#!/usr/bin/python
import random
import pdb


class EventHandler(object):
	
	"""Handles all key event operations coming in from the 2048 view"""
	def __init__(self, size = 4):	
		""" Starts of a with a default board"""
		self.size = size
		self.grid = [[]]
		self.start_game()

	def start_game(self):
		self.grid = [[None for x in range(0,self.size)] for y in range(0,self.size)]


	def __generate_coord(self):
		coord = {}
		coord["x"] = random.randint(0,self.size - 1) #Assuming X start from the top left and increases as you go right
		coord["y"] = random.randint(0,self.size - 1) #Assuming Y start from the top left and increases as you go to the bottom
		return coord

	def add_tile(self): #Thoughts: Optimize function by recording vacant spots in a list during collapse? Rand will choose from said list
		"""Find an empty spot and add new tile"""
		added_coord = False

		while not added_coord:
			coord = self.__generate_coord()
			if self.grid[coord["y"]][coord["x"]] is None: #Adding the 
				self.grid[coord["y"]][coord["x"]] = random.choice([2,4])
				added_coord = True

	def print_board(self):
		""" Printing exising board contents """
		for x in range(0, self.size):
			for y in range(0, self.size):
				if (self.grid[x][y] is None):
					print "-",
				else:
				 print self.grid[x][y],
			print "\r"


	def find_number_rightwards(self,  y, x):
		#pdb.set_trace()
		while x < self.size: # Stops when you've found a number
			if self.grid[y][x] is not None: break
			x = x + 1
		result = x if x < self.size	else None
		return result

	def __sweep_left(self,y):	
		x = 0
		while x < self.size: 
			non_vacant_x = self.find_number_rightwards(y, x) # Looking for the first of a pair
			if non_vacant_x is None: break # No number was found, nothing is to be done
			if non_vacant_x > x:  
				self.grid[y][x] = self.grid[y][non_vacant_x]
				self.grid[y][non_vacant_x] = None
			x = x + 1


	def __collapse_horizontal(self,y,x,pair):		
		""" Collapses same numbers and if not the same restarts the pairing"""
		if pair is None:
				return x
		else:
			if self.grid[y][pair] == self.grid[y][x]:
				self.grid[y][pair] = 2 * self.grid[y][pair]	
				pair = None
				self.grid[y][x] = None
			else:
				pair = x
		return pair

	def __collapse_pairs_left(self,y):
		pair = None 
		x = 0
		while x < self.size and self.grid[y][x] != None: 
			pair = self.__collapse_horizontal(y,x,pair)
			x = x + 1


	def move_left(self): # Thoughts : Should I merge all the move functions and pass the indexes..
		""" Moving coords to the left extreme of the board """
		for y in range(0,self.size): #Iterating from top to bottom
			self.__sweep_left(y)
			self.__collapse_pairs_left(y)
			self.__sweep_left(y)
			

	def find_number_leftwards(self,  y, x):
		while x >= 0: # Stops when you've found a number
			if self.grid[y][x] is not None: break
			x = x - 1
		result = x if x >= 0 else None
		return result

	def __collapse_pairs_right(self,y):
		pair = None 
		x = self.size - 1
		while x >= 0 and self.grid[y][x] != None: 
			pair = self.__collapse_horizontal(y,x,pair)
			x = x - 1


	def __sweep_right(self,y):	
		x = self.size -1
		while x >= 0: 
			non_vacant_x = self.find_number_leftwards(y, x) # Looking for the first of a pair
			if non_vacant_x is None: break # No number was found, nothing is to be done
			if non_vacant_x < x:  
				self.grid[y][x] = self.grid[y][non_vacant_x]
				self.grid[y][non_vacant_x] = None
			x = x - 1

	

	def move_right(self): # Thoughts : Should I merge all the move functions and pass the indexes..
		""" Moving coords to the right extreme of the board """
		for y in range(0,self.size): #Iterating from top to bottom
			self.__sweep_right(y)
			self.__collapse_pairs_right(y)
			self.__sweep_right(y)
