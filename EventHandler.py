#!/usr/bin/python

import random

class EventHandler(object):
	"""Handles all key event operations coming in from the 2048 view"""

	def __init__(self, gridsize = 4):	
		super(EventHandler, self).__init__()
		""" Starts of a with a default board"""
		self.gridsize = gridsize

	def StartGame():
		self.data = [[]]

	def GenerateRandomTile(self):
		coord = {}
		coord["tileX"] = random.randint(0,self.gridsize) #Assuming X start from the top left and increases as you go right
		coord["tileY"] = random.randint(0,self.gridsize) #Assuming Y start from the top left and increases as you go to the bottom
		return coord

	def LoadBoard(self):
		pass

	def PrintBoard(self):
		for x in range

	def Moveleft(self):
		pass

	def MoveRight(self):
		pass
