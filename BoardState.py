
from TileEnum import TileEnum

BOARD_INITIAL_SIZE = 8


class BoardState:
    def __init__(self):

        # list of lists representing the board. Hold Tile objects
        self._board = []

        self._white_loc = []
        self._black_loc = []
        self._corner_loc = [(0, 0), (7, 0), (7, 7), (0, 7)]
        self._board_end = BOARD_INITIAL_SIZE
        self._board_start = BOARD_INITIAL_SIZE - self._board_end

        # initialize the board with empty tiles and corner tiles
        for row in range(self._board_end):
            row_list = []
            for col in range(self._board_end):
                if (row, col) in ((0, 0), (7, 0), (7, 7), (0, 7)):
                    row_list.append(TileEnum.CORNER_TILE)
                else:
                    row_list.append(TileEnum.EMPTY_TILE)
            self._board.append(row_list)

    def place_piece(self, color, coord):
        coord_row = coord[0]
        coord_col = coord[1]
        if color == 'white':
            self._white_loc.append(coord)
            # update board we placed a piece
            self._board[coord_row][coord_col] = TileEnum.WHITE_PIECE

        elif color == 'black':
            self._black_loc.append(coord)
            # update board we placed a piece
            self._board[coord_row][coord_col] = TileEnum.BLACK_PIECE

        # update board by removing surrounded piece
        self.remove_surrounded_piece(color, coord)

    def remove_piece(self, color, coord):
        coord_row = coord[0]
        coord_col = coord[1]
        self._board[coord_row][coord_col] = TileEnum.EMPTY_TILE
        if color == 'white':
            self._white_loc.remove(coord)
        elif color == 'black':
            self._black_loc.remove(coord)

    def get_empty_tiles(self, color):
        empty_tiles = []
        if color == 'white':
            start_board = self._board_start
            end_board = self._board_end - 2
        else:
            start_board = self._board_start + 2
            end_board = self._board_end

        for row in range(start_board, end_board):
            for col in range(len(self._board)):
                if self._board[row][col] == TileEnum.EMPTY_TILE:
                    empty_tiles.append((row, col))
        return empty_tiles

    def get_available_moves(self, color):
        available_moves = []
        if color == 'white':
            loc_list = self._white_loc
        else:
            loc_list = self._black_loc

        for piece in loc_list:
            row = piece[0]
            col = piece[1]

            left_move = self.check_left_move(row, col)
            if left_move is not None:
                available_moves.append(left_move)

            up_move = self.check_up_move(row, col)
            if up_move is not None:
                available_moves.append(up_move)

            right_move = self.check_right_move(row, col)
            if right_move is not None:
                available_moves.append(right_move)

            down_move = self.check_down_move(row, col)
            if down_move is not None:
                available_moves.append(down_move)
        return available_moves

    def check_left_move(self, row, col):
        if col > 0:
            if self._board[row][col - 1] == TileEnum.EMPTY_TILE:
                return (row, col), (row, col - 1)
            elif self._board[row][col - 1] in (TileEnum.BLACK_PIECE, TileEnum.WHITE_PIECE):
                if col - 1 > 0:
                    if self._board[row][col - 2] == TileEnum.EMPTY_TILE:
                        return (row, col), (row, col - 2)

    def check_up_move(self, row, col):
        if row > 0:
            if self._board[row-1][col] == TileEnum.EMPTY_TILE:
                return (row, col), (row - 1, col)
            elif self._board[row - 1][col] in (TileEnum.BLACK_PIECE, TileEnum.WHITE_PIECE):
                if row - 1 > 0:
                    if self._board[row - 2][col] == TileEnum.EMPTY_TILE:
                        return (row, col), (row - 2, col)

    def check_right_move(self, row, col):
        """
        check for move right, if exist return move object
        :param row: row of tile we are moving from
        :param col: column of tile we are moving from
        :return: move
        """
        if col < len(self._board) - 1:
            if self._board[row][col + 1] == TileEnum.EMPTY_TILE:
                return (row, col), (row, col + 1)
            elif self._board[row][col + 1] in (TileEnum.BLACK_PIECE, TileEnum.WHITE_PIECE):
                if col + 1 < len(self._board) - 1:
                    if self._board[row][col + 2] == TileEnum.EMPTY_TILE:
                        return (row, col), (row, col + 2)

    def check_down_move(self, row, col):
        """
        check for move down, if exist return move object
        :param row: row of tile we are moving from
        :param col: column of tile we are moving from
        :return: move
        """
        if row < len(self._board) - 1:
            if self._board[row + 1][col] == TileEnum.EMPTY_TILE:
                return (row, col) , (row + 1, col)
            elif self._board[row + 1][col] in (TileEnum.BLACK_PIECE, TileEnum.WHITE_PIECE):
                if row + 1 < len(self._board) - 1:
                    if self._board[row + 2][col] == TileEnum.EMPTY_TILE:
                        return (row, col), (row + 2, col)

    def remove_surrounded_piece(self, color, coord):
        coord_row = coord[0]
        coord_col = coord[1]
        if color == 'white':
            opposite_color_enum = TileEnum.BLACK_PIECE
        else:
            opposite_color_enum = TileEnum.WHITE_PIECE

        if coord_row == self._board_start or coord_row == self._board_end:
            if self._board[coord_row][coord_col - 1] \
                    in (opposite_color_enum, TileEnum.CORNER_TILE) and \
                    self._board[coord_row][coord_col + 1] \
                    in (opposite_color_enum, TileEnum.CORNER_TILE):
                        self.remove_piece(color, coord)
            elif coord_col == self._board_start or coord_col == self._board_end:
                if self._board[coord_row - 1][coord_col] \
                        in (opposite_color_enum, TileEnum.CORNER_TILE) and \
                        self._board[coord_row + 1][coord_col] \
                        in (opposite_color_enum, TileEnum.CORNER_TILE):
                    self.remove_piece(color, coord)
            else:
                if (self._board[coord_row][coord_col - 1] == opposite_color_enum and \
                    self._board[coord_row][coord_col + 1] == opposite_color_enum) \
                        or (self._board[coord_row - 1][coord_col] == opposite_color_enum and \
                            self._board[coord_row + 1][coord_col] == opposite_color_enum):
                    self.remove_piece(color, coord)
