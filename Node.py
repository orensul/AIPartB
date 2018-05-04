import copy
import random
class Node:
    """
    This class of Node contains the information of node in the search tree.
    each node contains board_state, his parent, successors.
    """
    def __init__(self, board_state, parent, depth, color, turn):

        random.seed(9002)
        # current state of the board this node represents
        self._board = board_state
        # parent node, used to traverse up sequence of nodes once goal state found
        self._parent = parent
        # collection of successor nodes
        self._successors = []
        # depth of the node in the tree, to know stop expanding because of cut-off
        self._depth = depth
        self._color = color
        self._turn = turn

    def get_color(self):
        return self._color
    def get_eval(self, color):
        #return  random.randint(5,200000) +random.randint(5,2000)
        return self._board.rank_centre_control(color) + 0*len(self._board.get_available_moves(color))+18*(self._board.get_remaining_pieces(color)-self._board.get_remaining_pieces(self._board.get_opposite_color(color)))
    def get_board(self):
        return self._board
    def get_depth(self):
        return self._depth
    def get_turn(self):
        return self._turn
    def get_successors(self):
        return self._successors
    def get_parent(self):
        return self._parent

    def expand_successors(self):
        actions = self._board.get_actions(self._turn,self._color)
        if len(actions) > 0:
            for action in actions:
                    # create copy of this node's board
                    new_board = copy.deepcopy(self._board)
                    # update the copy with the action
                    new_board.take_action(action, self._color)
                    new_board.check_update_phase(self._turn)
                    # update successors with the new board state
                    self._successors.append(Node(new_board, self, self._depth + 1, new_board.get_opposite_color(self._color),self._turn + 1))
