import copy
import math
from heapq import heappush, heappop

INFINITY = 100000
NEG_INFINITY = -100000

"""
Node class is responsible of the performance of the minimax-alpha-beta pruning algorithm
for the player class. Multiple instances of this class make a tree with re-orderable succession
based on the results of each iteraion of the minimax algorithm
@ authors: Tasrael,  Last updated May 2018
"""
class Node:
    """
    This class of Node contains the information of node in the search tree.
    each node contains board_state, his parent, successors.
    """
    def __init__(self, board_state, color, depth, turn, action):

        ''' current state of the board this node represents'''
        self._board = board_state
        '''collection of successor nodes'''
        self._successors = []
        ''' depth of the node in the current tree, to know stop expanding because of cut-off'''
        self._depth = depth
        ''' the color taking action on the move this node represents'''
        self._color = color
        '''the turn number of the game this node represents'''
        self._turn = turn
        '''The action that produced this node from the previous game turn'''
        self._action = action


    def __lt__(self, other):
        """
        We specify a less than comparitor for this class to allow it to be sorted (along with a key)
        in a heapq structure. Because of how the minimax is written if the key value is the same
        as an object already in the heap we automatically place the new object bellow it in the heap
        """
        return False

    def get_successors(self):
        """
        :return:the heapq containing the successor nodes of this node
        """
        return self._successors

    def get_action(self):
        """
        :return:the action on this node's parent's BoardState that produced this node
        """
        return self._action

    def get_eval(self, color):
        """
        :param: color the team who we are evaluating the board for
        :return:the numerical utility rating of this node's board state object
        """
        return self._board.evaluation(color,self._turn)



    def expand_successors(self):
        """
        Produce successor nodes to this object by copying this object's BoardState and
        applying available actions to it
        :return:the numerical utility rating of this node's board state object
        """
        self._board.check_shrink_board(self._turn)
        actions = self._board.get_actions(self._turn,self._color)
        if len(actions) > 0:
            for action in actions:
                ''' create copy of this node's board'''
                new_board = copy.deepcopy(self._board)
                '''update the copy with the action'''
                new_board.take_action(action, self._color)
                new_board.check_update_phase(self._turn)
                ''' update successors with the new board state
                pushed with INFINITY priority (i.e. every evaluation
                function is higher than an unexplored node)'''
                child = Node(new_board, new_board.get_opposite_color(self._color), self._depth + 1, self._turn + 1, action)
                heappush(self._successors,(INFINITY,child))






    def min_max_value(self,cutoff_depth, eval_color,a,b):
        """
        Perform the alpha-beta minimax algorithm on a tree made of these Node
        objects to the specified depth. Expanding successors if not already done so.
        Successors are sorted based on the result in anticipation of a higher depth iteration.
        :param cutoff_depth the depth of the interation
        :param eval_color the team who we evaluate the nodes w.r.t
        :param a,b the initial values for alpha beta this node begins the algorithm with
        :return:the minimum/maximum eval function at cutoff_depth depending on if the Node
         is minimizing or maximizing
        """
        alpha = a
        beta = b
        if self._depth >= cutoff_depth:
            return self.get_eval(eval_color)
        else:
            '''If successors not expanded, do so. If no possible actions/successors
            simply return this nodes evaluation function rather than it's children'''
            successors_update = []
            if self._successors == []:
                 self.expand_successors()
                 if self._successors == []:
                     return (self.get_eval(eval_color))

            if self._color == eval_color:
                '''maximizing node'''
                expanded_count = 0
                if cutoff_depth == 1:
                    '''always check all nodes on first interation'''
                    late_move_reduction_cutoff = len(self._successors)
                else:
                    '''otherwise if we are at a deeper iteration, pre-emptively don't consider
                    some nodes at the end of the successor order produced by the last iteration
                    /2 determined by experimentation from tradeoff of speed and better moves'''
                    late_move_reduction_cutoff = math.ceil(len(self._successors)/(2*(cutoff_depth - self._depth)))

                while not self._successors == []:
                    child = heappop(self._successors)[1]
                    score = child.min_max_value(cutoff_depth, eval_color, alpha, beta)
                    heappush(successors_update,(-score,child))
                    if score >= beta:
                        while not self._successors == []:
                            '''put unexplored nodes back into the successors_update with the worst
                            priority possible'''
                            heappush(successors_update,(INFINITY,heappop(self._successors)[1]))
                        '''update the successor order based on this iteration results'''
                        self._successors = successors_update
                        return beta

                    if score > alpha:
                        alpha = score

                    expanded_count +=1
                    if expanded_count > late_move_reduction_cutoff:
                        '''put unexplored nodes back into the successors_update with the worst
                        priority possible'''
                        while not self._successors == []:
                            heappush(successors_update,(INFINITY,heappop(self._successors)[1]))
                        break
                '''update the successor order based on this iteration results'''
                self._successors = successors_update
                return alpha
            else:
                expanded_count = 0
                late_move_reduction_cutoff = math.ceil(len(self._successors)/(2*(cutoff_depth - self._depth)))
                while not self._successors == []:
                    child = heappop(self._successors)[1]
                    score = child.min_max_value(cutoff_depth, eval_color, alpha, beta)
                    heappush(successors_update,(score,child))
                    if score <= alpha:
                        while not self._successors == []:
                            heappush(successors_update,(INFINITY,heappop(self._successors)[1]))
                        self._successors = successors_update
                        return alpha
                    if score < beta:
                        beta = score
                    expanded_count +=1
                    if expanded_count > late_move_reduction_cutoff:

                        while not self._successors == []:
                            heappush(successors_update,(INFINITY,heappop(self._successors)[1]))
                        break

                self._successors = successors_update
                return beta
