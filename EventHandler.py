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

	def is_game_over(self,added_tile):
		if added_tile is False and self.__is_collapse_possible() is False:
			return True
		return False

	def __is_collapse_possible(self):
		prev_x = None
		x = 0
		for y in range(0,self.size):
			while x < self.size:
				if prev_x != None:
					if self.grid[y][prev_x] == self.grid[y][x]:
						print "Some items are equal",y,x,y,prev_x
						return True
				prev_x = x
				x = x + 1

		prev_y = None
		y = 0
		for x in range(0,self.size):
			while y < self.size:
				if prev_y != None:
					if self.grid[prev_y][x] == self.grid[prev_y][x]:
						print "Some items are equal",y,x,prev_y,x
						return True
				prev_y = y
				y = y + 1

		return False
		

	def __add_tile(self): #Thoughts: Optimize function by recording vacant spots in a list during collapse? Rand will choose from said list
		"""Find an empty spot and add new tile"""
		added_coord = False
		check = 0
		while not added_coord and check < (self.size * self.size):
			coord = self.__generate_coord()
			if self.grid[coord["y"]][coord["x"]] is None: #Adding the 
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


	def find_number_rightwards(self,  y, x):
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
				self.score = self.score + self.grid[y][pair] 
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
		added  = self.__add_tile()
		return  self.is_game_over(added)
	

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
		added  = self.__add_tile()
		return  self.is_game_over(added)


	def __collapse_vertical(self,y,x,pair):		
		""" Collapses same numbers and if not the same restarts the pairing"""
		if pair is None:
				return y
		else:
			if self.grid[pair][x] == self.grid[y][x]:
				self.grid[pair][x] = 2 * self.grid[pair][x]	
				self.score = self.score + self.grid[pair][x] 
				pair = None
				self.grid[y][x] = None
			else:
				pair = y
		return pair
		

	def find_number_upwards(self,  y, x):
		while y >= 0: # Stops when you've found a number
			if self.grid[y][x] is not None: break
			y = y - 1
		result = y if y >= 0 else None
		return result

	def __collapse_pairs_bottom(self,x):
		pair = None 
		y = self.size - 1
		while y >= 0 and self.grid[y][x] != None: 
			pair = self.__collapse_vertical(y,x,pair)
			y = y - 1

	def __sweep_down(self,x):	
		y = self.size -1
		while y >= 0: 
			non_vacant_y = self.find_number_upwards(y, x) # Looking for the first of a pair
			if non_vacant_y is None: break # No number was found, nothing is to be done
			if non_vacant_y < y:  
				self.grid[y][x] = self.grid[non_vacant_y][x]
				self.grid[non_vacant_y][x] = None
			y = y - 1	

	def move_down(self): # Thoughts : Should I merge all the move functions and pass the indexes..
		""" Moving coords to the right extreme of the board """
		for x in range(0,self.size): #Iterating from top to bottom
			self.__sweep_down(x)
			self.__collapse_pairs_bottom(x)
			self.__sweep_down(x)
		added  = self.__add_tile()
		return  self.is_game_over(added)


	def find_number_downwards(self,  y, x):
		while y < self.size: # Stops when you've found a number
			if self.grid[y][x] is not None: break
			y = y + 1
		result = y if y < self.size else None
		return result

	def __collapse_pairs_top(self,x):
		pair = None 
		y = 0
		while y < self.size and self.grid[y][x] != None: 
			pair = self.__collapse_vertical(y,x,pair)
			y = y + 1

	def __sweep_up(self,x):	
		y = 0
		while y < self.size: 
			non_vacant_y = self.find_number_downwards(y, x) # Looking for the first of a pair
			if non_vacant_y is None: break # No number was found, nothing is to be done
			if non_vacant_y > y:  
				self.grid[y][x] = self.grid[non_vacant_y][x]
				self.grid[non_vacant_y][x] = None
			y = y + 1	

	def move_up(self): # Thoughts : Should I merge all the move functions and pass the indexes..
		""" Moving coords to the right extreme of the board """
		for x in range(0,self.size): #Iterating from top to bottom
			self.__sweep_up(x)
			self.__collapse_pairs_top(x)
			self.__sweep_up(x)
		added  = self.__add_tile()
		return  self.is_game_over(added)