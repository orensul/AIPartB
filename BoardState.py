
from TileEnum import TileEnum

BOARD_INITIAL_END = 7
TOTAL_TURNS_PLACE_PHASE = 24
FIRST_BOARD_SHRINK = 128
SECOND_BOARD_SHRINK = 192
BOARD_CENTRE = 3.5

class BoardState:
    def __init__(self):

        # list of lists representing the board. Hold Tile objects
        self._board_end = BOARD_INITIAL_END
        self._board_start = BOARD_INITIAL_END - self._board_end
        self._board = []
        self._is_place_phase = True
        self._piece_loc =[[],[],[(self._board_start,self._board_start),(self._board_end,self._board_start),(self._board_end,self._board_end),(self._board_start,self._board_end)] ] #3 lists for TileEnum.WHITE_PIECE, TileEnum.BLACK_PIECE and TileEnum.CORNER_TILE respectively accesses with enum value

        # initialize the board with empty tiles and corner tiles
        for row in range(self._board_end + 1):
            row_list = []
            for col in range(self._board_end + 1):
                if (row, col) in self._piece_loc[TileEnum.CORNER_TILE._value_]:
                    row_list.append(TileEnum.CORNER_TILE)
                else:
                    row_list.append(TileEnum.EMPTY_TILE)
            self._board.append(row_list)


    def get_actions(self, turns, color):
        self.check_shrink_board(turns)
        if self.get_is_place_phase():
            actions = self.get_available_placements(color)
        else:
            actions = self.get_available_moves(color)
        return actions

    def take_action(self, action, color):
        if isinstance(action[0], tuple):
            self.move_piece(color, action)
        else:
            self.place_piece(color, action)

    def get_available_placements(self, color):
        available_placements = []
        if color == TileEnum.WHITE_PIECE:
            range_start = self._board_start
            range_end = self._board_end - 2
        elif color == TileEnum.BLACK_PIECE:
            range_start = self._board_start + 2
            range_end = self._board_end

        for row in range(range_start, range_end + 1):
            for col in range(self._board_end + 1):
                if self._board[row][col] == TileEnum.EMPTY_TILE:
                    available_placements.append((row, col))
        return available_placements

    def get_available_moves(self, color):
        available_moves = []

        for piece in self._piece_loc[color._value_]:
            for direction in [(0,-1),(-1,0),(0,1),(1,0)]: #left,right,up,down
                adjacent = tuple([loc + dir for loc, dir in zip(piece,direction)])
                if self.square_free(adjacent, None):
                    available_moves.append((piece,adjacent))
                else:
                    adjacent = tuple([loc + dir for loc, dir in zip(adjacent,direction)])
                    if self.square_free(adjacent, None):
                        available_moves.append((piece,adjacent))
        return available_moves

    def square_free(self, coord, color):   #color may be None in case of checking available moves or a color if checking for surrounded pieces
        if color is None:
            return all([x >= self._board_start and x <= self._board_end for x in coord]) and self._board[coord[0]][coord[1]] == TileEnum.EMPTY_TILE
        else:
            return any([x < self._board_start or x > self._board_end for x in coord]) or self._board[coord[0]][coord[1]] in (TileEnum.EMPTY_TILE, color)

    def place_piece(self, color, coord):

        self._piece_loc[color._value_].append(coord)
        self._board[coord[0]][coord[1]] = color
        # remove pieces which are surrounded (first the opponent pieces)
        self.remove_surrounded_pieces(self.get_opposite_color(color))
        self.remove_surrounded_pieces(color)

    def remove_piece(self, color, coord):
        self._board[coord[0]][coord[1]] = TileEnum.EMPTY_TILE
        self._piece_loc[color._value_].remove(coord)

    def move_piece(self, color, action):
        # remove the piece from his source tile
        self.remove_piece(color, action[0])
        # place the piece on his dest tile
        self.place_piece(color, action[1])

    def remove_surrounded_pieces(self, color):
        for row, col in self._piece_loc[color._value_]:
            if (all([not self.square_free((row,col-1), color),not self.square_free((row,col+1), color)])
                or all([not self.square_free((row-1,col), color), not self.square_free((row+1,col), color)])):
                self.remove_piece(color, (row,col))

    def shrink_board(self):
        self._board_end -= 1
        self._board_start += 1

        # update the board with the new corners
        for row, col in self._piece_loc[TileEnum.CORNER_TILE._value_]:
            self._board[row][col] = TileEnum.EMPTY_TILE
        self._piece_loc[TileEnum.CORNER_TILE._value_] = [(self._board_start,self._board_start),(self._board_end,self._board_start),(self._board_end,self._board_end),(self._board_start,self._board_end)]
        for row, column in self._piece_loc[TileEnum.CORNER_TILE._value_]:
            self._board[row][column] = TileEnum.CORNER_TILE


        # remove from black_loc and white_loc lists pieces from old board locations
        for color in (TileEnum.WHITE_PIECE, TileEnum.BLACK_PIECE):
            to_delete = []
            for row, column in self._piece_loc[color._value_]:
                if any([x < self._board_start or x > self._board_end for x in [row,column]]):
                    self._board[row][column] = TileEnum.EMPTY_TILE
                    to_delete.append((row,column))
                if (row,column) in self._piece_loc[TileEnum.CORNER_TILE._value_]:
                    to_delete.append((row,column))
            for piece in to_delete:
                self._piece_loc[color._value_].remove(piece)

        #remove all pieces surrounded by the new corner pieces in a clockwise manner from top left corner
        for piece in self._piece_loc[TileEnum.CORNER_TILE._value_]:
            for direction in [(0,-1),(-1,0),(0,1),(1,0)]: #left,right,up,down
                (row,col) = tuple([loc + dir for loc, dir in zip(piece,direction)])
                color = self._board[row][col]
                if color in (TileEnum.WHITE_PIECE, TileEnum.BLACK_PIECE):
                    if (all([not self.square_free((row,col-1), color),not self.square_free((row,col+1), color)])
                        or all([not self.square_free((row-1,col), color), not self.square_free((row+1,col), color)])):
                        self.remove_piece(color, (row,col))


    def get_is_place_phase(self):
        return self._is_place_phase

    '''Possibly a problem here around board shinking for minimax. Because of how check_shrink_board() works may shrink twice. UPDATED'''
    def check_shrink_board(self, turns):
        if turns in (FIRST_BOARD_SHRINK, FIRST_BOARD_SHRINK + 1):
            if BOARD_INITIAL_END - self._board_end == 0:
                self.shrink_board()
        if turns in (SECOND_BOARD_SHRINK , SECOND_BOARD_SHRINK + 1):
            if BOARD_INITIAL_END - self._board_end == 1:
                self.shrink_board()


    def check_update_phase(self, turns):
        if turns == TOTAL_TURNS_PLACE_PHASE - 1 or turns == TOTAL_TURNS_PLACE_PHASE - 2:
            self._is_place_phase = False

    def get_remaining_pieces(self, color):
        return len(self._piece_loc[color._value_])

    def rank_centre_control(self, color):
        rating = 0
        for row, column in self._piece_loc[color._value_]:
            rating +=  (9.5 - abs(column-BOARD_CENTRE) - abs(row-BOARD_CENTRE))
        if self.get_remaining_pieces(color) > 0:
            rating = rating/self.get_remaining_pieces(color)
        return rating


    def get_opposite_color(self, color):
        if color == TileEnum.WHITE_PIECE:
            return TileEnum.BLACK_PIECE
        elif color == TileEnum.BLACK_PIECE:
            return TileEnum.WHITE_PIECE

    def print_board(self):
        print('INTERNALBOARD: _____________________________________________________________')
        for i in range(len(self._board)):
            row = ''
            for j in range(len(self._board)):
                if self._board[i][j] == TileEnum.BLACK_PIECE:
                    row += '@ '
                elif self._board[i][j] == TileEnum.WHITE_PIECE:
                    row += 'O '
                elif self._board[i][j] == TileEnum.EMPTY_TILE:
                    row += '- '
                else:
                    row += 'X '
            print(row)
        print('____________________________________________________________________________________')
