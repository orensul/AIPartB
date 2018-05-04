from BoardState import BoardState
from TileEnum import TileEnum
from Node import Node
from MC_Node import MC_Node
import random
import copy
import time
INITIAL_CUT_OFF_DEPTH_LIMIT = 2

class Player:
    def __init__(self, colour):
        """
        called by the referee once at the beginning of the game to initialise.
        Here we will set the state of the board and more states we will want to maintain during the game.
        :param colour:  string representing the piece colour your program will control for this game.
        can be 'white' or 'black
        """

        random.seed(9002)
        self._board = BoardState()
        if(colour == 'white'):
            self._color = TileEnum.WHITE_PIECE
            self._opponent_color = TileEnum.BLACK_PIECE
            self._monte_carlo_tree = MC_Node(copy.deepcopy(self._board), None, self._color, 0, None)
        elif(colour == 'black'):
            self._color = TileEnum.BLACK_PIECE
            self._opponent_color = TileEnum.WHITE_PIECE
            self._monte_carlo_tree = MC_Node(copy.deepcopy(self._board), None, self._opponent_color, 0, None)

        self._minimax_cutoff_depth = INITIAL_CUT_OFF_DEPTH_LIMIT

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
        #if self._board.get_is_place_phase():
            #self._monte_carlo_tree = self._monte_carlo_tree.get_child_from_move(action)


    def action(self, turns):
        """
        This method is called by the referee to request an action by your player.
        :param turns: turns is an integer representing the number of turns that have
        taken place since the start of the current game phase
        :return: the next action of the player in a format of:
                 (x,y) -  placing a piece on square (x,y)
                 ((a,b),(c,d)) -  moving a piece from square (a,b) to square (c,d)
        """
        actions = self._board.get_actions(turns,self._color)
        if len(actions) > 0:
            if self._board.get_is_place_phase():
                #action = actions[random.randint(0, len(actions) - 1)]
                action = self.minimax_decision(actions, turns)
            else:
                action = self.minimax_decision(actions, turns)
                #action = actions[random.randint(0, len(actions) - 1)]


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



    def minimax_decision(self, operators, turns):
        if len(operators) == 0:
            return None
        operation = operators[0]
        alpha = -10000
        beta = 10000
        for op in operators:
            #print(alpha)
            #print(beta)
            #print('-----------------------')
            op_board = copy.deepcopy(self._board)

            op_board.take_action(op, self._color)
            op_board.check_update_phase(turns)

            node = Node(op_board, None, 1, self._opponent_color, turns+1)

            curr_val= self.min_value(node,alpha,beta)
            if curr_val > alpha:
                alpha = curr_val
                operation = op

        return operation

    def max_value(self, node,alpha,beta):
        """
        :param node: node which represents a state of the board
        :return: evaluation function result
        """
        if self.is_cut_off(node):
            return node.get_eval(self._color)
        else:
            node.expand_successors()
            for child in node.get_successors():
                alpha = max([alpha,self.min_value(child,alpha,beta)])
                if alpha >= beta:
                    return beta
            return alpha

    def min_value(self, node,alpha,beta):
        """
        :param node: node which represents a state of the board
        :return: evaluation function result
        """
        if self.is_cut_off(node):
            return node.get_eval(self._color)
        else:
            node.expand_successors()
            for child in node.get_successors():
                beta = min([beta,self.max_value(child,alpha,beta)])
                if beta <= alpha:
                    return alpha
            return beta

    def switch_row_column(self, action):
        if isinstance(action[0], tuple):
            return (action[0][::-1],action[1][::-1])
        else:
            return action[::-1]
