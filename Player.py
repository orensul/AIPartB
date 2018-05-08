
from BoardState import BoardState
from TileEnum import TileEnum
from Node import Node
import copy
import time
import math

'''
Player class controller class for an adversarial search AI designed to compete against
other similar programs in a game of 'Watch Your Back' through the referee.py class. The overall
program plays the game making decisions using an alpha-beta pruning minimax algorithm with heuristic
alterations.
The class is mainly a facade providing access to the actual logical functionality defined within
the BoardState (internal board representation) and Node (minimax information) classes. The Player class
also measures and tracks time to support staying within the project constraints of 120 sec total decision
time per player per game.
'''

INFINITY = 100000
NEG_INFINITY = -100000
'''in sec accounting for other player'''
MAX_GAME_TIME = 240
'''estimate for maximum moves a this player should make in the game. ~12 in placing ~100 max in moving'''
MAX_MOVES = 112
'''estimate of games average branching factor. Allows prediction of how long the next alpha-beta depth iteration will take'''
GAME_AVERAGE_BRANCHING_FACTOR = 40

class Player:
    def __init__(self, colour):
        """
        called by the referee once at the beginning of the game to initialise.
        Here we initialise the internal state of the board and set the team colour for this player.
        :param colour:  string representing the piece colour this class will control for this game.
        can be 'white' or 'black'
        """
        #random.seed(9002)
        '''blank 8x8 board with corners'''
        self._board = BoardState()
        '''Using the TileEnum instead of the string for color allows us to avoid switching in BoardState Class'''
        if(colour == 'white'):
            self._color = TileEnum.WHITE_PIECE
            self._opponent_color = TileEnum.BLACK_PIECE
        elif(colour == 'black'):
            self._color = TileEnum.BLACK_PIECE
            self._opponent_color = TileEnum.WHITE_PIECE

        self._game_start_time = time.time()
        self._max_time_for_decision = MAX_GAME_TIME/MAX_MOVES

    def update(self, action):
        """
        This method is called by the referee to inform the player about the opponent’s
        most recent move, maintains the nternal board configuration by applying the
        opponents action to the BoardState.
        :param action: representation of the opponent’s recent action tuple for placing, tuple of tuples for moving
        :return:
        """
        if not action == None:
            action = self.switch_row_column(action)
            self._board.take_action(action, self._opponent_color)



    def action(self, turns):
        """
        Called by the referee to request an action from the player.
        :param turns: turns is an integer representing the number of turns that have
        taken place since the start of the current game phase, counts from 0-23 in place phase,
        then 0-... in the moving phase.
        :return: the next action of the player in a format of:
                 (x,y) -  placing a piece on square (x,y)
                 ((a,b),(c,d)) -  moving a piece from square (a,b) to square (c,d)
        """

        '''Determine from how much time has passed of the total allowed and the number of likely moves
        the player has left to make, how much time we should allocate to the next decision.'''
        self._max_time_for_decision = (MAX_GAME_TIME - (time.time() - self._game_start_time))/((MAX_MOVES-((turns+1)/2)))   #/2 to account for only this players game time
        '''Check if the internal board should be shrunk on this turn'''
        self._board.check_shrink_board(turns)

        action = self.minimax_decision(turns,time.time())

        if not action == None:
            '''update board with action and return action in (col,row) format the referee prefers'''
            self._board.take_action(action, self._color)
            '''update internal board representation to the move phase if appropriate'''
            self._board.check_update_phase(turns)
            return self.switch_row_column(action)
        else:
            self._board.check_update_phase(turns)
            return None


    def minimax_decision(self, turns, start_time):
        """
        Performs an iterative deepening version of alpha-beta minimax algorithm
        before the start of each iteration we predict (from the time complexity of
        alpha-beta and our estimated branching factor) how long the next iteration
        will take. If we have not allowed the time to perform this for this move
        the result of the last depth iteration is returned

        :param turs: turns is an integer representing the number of turns that have
        taken place since the start of the current game phase, counts from 0-23 in place phase,
        then 0-... in the moving phase.
        :param start_time: time at which this method was first called
        :return: the next action of the player in a format of:
                 (x,y) -  placing a piece on square (x,y)
                 ((a,b),(c,d)) -  moving a piece from square (a,b) to square (c,d)
        """
        root = Node(copy.deepcopy(self._board), self._color, 0, turns, None, NEG_INFINITY, INFINITY)
        last_iteration_time = 0
        for depth in range(1,8):
            #print(self._max_time_for_decision)

            if (self._max_time_for_decision - (time.time()-start_time)) < math.sqrt(GAME_AVERAGE_BRANCHING_FACTOR) * last_iteration_time:
                pass
            else:
                begin = time.time()
                #print(time.time()-start_time)
                (alpha,best_action) = root.min_max_value(depth, self._color)
                last_iteration_time = time.time() - begin
                #print('DEPTH: ' + str(depth))
                #print('ALPHA: ' + str(alpha))
                #print('ACTION: ' + str(best_action))
                root.set_alpha_beta(NEG_INFINITY,INFINITY)
                #print('Time spent on decision so far: ' +str(time.time()-start_time))
        return best_action




    def switch_row_column(self, action):
        """
        internal board uses (row,column) format for peice coordinates,
        referee uses (column,row). Simple method to convert between the two
        :param action: representation of the opponent’s recent action tuple for placing, tuple of tuples for moving
        :return:the action of the player in the reversed format
        """
        if isinstance(action[0], tuple):
            return (action[0][::-1],action[1][::-1])
        else:
            return action[::-1]
