import copy
class Node:
    """
    This class of Node contains the information of node in the search tree.
    each node contains board_state, his parent, successors.
    """
    def __init__(self, board_state, parent, depth, color, turns):
        # current state of the board this node represents
        self._board = board_state

        # parent node, used to traverse up sequence of nodes once goal state found
        self._parent = parent

        # collection of successor nodes
        self._successors = []

        # depth of the node in the tree, to know stop expanding because of cut-off
        self._depth = depth

        self._color = color

        self._turns = turns

    def get_turns(self):
        return self._turns

    def get_color(self):
        return self._color


    def get_board(self):
        return self._board

    def get_depth(self):
        return self._depth

    def expand_successors(self):
        self._board.check_shrink_board(self._turns)

        if self._board.get_is_place_phase():
            coords_list = self._board.get_empty_tiles(self._color)

            for coord in coords_list:
                row, col = coord[0], coord[1]

                # create copy of current board
                new_board = copy.deepcopy(self._board)


                # update the copy with the placement
                new_board.place_piece(self._color, (row, col))

                new_board.check_update_phase(self._turns)

                # update successors with the new board state
                self._successors.append(Node(new_board, self, self._depth + 1,
                new_board.get_opposite_color(self._color), self._turns + 1))

        else:
            coords_list = self._board.get_available_moves(self._color)
            for coord in coords_list:
                source, dest = coord[0], coord[1]
                source_row, source_col, dest_row, dest_col = source[0], source[1], dest[0], dest[1]

                # create copy of current board
                new_board = copy.deepcopy(self._board)


                # update the copy with the move
                new_board.move_piece(self._color, source_row, source_col, dest_row, dest_col)

                new_board.check_update_phase(self._turns)

                self._successors.append(Node(new_board, self, self._depth + 1,
                                             self._board.get_opposite_color(self._color), self._turns+1))

    def get_successors(self):
        return self._successors

    def get_parent(self):
        return self._parent

    def get_move(self):
        return self._move
