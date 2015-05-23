#!/usr/bin/python

from Model import Model
from View import View

class Controller(object):

    def __init__(self):
        self.handler = Model()
        self.view = View()
        self.view.set_controller(self)
        self.handler.register_listener(self.view)
        self.view.load_view()

    def start(self):
        self.handler.start_game()

    def handle_key_left(self):
        self.handler.move_left()

    def handle_key_right(self):
        self.handler.move_right()

    def handle_key_up(self):
        self.handler.move_up()

    def handle_key_down(self):
        self.handler.move_down()

controller = Controller()
