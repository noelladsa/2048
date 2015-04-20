#!/usr/bin/python
from Model import Model


def game_over(handler):
    print "Game Over!"
    print (handler.get_board_string())
    score = handler.get_score()
    print "Your Score is",score

handler = Model()
handler.start_game()

response = None
while(response != "q"):
    print (handler.get_board_string())
    response = raw_input("Enter a move: l - left, r - right, u - up, d - down")
    move_result = ""
    if response == "l":
        move_result = handler.move_left()
    elif response == "r":
        move_result = handler.move_right()
    elif response == "u":
        move_result = handler.move_up()
    elif response == "d":
        move_result = handler.move_down()

    if handler.is_game_over() is True:
        game_over(handler)
        break
