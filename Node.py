import copy
import math
from heapq import heappush, heappop

INFINITY = 100000
NEG_INFINITY = -100000
UNEXPANDED_NODE_QUEUE_PRIORITY = 0
class Node:
    """
    This class of Node contains the information of node in the search tree.
    each node contains board_state, his parent, successors.
    """
    def __init__(self, board_state, color, depth, turn, action, alpha, beta):

        # current state of the board this node represents
        self._board = board_state
        # collection of successor nodes
        self._successors = []
        # depth of the node in the tree, to know stop expanding because of cut-off
        self._depth = depth
        self._color = color
        self._turn = turn
        self._action = action
        self._alpha = alpha
        self._beta = beta

    def __lt__(self, other):
        return False

    def get_successors(self):
        return self._successors

    def get_action(self):
        return self._action

    def set_alpha_beta(self, alpha, beta):
        self._alpha = alpha
        self._beta = beta


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
                child = Node(new_board, new_board.get_opposite_color(self._color), self._depth + 1, self._turn + 1, action, self._alpha, self._beta)
                heappush(self._successors,(UNEXPANDED_NODE_QUEUE_PRIORITY,child))
            #print([(key[0],key[1].get_action()) for key in self._successors.queue])





    def min_max_value(self,cutoff_depth, eval_color):
        if self._depth >= cutoff_depth:
            '''print(eval_color)
            print(self._turn)
            print(self.get_eval(eval_color))
            self._board.print_board()'''
            return self.get_eval(eval_color)
        else:
            successors_update = []

            if self._successors == []:
                 self.expand_successors(self._color)
                 if self._successors == []:
                     return (self.get_eval(eval_color))

            if self._color == eval_color:
                expanded_count = 0
                late_move_reduction_cutoff = math.floor(len(self._successors)/((cutoff_depth - self._depth)))
                while not self._successors == []:
                    child = heappop(self._successors)[1]
                    score = child.min_max_value(cutoff_depth, eval_color)


                    child.set_alpha_beta(self._alpha,self._beta)
                    #print(-score,child.get_action())
                    heappush(successors_update,(-score,child))

                    if score >= self._beta:
                        while not self._successors == []:
                            heappush(successors_update,heappop(self._successors))
                        self._successors = successors_update
                        return self._beta

                    if score > self._alpha:
                        self._alpha = score

                    expanded_count +=1
                    if expanded_count >= late_move_reduction_cutoff:
                        while not self._successors == []:
                            heappush(successors_update,heappop(self._successors))
                        break
                self._successors = successors_update
                return self._alpha

            else:
                expanded_count = 0
                late_move_reduction_cutoff = math.floor(len(self._successors)/((cutoff_depth - self._depth)))
                while not self._successors == []:
                    child = heappop(self._successors)[1]
                    score = child.min_max_value(cutoff_depth, eval_color)
                    child.set_alpha_beta(self._alpha,self._beta)
                    #print(-score,child.get_action())
                    heappush(successors_update,(score,child))

                    if score <= self._alpha:
                        while not self._successors == []:
                            heappush(successors_update,heappop(self._successors))
                        self._successors = successors_update
                        return self._alpha

                    if score < self._beta:
                        self._beta = score

                    expanded_count +=1
                    if expanded_count >= late_move_reduction_cutoff:
                        while not self._successors == []:
                            heappush(successors_update,heappop(self._successors))
                        break

                self._successors = successors_update
                return self._beta
