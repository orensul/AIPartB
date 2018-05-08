from BoardState import BoardState
from TileEnum import TileEnum
from Node import Node
import random
import copy
import time
import math

INFINITY = 100000
NEG_INFINITY = -100000
MAX_GAME_TIME = 240  #accounting for other player
MAX_MOVES = 112 #estimate for maximum moves a this player should make in the game
GAME_AVERAGE_BRANCHING_FACTOR = 40 # estimate

class Player:
    def __init__(self, colour):
        """
        called by the referee once at the beginning of the game to initialise.
        Here we will set the state of the board and more states we will want to maintain during the game.
        :param colour:  string representing the piece colour your program will control for this game.
        can be 'white' or 'black
        """

        #random.seed(9002)
        self._board = BoardState()
        if(colour == 'white'):
            self._color = TileEnum.WHITE_PIECE
            self._opponent_color = TileEnum.BLACK_PIECE
        elif(colour == 'black'):
            self._color = TileEnum.BLACK_PIECE
            self._opponent_color = TileEnum.WHITE_PIECE
        self._game_start_time = time.time()
        self._max_time_for_decision = 120/MAX_MOVES

    def update(self, action):
        """
        This method is called by the referee to inform your player about the opponent’s
        most recent move, so that you can maintain your internal board configuration.
        :param action: representation of the opponent’s recent action
        :return:
        """
        if not action == None:
            action = self.switch_row_column(action)
            self._board.take_action(action, self._opponent_color)



    def action(self, turns):
        """
        This method is called by the referee to request an action by your player.
        :param turns: turns is an integer representing the number of turns that have
        taken place since the start of the current game phase
        :return: the next action of the player in a format of:
                 (x,y) -  placing a piece on square (x,y)
                 ((a,b),(c,d)) -  moving a piece from square (a,b) to square (c,d)
        """
        self._max_time_for_decision = (MAX_GAME_TIME - (time.time() - self._game_start_time))/(2*(MAX_MOVES-((turns+1)/2)))   #/2 to account for only this players game time
        self._board.check_shrink_board(turns)

        actions = self._board.get_actions(turns,self._color)
        action = actions[random.randint(0, len(actions) - 1)]
        if not action == None:
            self._board.take_action(action, self._color)
            self._board.check_update_phase(turns)
            return self.switch_row_column(action)
        else:
            self._board.check_update_phase(turns)
            return None


    def is_cut_off(self, node):
        """
        :param node: node which represents a state of the board
        :return: boolean - true is node is in the depth of cut-off limit, false - otherwise.
        """
        if node.get_depth() >= self._minimax_cutoff_depth:
            return True
        return False




    def switch_row_column(self, action):
        if isinstance(action[0], tuple):
            return (action[0][::-1],action[1][::-1])
        else:
            return action[::-1]
