#!/usr/bin/python
import random
import pickle
import os.path
import copy
import numpy as np
from ListOperations import ListOperations

class Model(object):
	"""Handles all key event operations coming in from the 2048 view"""

	def __init__(self, size = 4):	
		""" Starts of a with a default board"""
		self.size = size									#Size of the edge of a grid
		self.grid = np.zeros((size,size),dtype=np.int)		#Using numpy for easier array translation
		self.max_score = 0
		# if os.path.isfile("2048.p"):
		# 	self.max_score = pickle.load( open( "2048.p", "rb" ) )
		self.listeners = []

	def start_game(self):
		self.score = 0
		self._add_number()

	def register_listener(self,listener):
		self.listeners.append(listener)

	def remove_listener(self,listener):
		self.listeners.remove(listener)

	def send_notification():
		pass

	def get_score(self):									 #Getters in python?
		return self.score
		
	def _add_number(self): 
		"""Find an empty spot and add new tile"""
		occupied_tiles = set()
		while len(occupied_tiles) <= self.size * self.size:
			coord = (random.randint(0,self.size - 1),random.randint(0,self.size - 1)) 
			if coord in occupied_tiles:
				continue
			elif self.grid[coord[0]][coord[1]] == 0:
				self.grid[coord[0]][coord[1]] = random.choice([2,4])
				for listener in self.listeners: 			#Send notifications
					listener.number_added(coord[0],coord[1],self.grid[coord[0]][coord[1]])
				return True
			else:
				occupied_tiles.add(coord)

		return False	

	def print_board(self):
		""" Printing exising board contents """
		print "Printing board"
		for x in range(0, self.size):
			for y in range(0, self.size):
				if (self.grid[x][y] == 0):
					print "-",
				else:
				 	print self.grid[x][y],
			print "\r"
	
	def move_left(self): 
		""" Moving numbers to the left extreme of the board """
		ops_log = []
		for y in range(0,self.size): #Iterating from top to bottom
			ops_log_row = ListOperations.collapse_list(self.grid[y,:])
			ops_log = ops_log + ops_log_row

		if len(ops_log) > 0:
			self._add_number()


	def move_right(self): 
		""" Moving numbers to the right extreme of the board """
		ops_log = []
		for y in range(0,self.size): #Iterating from top to bottom
			ops_log_row = ListOperations.collapse_list(self.grid[y,::-1])
			ops_log = ops_log + ops_log_row

		if len(ops_log) > 0:
			self._add_number()
	
	def move_up(self): 
		""" Moving numbers to the top extreme of the board """
		ops_log = []
		for x in range(0,self.size): #Iterating from left to right
			ops_log_row = ListOperations.collapse_list(self.grid[:,x])
			ops_log = ops_log + ops_log_row

		if len(ops_log) > 0:
			self._add_number()
	
	def move_down(self): 
		""" Moving numbers to the bottom extreme of the board """
		ops_log = []
		for x in range(0,self.size): #Iterating from left to right
			ops_log_row = ListOperations.collapse_list(self.grid[::-1,x])
			ops_log = ops_log + ops_log_row

		if len(ops_log) > 0:
			self._add_number()

	def _has_empty_spaces(self):
		for x in range(0,self.size):
			for y in range(0,self.size):
				if self.grid[x][y] == 0 : return True
		return False

	def is_game_over(self):
		""" Checking if number pairs are available in a full grid/ If further moves are possible"""
		if self._has_empty_spaces() == True:
			return False

		for y in range(0,self.size):
			if(ListOperations.is_pair_present(self.grid[y,:]) is True):
				return False
		for x in range(0,self.size):
			if(ListOperations.is_pair_present(self.grid[:,x]) is True):	
				return False
		return True
