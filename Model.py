#!/usr/bin/python
import random
import pickle
import os.path
import numpy as np
import ListOps


class Model(object):
    """Handles all key event operations coming in from the 2048 view"""
    FILE_NAME = "2048.p"

    def __init__(self, size=4):
        self.size = size
        # Using numpy for easy array transforms
        self.grid = np.zeros((size, size), dtype=np.int)
        self._load_score()
        self.listeners = []

    def _load_score(self):
        self.max_score = 0
        if os.path.isfile(self.FILE_NAME):
            self.max_score = pickle.load(open(self.FILE_NAME, "rb"))

    def _save_score(self):
        pickle.dump(self.max_score,open(self.FILE_NAME, "wb"))

    def start_game(self):
        self.score = 0
        self._add_number()

    def register_listener(self, listener):
        self.listeners.append(listener)

    def remove_listener(self, listener):
        self.listeners.remove(listener)

    def send_notification(self, notification):
        for listener in self.listeners:
            listener.notify(notification)

    def get_score(self):
        return self.score

    def get_max_score(self):
        return self.max_score

    def _get_rand_coord(self):
        """ Returns a random value coord"""
        return random.randint(0, self.size-1), random.randint(0, self.size-1)

    def _add_number(self):
        """Find an empty spot and add new tile"""
        occupied_tiles = set()
        while len(occupied_tiles) <= self.size * self.size:
            x, y = self._get_rand_coord()
            if (x, y) in occupied_tiles:                        # Already checked this spot in a prev iteration
                continue
            elif self.grid[x][y] == 0:
                self.grid[x][y] = random.choice([2, 4])
                self.send_notification({'State': ListOps.NEW, 'to_x': x,
                                        "to_y": y, "val": self.grid[x][y]})
                return True
            else:
                occupied_tiles.add((x, y))
        return False

    def get_board_string(self):
        """ String rep of the board"""
        string = ""
        for row in self.grid:
            for element in row:
               eleStr= " - " if element == 0 else " "+str(element)+" "
               string = string +eleStr
            string = string + "\n"
        return string

    def _process_results(self, logs, axis):
        if all(not log for log in logs):
            return

        self._add_number()
        for log in logs:
            for entry in log:
                if entry["State"] == ListOps.ADD:
                    self.score = self.score + entry["to_val"]
        return axis, logs

    def move_left(self):
        """ Moving numbers to the left extreme of the board """
        return self._process_results([ListOps.collapse_list(self.grid[y, :], 0)
                                      for y in range(self.size)], "y")

    def move_right(self):
        """ Moving numbers to the right extreme of the board """
        return self._process_results([ListOps.collapse_list(self.grid[y, ::-1], self.size)
                                      for y in range(self.size)], "y")

    def move_up(self):
        """ Moving numbers to the top extreme of the board """
        return self._process_results([ListOps.collapse_list(self.grid[:, x], 0)
                                      for x in range(self.size)], "x")

    def move_down(self):
        """ Moving numbers to the bottom extreme of the board """
        return self._process_results([ListOps.collapse_list(self.grid[::-1, x], self.size)
                                      for x in range(self.size)], "x")

    def _has_empty_spaces(self):
        for x in range(0, self.size):
            for y in range(0, self.size):
                if self.grid[x][y] == 0:
                    return True
        return False

    def is_game_over(self):
        """ Checking if number pairs are available in a full grid/ If further moves are possible"""
        if self._has_empty_spaces():
            return False

        for y in range(0, self.size):
            if(ListOps.is_pair_present(self.grid[y, :])):
                return False
        for x in range(0, self.size):
            if(ListOps.is_pair_present(self.grid[:, x])):
                return False
        if self.score > self.max_score:
            self.max_score = self.score
            self._save_score()

        return True
