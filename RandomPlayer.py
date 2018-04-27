from BoardState import BoardState
from Node import Node
import random
import copy
CUT_OFF_DEPTH_LIMIT = 3

# a constant
INFINITY = 1.0e400

class Player:
    def __init__(self, colour):
        """
        called by the referee once at the beginning of the game to initialise.
        Here we will set the state of the board and more states we will want to maintain during the game.
        :param colour:  string representing the piece colour your program will control for this game.
        can be 'white' or 'black
        """

        random.seed(9002)
        self._color = colour
        self._opponent_color = self.get_opponent_color()
        self._board = BoardState()

    def get_opponent_color(self):
        if self._color == 'white':
            return 'black'
        return 'white'

    def is_cut_off(self, node):
        """
        :param node: node which represents a state of the board
        :return: boolean - true is node is in the depth of cut-off limit, false - otherwise.
        """
        if node.get_depth() >= CUT_OFF_DEPTH_LIMIT:
            return True
        return False

    def minimax_decision(self, operators, turns):
        max_val = -INFINITY
        operation = operators[0]
        alpha = - INFINITY
        beta = INFINITY

        for op in operators:
            op_board = copy.deepcopy(self._board)
            if op_board.get_is_place_phase():
                row, col = op[0], op[1]
                op_board.place_piece(self._color, (row, col))
            else:
                source, dest = op[0], op[1]
                source_row, source_col, dest_row, dest_col = source[0], source[1], dest[0], dest[1]

                op_board.move_piece(self._color, source_row, source_col, dest_row, dest_col)

            node = Node(op_board, None, 1, self._opponent_color, turns+1)

            curr_val = self.minimax_value(node, 0, True, alpha, beta)
            if curr_val > alpha:
                alpha = curr_val
                operation = op
            if curr_val < beta:
                beta = curr_val

        return operation

    def minimax_value(self, node, depth, is_maximizing_player, alpha, beta):

        if self.is_cut_off(node):
            eval = node.get_eval(self._color)
            return eval

        node.expand_successors()

        if is_maximizing_player:
            best_val = - INFINITY
            for child in node.get_successors():
                value = self.minimax_value(child, depth+1, False, alpha, beta)
                best_val = max(best_val, value)
                alpha = max(alpha, best_val)
                if beta <= alpha:
                    break
            return best_val
        else:
            best_val = INFINITY
            for child in node.get_successors():
                value = self.minimax_value(child, depth+1, True, alpha, beta)
                best_val = min(best_val, value)
                beta = min(beta, best_val)
                if beta <= alpha:
                    break
            return best_val





    def action(self, turns):
        """
        This method is called by the referee to request an action by your player.
        :param turns: turns is an integer representing the number of turns that have
        taken place since the start of the current game phase
        :return: the next action of the player in a format of:
                 (x,y) -  placing a piece on square (x,y)
                 ((a,b),(c,d)) -  moving a piece from square (a,b) to square (c,d)
        """
        self._board.check_shrink_board(turns)
        if self._board.get_is_place_phase():
            coords_list = self._board.get_empty_tiles(self._color)
            #coord = self.minimax_decision(coords_list, turns)
            coord = coords_list[random.randint(0, len(coords_list) - 1)]
            row, col = coord[0], coord[1]
            self._board.place_piece(self._color, (row, col))
            return_val = col, row

        else:
            coords_list = self._board.get_available_moves(self._color)
            #coord = self.minimax_decision(coords_list, turns)

            coord = coords_list[random.randint(0, len(coords_list) - 1)]
            source, dest = coord[0], coord[1]
            source_row, source_col, dest_row, dest_col = source[0], source[1], dest[0], dest[1]

            self._board.move_piece(self._color, source_row, source_col, dest_row, dest_col)

            return_val = (source_col, source_row), (dest_col, dest_row)

        self._board.check_update_phase(turns)

        return return_val

    def update(self, action):
        """
        This method is called by the referee to inform your player about the opponent’s
        most recent move, so that you can maintain your internal board configuration.
        :param action: representation of the opponent’s recent action
        :return:
        """

        if not isinstance(action[0], tuple):
            self._board.place_piece(self._opponent_color, (action[1], action[0]))
        else:
            self._board.remove_piece(self._opponent_color, (action[0][1], action[0][0]))
            self._board.place_piece(self._opponent_color, (action[1][1], action[1][0]))
