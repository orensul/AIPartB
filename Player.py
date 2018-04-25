from BoardState import BoardState
from Node import Node
import random
import copy
CUT_OFF_DEPTH_LIMIT = 4

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
        self._is_place_phase = True

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
        max_val = 0
        operation = operators[0]
        for op in operators:
            op_board = copy.deepcopy(self._board)
            if op_board._is_place_phase:
                row = op[0]
                col = op[1]
                self._board.place_piece(self._color, (row, col))
            else:

                source = op[0]
                dest = op[1]

                source_row = source[0]
                source_col = source[1]

                dest_row = dest[0]
                dest_col = dest[1]

                self._board.move_piece(source_row, source_col, dest_row, dest_col)

            node = Node(op_board, None, 0, self._opponent_color, turns+1)

            curr_val = self.minimax_value(node)
            if curr_val >= max_val:
                max_val = curr_val
                operation = op
        return op

    def minimax_value(self, node):
        """
        :param node: node which represents a state of the board
        :return: evaluation function result
        """
        if self.is_cut_off(node):
            return node.eval()
        elif node.get_color() == self._color:
            node.expand_successors()
            return max(node.get_eval() for node in node.get_successors())
        else:
            node.expand_successors()
            return min(node.get_eval() for node in node.get_successors())

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
        if self._is_place_phase:
            coords_list = self._board.get_empty_tiles(self._color)
            print (coords_list)
            coord = self.minimax_decision(coords_list, turns)
            #coord = coords_list[random.randint(0, len(coords_list) - 1)]
            row = coord[0]
            col = coord[1]
            self._board.place_piece(self._color, (row, col))
            return_val = col, row

        else:
            coords_list = self._board.get_available_moves(self._color)
            coord = coords_list[random.randint(0, len(coords_list) - 1)]
            print("coord random")
            print(coord)

            source = coord[0]
            dest = coord[1]

            source_row = source[0]
            source_col = source[1]

            dest_row = dest[0]
            dest_col = dest[1]

            self._board.move_piece(source_row, source_col, dest_row, dest_col)

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
