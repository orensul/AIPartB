
from TileEnum import TileEnum
import math

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
            for direction in [(0,-1),(-1,0),(0,1),(1,0)]: #left,up,right,down
                adjacent = tuple([loc + dir for loc, dir in zip(piece,direction)])
                if self.square_viable(adjacent, None):
                    available_moves.append((piece,adjacent))
                else:
                    adjacent = tuple([loc + dir for loc, dir in zip(adjacent,direction)])
                    if self.square_viable(adjacent, None):
                        available_moves.append((piece,adjacent))
        return available_moves

    def square_viable(self, coord, color):   #color may be None in case of checking available moves or a color if checking for surrounded pieces
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
            if (all([not self.square_viable((row,col-1), color),not self.square_viable((row,col+1), color)])
                or all([not self.square_viable((row-1,col), color), not self.square_viable((row+1,col), color)])):
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
            for direction in [(0,-1),(-1,0),(0,1),(1,0)]: #left,up,right,down
                (row,col) = tuple([loc + dir for loc, dir in zip(piece,direction)])
                color = self._board[row][col]
                if color in (TileEnum.WHITE_PIECE, TileEnum.BLACK_PIECE):
                    if (all([not self.square_viable((row,col-1), color),not self.square_viable((row,col+1), color)])
                        or all([not self.square_viable((row-1,col), color), not self.square_viable((row+1,col), color)])):
                        self.remove_piece(color, (row,col))


    def get_is_place_phase(self):
        return self._is_place_phase

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


    def rank_piece_threats(self,piece,color,turn):
        threats_made = 0
        threats_recieved = 0
        '''need to know if the team we are evaluating has the next move or not'''
        next_to_move = any([turn % 2 == 0 and color == TileEnum.WHITE_PIECE,(not turn % 2 == 0) and color == TileEnum.BLACK_PIECE])

        for direction in [(0,-1),(-1,0),(0,1),(1,0)]: #left,up,right,down
            (row,col) = tuple([loc + dir for loc, dir in zip(piece,direction)])
            if all([x >= self._board_start and x <= self._board_end for x in (row,col)]):
                if self._board[row][col] == self.get_opposite_color(color):
                    (row,col) = tuple([loc + dir for loc, dir in zip((row,col),direction)])
                    if all([x >= self._board_start and x <= self._board_end for x in (row,col)]):
                        if self._board[row][col] == TileEnum.EMPTY_TILE:
                            threats_made +=1

        sides = [[(0,-1),(0,1)],[(-1,0),(1,0)]]
        for side in sides:
            adjacent = []
            for direction in side:
                coord = tuple([loc + dir for loc, dir in zip(piece,direction)])
                if all([x >= self._board_start and x <= self._board_end for x in coord]):
                    adjacent.append(self._board[coord[0]][coord[1]])
            if all([TileEnum.EMPTY_TILE in adjacent, self.get_opposite_color(color) in adjacent]):
                threats_recieved += 1
        if threats_recieved > 1 and next_to_move:
            threats_recieved -= 1
        elif threats_made > 1 and not next_to_move:
            threats_made -= 1

        return 10 * (threats_made-(threats_recieved))



    def rank_piece_exposure(self, piece, color):
        score = 0
        sides = [[(0,-1),(0,1)],[(-1,0),(1,0)]]
        for side in sides:
            adjacent = []
            for direction in side:
                coord = tuple([loc + dir for loc, dir in zip(piece,direction)])
                if all([x >= self._board_start and x <= self._board_end for x in coord]):
                    adjacent.append(self._board[coord[0]][coord[1]])
            if not color in adjacent:
                score += 1
        return -5 * score


    def rank_piece_loc(self, piece):
        from_centre = max([abs(piece[0]-BOARD_CENTRE), abs(piece[1]-BOARD_CENTRE)])
        if self._board_end == BOARD_INITIAL_END:
            if from_centre == 0.5:
                return 100
            if from_centre == 1.5:
                return 80
            if from_centre == 2.5:
                return 60
            if from_centre == 3.5:
                return 50
        elif self._board_end == BOARD_INITIAL_END - 1:
            if from_centre == 0.5:
                return 100
            if from_centre == 1.5:
                return 80
            if from_centre == 2.5:
                return 70
        elif self._board_end == BOARD_INITIAL_END - 2:
            if from_centre == 0.5:
                return 100
            if from_centre == 1.5:
                return 90



    def rank_piece_mobility(self, piece):
        score = 0
        for direction in [(0,-1),(-1,0),(0,1),(1,0)]: #left,right,up,down
            adjacent = tuple([loc + dir for loc, dir in zip(piece,direction)])
            if self.square_viable(adjacent, None):
                score += 1
            else:
                adjacent = tuple([loc + dir for loc, dir in zip(adjacent,direction)])
                if self.square_viable(adjacent, None):
                    score += 1
        if score == 0:
            return 0
        if score == 1:
            return 3
        if score == 2:
            return 5
        if score == 3:
            return 6
        if score == 4:
            return 8

    def evaluation(self,color,turn):
        team_score = 0
        for piece in self._piece_loc[color._value_]:
            piece_score = self.rank_piece_loc(piece) + self.rank_piece_mobility(piece)
            piece_score += self.rank_piece_exposure(piece, color) + self.rank_piece_threats(piece, color, turn)
            if self._is_place_phase:
                piece_score = piece_score/self.ideal_pieces(color,turn)
            team_score += piece_score

        for piece in self._piece_loc[self.get_opposite_color(color)._value_]:
            piece_score = self.rank_piece_loc(piece) + self.rank_piece_mobility(piece)
            piece_score += self.rank_piece_exposure(piece, self.get_opposite_color(color)) + self.rank_piece_threats(piece, self.get_opposite_color(color), turn)
            if self._is_place_phase:
                piece_score = piece_score/self.ideal_pieces(self.get_opposite_color(color),turn)
            team_score -= piece_score
        return team_score

    def ideal_pieces(self,color,turn):
        if color == TileEnum.WHITE_PIECE:
            return (math.ceil((turn)/2))
        else:
            return (math.ceil((turn-1)/2))

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
