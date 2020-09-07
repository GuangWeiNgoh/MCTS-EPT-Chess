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


class MCTSEPT3Node(NodeMixin):

    def __init__(self, state, eval, key, parent=None, children=None, weight=None):
        # Takes an instance of a Board and optionally some keyword
        # arguments.  Initializes the list of game states and the
        # statistics tables.
        # pass
        super(MCTSEPT3Node, self).__init__()
        self.state = state
        self.winsum = 0.0  # total added up win percentage
        self.sims = 0
        self.eval = eval
        self.key = key
        self.termnode = False
        self.termresult = 0.0
        self.parent = parent
        if children:
            self.children = children
        self.weight = weight if parent is not None else None

    @property
    def score(self):
        # check if denominator is 0, return 0 if it is
        return self.winsum / self.sims if self.sims else 0

    @property
    def name(self):
        # check if denominator is 0, return 0 if it is
        return (str(self.score) + "\n\n" +
                str(self.weight or 'Root') + "\n\n" + 'Depth: ' + str(self.depth))
