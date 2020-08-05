# MCTS
from __future__ import division

import chess
# import chess.engine
# import chess.svg
# import chess.pgn
import time
import datetime
import random
import ast
from copy import deepcopy
from anytree import NodeMixin, RenderTree


class MCTSNode(NodeMixin):

    def __init__(self, state, wins, sims, key, parent=None, children=None, weight=None):
        # Takes an instance of a Board and optionally some keyword
        # arguments.  Initializes the list of game states and the
        # statistics tables.
        # pass
        super(MCTSNode, self).__init__()
        self.state = state
        # self.wins = kwargs.get('wins', 0)
        # self.sims = kwargs.get('sims', 0)
        self.wins = wins
        self.sims = sims
        self.key = key
        self.termnode = False
        self.termresult = False
        # self.score = self.wins / self.sims
        self.parent = parent
        if children:
            self.children = children
        self.weight = weight if parent is not None else None
        # self.name = weight or 'Root'
        # self.name = (str(self.wins) + '/' + str(self.sims) + "\n\n" +
        #              str(weight or 'Root') + "\n\n" + 'Depth: ' + str(self.depth))
        # self.depth = 0
        # self.is_leaf = True

    @property
    def score(self):
        # check if denominator is 0, return 0 if it is
        return self.wins / self.sims if self.sims else 0

    @property
    def name(self):
        # check if denominator is 0, return 0 if it is
        return (str(self.wins) + '/' + str(self.sims) + "\n\n" +
                str(self.weight or 'Root') + "\n\n" + 'Depth: ' + str(self.depth))

    # @property
    # def wins(self):
    #     return self.__wins

    # @wins.setter
    # def wins(self, value):
    #     self.wins = value

    # @sims.setter
    # def sims(self, value):
    #     self.sims = value

# get is_leaf
# get move_list
# get random_legal_move
