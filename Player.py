from BoardState import BoardState

SUM_TURNS_PLACE_PHASE = 24

class Player:
    def __init__(self, colour):
        """
        called by the referee once at the beginning of the game to initialise.
        Here we will set the state of the board and more states we will want to maintain during the game.
        :param colour:  string representing the piece colour your program will control for this game.
        can be 'white' or 'black
        """
        self._color = colour
        self._opponent_color = self.get_opponent_color()
        self._board = BoardState()
        self._is_place_phase = True

    def get_opponent_color(self):
        if self._color == 'white':
            return 'black'
        return 'white'

    def action(self, turns):
        """
        This method is called by the referee to request an action by your player.
        :param turns: turns is an integer representing the number of turns that have
        taken place since the start of the current game phase
        :return: the next action of the player in a format of:
                 (x,y) -  placing a piece on square (x,y)
                 ((a,b),(c,d)) -  moving a piece from square (a,b) to square (c,d)
        """
        if self._is_place_phase:
            coord = self._board.get_empty_tiles(self._color)[0]
            row = coord[0]
            col = coord[1]
            self._board.place_piece(self._color, (row, col))
            return_val = col, row
        else:
            coord = self._board.get_available_moves(self._color)[0]
            source = coord[0]
            dest = coord[1]

            source_row = source[0]
            source_col = source[1]

            dest_row = dest[0]
            dest_col = dest[1]

            self._board.place_piece(self._color, (dest_row, dest_col))
            return_val = (source_col, source_row), (dest_col, dest_row)

        if turns == SUM_TURNS_PLACE_PHASE - 1:
            self._is_place_phase = False

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


