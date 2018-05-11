
from BoardState import BoardState
from TileEnum import TileEnum
from Node import Node
import copy
import time
import math
from heapq import heappush, heappop
"""
Player class controller class for an adversarial search AI designed to compete against
other similar programs in a game of 'Watch Your Back' through the referee.py class. The overall
program plays the game making decisions using an alpha-beta pruning minimax algorithm with heuristic
alterations.
The class is mainly a facade providing access to the actual logical functionality defined within
the BoardState (internal board representation) and Node (minimax information) classes. The Player class
also measures and tracks time to support staying within the project constraints of 120 sec total decision
time per player per game.
@ authors: Tasrael,  Last updated May 2018
"""

INFINITY = 100000
NEG_INFINITY = -100000
'''in sec accounting for other player'''
MAX_GAME_TIME = 120
'''estimate for maximum moves a this player should make in the game to win.'''
INITIAL_TARGET_WIN_TURN = 180
'''~ number of actions available for players first move'''
GAME_INITIAL_BRANCHING_FACTOR = 46

class Player:
    def __init__(self, colour):
        """
        called by the referee once at the beginning of the game to initialise.
        Here we initialise the internal state of the board and set the team colour for this player.
        :param colour:  string representing the piece colour this class will control for this game.
        can be 'white' or 'black'
        """

        '''blank 8x8 board with corners'''
        self._board = BoardState()
        '''Using the TileEnum instead of the string for color allows us to avoid switching in BoardState Class'''
        if(colour == 'white'):
            self._color = TileEnum.WHITE_PIECE
            self._opponent_color = TileEnum.BLACK_PIECE
        elif(colour == 'black'):
            self._color = TileEnum.BLACK_PIECE
            self._opponent_color = TileEnum.WHITE_PIECE

        '''Take a measurement of when the game started for later allocations of time for decisions'''
        self._game_start_time = time.time()
        '''By predicting how many moves we will take to win we can allow for better allocation of time
        to each decision'''
        self._target_win_turn = INITIAL_TARGET_WIN_TURN
        self._time_remaining = MAX_GAME_TIME
        self._max_time_for_decision = MAX_GAME_TIME/self._target_win_turn
        '''estimate of games average branching factor. Allows prediction of how long
            the next alpha-beta depth iteration will take'''
        self._turn_branching_factor = GAME_INITIAL_BRANCHING_FACTOR

        '''Save the last action taken in the move phase to allow for avoiding becoming
        trapped in length 2 loops of moves'''
        self._last_move = None
        self._move_loop_count = 0

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
        action_start_time = time.time()
        if not self._board.get_is_place_phase():
            self._target_win_turn = turns + (INITIAL_TARGET_WIN_TURN - turns) * (self._board.get_remaining_pieces(self._opponent_color)/self._board.get_remaining_pieces(self._color))
            #print(self._target_win_turn)

        '''Determine from how much time has passed of the total allowed and the number of likely moves
        the player has left to make, how much time we should allocate to the next decision.
        assumes the other player is working in the time constraints as well'''
        if self._target_win_turn - turns <= 0:
            '''ocasionally if game is long enough this occurs and produces errors
            default to 1 second per turn'''
            self._max_time_for_decision = 1
        else:
            self._max_time_for_decision = (self._time_remaining)/((self._target_win_turn-turns))
        if self._board.get_is_place_phase():
            '''allow 5x time in place phase'''
            self._max_time_for_decision *= 5
        '''Check if the internal board should be shrunk on this turn'''
        self._board.check_shrink_board(turns)

        action = self.minimax_decision(turns,time.time())
        self._time_remaining -= (time.time() - action_start_time)
        if isinstance(action[0], tuple):
            self._last_move = action
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
        root = Node(copy.deepcopy(self._board), self._color, 0, turns, None)
        last_iteration_time = 0
        best_actions = []
        #print('Time we are allowing for this decision: ' + str(self._max_time_for_decision))
        for depth in range(1,6):
            '''Estimate How long next iteration will take from the last and only undertake it if
            there is time. /2 added by experimentation'''
            if (self._max_time_for_decision - (time.time()-start_time)) < (math.sqrt(self._turn_branching_factor)/2) * last_iteration_time:
                pass
            else:
                begin = time.time()
                root_alpha = root.min_max_value(depth, self._color,NEG_INFINITY, INFINITY)
                last_iteration_time = time.time() - begin
                root_successors = copy.deepcopy(root.get_successors())
                self._turn_branching_factor = len(root_successors)
                #print(math.sqrt(self._turn_branching_factor))
                best_actions.append(heappop(root_successors)[1].get_action())
                best_action = best_actions[len(best_actions)-1]
                #print('DEPTH: ' + str(depth))
                #print('ALPHA: ' + str(root_alpha))
                #print('ACTION: ' + str(best_action))
                #print('Time spent on decision so far: ' +str(time.time()-start_time))

                '''If we have looked to depth 3 and all best_action returns were the same
                then don't bother with further iterations'''
                if len(best_actions) > 2 and all(elem == best_action for elem in best_actions):
                    return best_action

        if isinstance(best_action, tuple):
            if self.reverse_move(best_action) == self._last_move:
                #print('reversed last move')
                self._move_loop_count += 1
                if self._move_loop_count > 2:
                    '''We are probably in a loop, choose next action in queue'''
                    #print('Hit a move loop.............................................................................')
                    best_action = heappop(root_successors)[1].get_action()
                    self._move_loop_count = 0
            else:
                self._move_loop_count = 0
        return best_action




    def switch_row_column(self, action):
        """
        internal board uses (row,column) format for peice coordinates,
        referee uses (column,row). Simple method to convert between the two
        :param action: representation of the opponent’s recent action tuple for placing, tuple of tuples for moving
        :return:the action of the player in the reversed format
        """
        if action == None:
            return None
        if isinstance(action[0], tuple):
            return (action[0][::-1],action[1][::-1])
        else:
            return action[::-1]

    def reverse_move(self, move):
        return (move[1],move[0])
