
from TileEnum import TileEnum
import math

BOARD_INITIAL_END = 7
TOTAL_TURNS_PLACE_PHASE = 24
FIRST_BOARD_SHRINK = 128
SECOND_BOARD_SHRINK = 192
BOARD_CENTRE = 3.5


"""
BoardState Class handles the representation and update of the current game state for the player as well
as evaluating the game state for the MiniMax-alpha-beta algorithm of node. Objects of this class
are held by both the player object and within nodes of the minimax search tree
@ authors: Tasrael,  Last updated May 2018
"""
class BoardState:
    def __init__(self):
        '''dimensions of the board that pieces can be on'''
        self._board_end = BOARD_INITIAL_END
        self._board_start = BOARD_INITIAL_END - self._board_end
        self._board = []
        self._is_place_phase = True
        '''list of lists holds the tuple locations of the pieces for both teams and the corners
        accessed by using the values of the TileEnum class to retrieve the corrent list
        0:White, 1:Black, 2:Corner'''
        self._piece_loc =[[],[],[(self._board_start,self._board_start),(self._board_end,self._board_start),(self._board_end,self._board_end),(self._board_start,self._board_end)] ] #3 lists for TileEnum.WHITE_PIECE, TileEnum.BLACK_PIECE and TileEnum.CORNER_TILE respectively accesses with enum value

        '''initialize the board with empty tiles and corner tiles'''
        for row in range(self._board_end + 1):
            row_list = []
            for col in range(self._board_end + 1):
                if (row, col) in self._piece_loc[TileEnum.CORNER_TILE._value_]:
                    row_list.append(TileEnum.CORNER_TILE)
                else:
                    row_list.append(TileEnum.EMPTY_TILE)
            self._board.append(row_list)

    def get_is_place_phase(self):
        """
        :return: if the board_state is still in the placing phase
        """
        return self._is_place_phase

    def get_actions(self, turns, color):
        """
        From the current game turn returns the actions that a particular team
        has available to make in the current state
        :param turns current turn the game is at
        :param color the team whose available actions we retrieve
        :return: a list of actions (either placements or moves depending on the phase)
        """
        self.check_shrink_board(turns)
        if self.get_is_place_phase():
            actions = self.get_available_placements(color)
        else:
            actions = self.get_available_moves(color)
        return actions

    def take_action(self, action, color):
        """
        Update the board with a placement or move action for a particular
        team.
        :param action the action to implement
        :param color the team who takes the action
        """
        if isinstance(action[0], tuple):
            self.move_piece(color, action)
        else:
            self.place_piece(color, action)

    def get_available_placements(self, color):
        """
        From the current game state retrieve the placements available
        to a particular team.
        :param color the team whose available placements we retrieve
        :return: a list of placement tuples
        """
        available_placements = []
        '''White and Black can only place in certain row regions'''
        if color == TileEnum.WHITE_PIECE:
            range_start = self._board_start
            range_end = self._board_end - 2
        elif color == TileEnum.BLACK_PIECE:
            range_start = self._board_start + 2
            range_end = self._board_end

        for row in range(range_start, range_end + 1):
            for col in range(self._board_end + 1):
                if self._board[row][col] == TileEnum.EMPTY_TILE:
                    '''location on board is blank and can be placed in'''
                    available_placements.append((row, col))
        return available_placements

    def get_available_moves(self, color):
        """
        From the current game state retrieve the moves available
        to a particular team.
        :param color the team whose available placements we retrieve
        :return: a list of move nested tuples
        """
        available_moves = []

        for piece in self._piece_loc[color._value_]:
            '''check the tiles on each side of each piece'''
            for direction in [(0,-1),(-1,0),(0,1),(1,0)]:
                adjacent = tuple([loc + dir for loc, dir in zip(piece,direction)])
                if self.square_viable(adjacent, None):
                    available_moves.append((piece,adjacent))
                else:
                    '''check for a jump to the tile past the adjacent'''
                    adjacent = tuple([loc + dir for loc, dir in zip(adjacent,direction)])
                    if self.square_viable(adjacent, None):
                        available_moves.append((piece,adjacent))
        return available_moves

    def square_viable(self, coord, color):
        """
        Check a particular location on the board for placement availability or
        if it can refute a piece being surrounded'''
        :param coord the location we are investigating
        :param color if specified identifies friendly pieces
        :return: True if able to be placed on or if not contributing to a piece being surrounded
        """
        if color is None:
            '''used for checking moves. If coord on the board and empty is viable'''
            return all([x >= self._board_start and x <= self._board_end for x in coord]) and self._board[coord[0]][coord[1]] == TileEnum.EMPTY_TILE
        else:
            '''used for checking for surrounded pieces. If the tile is off
            the board or is empty or a friendly piece it is viable (i.e not
            contributing to a piece being surronded)'''
            return any([x < self._board_start or x > self._board_end for x in coord]) or self._board[coord[0]][coord[1]] in (TileEnum.EMPTY_TILE, color)

    def place_piece(self, color, coord):
        """
        update the board with a piece at a specified location
        :param color the team of the piece being placed
        :param coord the location we are placing at
        """
        self._piece_loc[color._value_].append(coord)
        self._board[coord[0]][coord[1]] = color
        ''' remove pieces which are surrounded (first the opponent pieces)'''
        self.remove_surrounded_pieces(self.get_opposite_color(color))
        self.remove_surrounded_pieces(color)

    def remove_piece(self, color, coord):
        """
        update the board by removing a piece at a specified location
        :param color the team of the piece being removed
        :param coord the location we are removing from
        """
        self._board[coord[0]][coord[1]] = TileEnum.EMPTY_TILE
        self._piece_loc[color._value_].remove(coord)

    def move_piece(self, color, action):
        """
        Remove a teams piece from one location and place at a new one
        :param color the team of the piece being moved
        :param action specifies the move to make (nested tuple)
        """
        # remove the piece from his source tile
        self.remove_piece(color, action[0])
        # place the piece on his dest tile
        self.place_piece(color, action[1])

    def remove_surrounded_pieces(self, color):
        """
        Check all pieces of a team and if they are surrounded remove them
        :param color the team of the piece being placed
        """
        for row, col in self._piece_loc[color._value_]:
            if (all([not self.square_viable((row,col-1), color),not self.square_viable((row,col+1), color)])
                or all([not self.square_viable((row-1,col), color), not self.square_viable((row+1,col), color)])):
                self.remove_piece(color, (row,col))

    def shrink_board(self):
        """
        update the dimensions of the available board and it's corner tiles
        if pieces outside the new board, at loc of new corners or surrounded
        by new corners remove them.
        """
        '''update dimensions'''
        self._board_end -= 1
        self._board_start += 1

        '''update the board with the new corners'''
        for row, col in self._piece_loc[TileEnum.CORNER_TILE._value_]:
            self._board[row][col] = TileEnum.EMPTY_TILE
        self._piece_loc[TileEnum.CORNER_TILE._value_] = [(self._board_start,self._board_start),(self._board_end,self._board_start),(self._board_end,self._board_end),(self._board_start,self._board_end)]
        for row, column in self._piece_loc[TileEnum.CORNER_TILE._value_]:
            self._board[row][column] = TileEnum.CORNER_TILE


        ''' remove pieces from outside the new board dimensions'''
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

        '''remove all pieces surrounded by the new corner pieces in an anticlockwise manner from top left corner'''
        for piece in self._piece_loc[TileEnum.CORNER_TILE._value_]:
            for direction in [(0,-1),(-1,0),(0,1),(1,0)]: #left,up,right,down
                (row,col) = tuple([loc + dir for loc, dir in zip(piece,direction)])
                color = self._board[row][col]
                if color in (TileEnum.WHITE_PIECE, TileEnum.BLACK_PIECE):
                    if (all([not self.square_viable((row,col-1), color),not self.square_viable((row,col+1), color)])
                        or all([not self.square_viable((row-1,col), color), not self.square_viable((row+1,col), color)])):
                        self.remove_piece(color, (row,col))




    def check_shrink_board(self, turns):
        """
        If at an appropriate turn an the board has not been shrunk yet,
        Shrink it
        :param turns current turn the game is at
        """
        if turns in (FIRST_BOARD_SHRINK, FIRST_BOARD_SHRINK + 1):
            if BOARD_INITIAL_END - self._board_end == 0:
                self.shrink_board()
        if turns in (SECOND_BOARD_SHRINK , SECOND_BOARD_SHRINK + 1):
            if BOARD_INITIAL_END - self._board_end == 1:
                self.shrink_board()


    def check_update_phase(self, turns):
        """
        If at an appropriate turn, update to the moving phase
        :param turns current turn the game is at
        """
        if turns == TOTAL_TURNS_PLACE_PHASE - 1 or turns == TOTAL_TURNS_PLACE_PHASE - 2:
            self._is_place_phase = False


    def get_remaining_pieces(self, color):
        """
        :param color the team whose pieces we are counting
        :return the number of pieces that team has remaining in this boardstate
        """
        return len(self._piece_loc[color._value_])




    def evaluation(self,color,turn):
        """
        Evaluate the boardstate for a team by scoring attributes of all pieces for said
        team and subtracting those of the enemy team. Used for Minimax-alpha-beta
        :param turn current turn the game is at
        :param color the team whose the evaluation function is focusing on
        :return: the evaluation function score
        """
        team_score = 0
        for piece in self._piece_loc[color._value_]:
            piece_score = self.rank_piece_loc(piece) + self.rank_piece_mobility(piece)
            piece_score += self.rank_piece_exposure(piece, color) + self.rank_piece_threats(piece, color, turn)
            if self._is_place_phase:
                '''if placing phase can have a natural imbalance of piece numbers
                depending on turn, normalize for this by dividing score by the
                mx number of pieces this team could have this turn'''
                piece_score = piece_score/self.ideal_pieces(color,turn)
            team_score += piece_score

        for piece in self._piece_loc[self.get_opposite_color(color)._value_]:
            piece_score = self.rank_piece_loc(piece) + self.rank_piece_mobility(piece)
            piece_score += self.rank_piece_exposure(piece, self.get_opposite_color(color)) + self.rank_piece_threats(piece, self.get_opposite_color(color), turn)
            if self._is_place_phase:
                piece_score = piece_score/self.ideal_pieces(self.get_opposite_color(color),turn)
            team_score -= piece_score

        return team_score

    def rank_piece_threats(self,piece,color,turn):
        """
        Count the number of threats to other team a particular piece makes,
        and how many it recieves and score it. This method accounts for which team is
        next to move to protect against bad evaluations on the edge of a minimax iteration
        :param piece the location of the piece we are evaluating
        :param turns current turn the game is at
        :param color the team whose threats we are evaluating
        :return: score depending on the balance of threats
        """
        threats_made = 0
        threats_recieved = 0
        '''need to know if the team we are evaluating has the next move or not'''
        next_to_move = any([turn % 2 == 0 and color == TileEnum.WHITE_PIECE,(not turn % 2 == 0) and color == TileEnum.BLACK_PIECE])
        for direction in [(0,-1),(-1,0),(0,1),(1,0)]:
            (row,col) = tuple([loc + dir for loc, dir in zip(piece,direction)])
            if all([x >= self._board_start and x <= self._board_end for x in (row,col)]):
                if self._board[row][col] == self.get_opposite_color(color):
                    '''enemy adjacent to this piece, check other side of enemy'''
                    (row,col) = tuple([loc + dir for loc, dir in zip((row,col),direction)])
                    if all([x >= self._board_start and x <= self._board_end for x in (row,col)]):
                        if self._board[row][col] == TileEnum.EMPTY_TILE:
                            '''this piece is making an active threat'''
                            threats_made +=1


        sides = [[(0,-1),(0,1)],[(-1,0),(1,0)]]
        for side in sides:
            adjacent = []
            for direction in side:
                coord = tuple([loc + dir for loc, dir in zip(piece,direction)])
                if all([x >= self._board_start and x <= self._board_end for x in coord]):
                    adjacent.append(self._board[coord[0]][coord[1]])
            if all([TileEnum.EMPTY_TILE in adjacent, self.get_opposite_color(color) in adjacent]):
                '''this piece has an enemy on one side and an empty tile on the other
                and is therefore recieving an active threat'''
                threats_recieved += 1



        if threats_recieved > 0 and next_to_move:
            '''if next to move can likely escape one threat'''
            threats_recieved -= 1
        elif threats_made > 0 and not next_to_move:
            '''if enemy next to move likely one threat is impotent'''
            threats_made -= 1

        '''score based on balance of active threats'''
        return 15 * (threats_made-(threats_recieved))



    def rank_piece_exposure(self, piece, color):
        """
        Score piece depending on how exposed it is (i.e. if it is not
        protected by a friendly piece or the edge of the board on it sides
        or top and bottom)
        :param piece the location of the piece we are evaluating
        :param color the team whose exposure we are evaluating
        :return: score depending on the exposure of the piece
        """
        score = 0
        sides = [[(0,-1),(0,1)],[(-1,0),(1,0)]]
        for side in sides:
            adjacent = []
            for direction in side:
                coord = tuple([loc + dir for loc, dir in zip(piece,direction)])
                if all([x >= self._board_start and x <= self._board_end for x in coord]):
                    adjacent.append(self._board[coord[0]][coord[1]])
            if not color in adjacent:
                '''piece is exposed on a side'''
                score += 1
        '''being exposed is a disadvantage, should keep friendly pieces connected most
        of the time'''
        return 0 * score


    def rank_piece_loc(self, piece):
        """
        Score piece depending on how close to the board centre it is
        :param piece the location of the piece we are evaluating
        :return: score depending on the centrality of the piece
        """
        from_centre = max([abs(piece[0]-BOARD_CENTRE), abs(piece[1]-BOARD_CENTRE)])
        if from_centre == 0.5:
            '''in centre'''
            return 200
        if from_centre == 1.5:
            '''one out'''
            return 180
        if from_centre == 2.5:
            '''two out'''
            return 160
        if from_centre == 3.5:
            '''on edge'''
            return 140




    def rank_piece_mobility(self, piece):
        """
        Score piece depending on how many moves it has available
        :param piece the location of the piece we are evaluating
        :return: score depending on the mobility of the piece
        """
        score = 0
        for direction in [(0,-1),(-1,0),(0,1),(1,0)]: #left,right,up,down
            adjacent = tuple([loc + dir for loc, dir in zip(piece,direction)])
            if self.square_viable(adjacent, None):
                score += 1
            else:
                adjacent = tuple([loc + dir for loc, dir in zip(adjacent,direction)])
                if self.square_viable(adjacent, None):
                    score += 1
        return 3 * score



    def ideal_pieces(self,color,turn):
        """
        :param turns current turn the game is at
        :param color the team who we are considering
        :return: the maximum number of pieces that team could have
        at this turn in the placing phase
        """
        if color == TileEnum.WHITE_PIECE:
            return (math.ceil((turn)/2))
        else:
            return (math.ceil((turn-1)/2))

    def get_opposite_color(self, color):
        """
        Invert the color enum (e.g. white->black)
        :param color the team who we are considering
        :return: the opposite team
        """
        if color == TileEnum.WHITE_PIECE:
            return TileEnum.BLACK_PIECE
        elif color == TileEnum.BLACK_PIECE:
            return TileEnum.WHITE_PIECE

    def print_board(self):
        """
        Method used for testing.
        Prints the internal representation of the board
        """
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
