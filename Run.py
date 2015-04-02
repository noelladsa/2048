#!/usr/bin/python

from EventHandler import EventHandler


def game_over(handler):
	print "Game Over!"
	score = handler.get_score()
	print "Your Score is",score

handler = EventHandler()
response = None
while(response != "q"):
	handler.print_board()
	response = raw_input("Enter a move: l - left, r - right, u - up, d - down")
	move_result = False
	if response == "l":
		move_result =  handler.move_left()
	elif response == "r":
		move_result =  handler.move_right()
	elif response == "u":
		move_result =  handler.move_up()
	elif response == "d":
		move_result = handler.move_down()

	if move_result is True : 
		game_over(handler)
		break
