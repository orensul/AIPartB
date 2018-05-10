import copy
import math
from heapq import heappush, heappop

INFINITY = 100000
NEG_INFINITY = -100000
class Node:
    """
    This class of Node contains the information of node in the search tree.
    each node contains board_state, his parent, successors.
    """
    def __init__(self, board_state, color, depth, turn, action):

        # current state of the board this node represents
        self._board = board_state
        # collection of successor nodes
        self._successors = []
        # depth of the node in the tree, to know stop expanding because of cut-off
        self._depth = depth
        self._color = color
        self._turn = turn
        self._action = action


    def __lt__(self, other):
        return False

    def get_successors(self):
        return self._successors

    def get_action(self):
        return self._action

    def get_eval(self, color):
        return self._board.evaluation(color,self._turn)



    def expand_successors(self, eval_color):
        self._board.check_shrink_board(self._turn)
        actions = self._board.get_actions(self._turn,self._color)
        #print(actions)
        if len(actions) > 0:
            for action in actions:
                # create copy of this node's board
                new_board = copy.deepcopy(self._board)
                # update the copy with the action
                new_board.take_action(action, self._color)
                new_board.check_update_phase(self._turn)
                # update successors with the new board state
                child = Node(new_board, new_board.get_opposite_color(self._color), self._depth + 1, self._turn + 1, action)
                heappush(self._successors,(INFINITY,child))
            #print([(key[0],key[1].get_action()) for key in self._successors.queue])





    def min_max_value(self,cutoff_depth, eval_color,a,b):
        alpha = a
        beta = b
        if self._depth >= cutoff_depth:
            return self.get_eval(eval_color)
        else:
            successors_update = []
            if self._successors == []:
                 self.expand_successors(self._color)
                 if self._successors == []:
                     return (self.get_eval(eval_color))

            if self._color == eval_color:
                expanded_count = 0

                if cutoff_depth == 1:
                    '''always check all nodes on first interation'''
                    late_move_reduction_cutoff = len(self._successors)
                else:
                    late_move_reduction_cutoff = math.ceil(len(self._successors)/(1.5*(cutoff_depth - self._depth)))

                while not self._successors == []:
                    child = heappop(self._successors)[1]
                    score = child.min_max_value(cutoff_depth, eval_color, alpha, beta)
                    heappush(successors_update,(-score,child))

                    if score >= beta:
                        while not self._successors == []:
                            heappush(successors_update,(INFINITY,heappop(self._successors)[1]))
                        self._successors = successors_update
                        return beta

                    if score > alpha:
                        alpha = score

                    expanded_count +=1
                    if expanded_count > late_move_reduction_cutoff:
                        while not self._successors == []:
                            heappush(successors_update,(INFINITY,heappop(self._successors)[1]))
                        break
                self._successors = successors_update
                return alpha
            else:
                expanded_count = 0
                late_move_reduction_cutoff = math.ceil(len(self._successors)/(1.5*(cutoff_depth - self._depth)))
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
