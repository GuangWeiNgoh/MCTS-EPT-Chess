# Playout Controller

import chess
import chess.engine
import time
import datetime

from MCTS import MCTS
from MCTS_EPT import MCTSEPT

# take in board, games, depth, algo?, mcts/mcts-ept object


class Playout(object):

    def __init__(self, board, games, depth, algo_obj):
        self.board_state = board
        self.num_games = games
        self.search_depth = depth
        self.algo_obj = algo_obj
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish.exe")

    def run_algo_playout(self):
        # initialize root node with children at depth 1
        root_node = self.algo_obj.mcts_init()
        if self.board_state.turn:
            player = True
        else:
            player = False
        print(self.algo_obj.calc_time)
        print(self.algo_obj.C)
        start_time = datetime.datetime.utcnow()  # current time
        # run simulation until allowed time is reached
        while datetime.datetime.utcnow() - start_time < self.algo_obj.calc_time:
            end_sim = self.algo_obj.mcts(root_node, player)
            if end_sim:
                break
        best_move, _, _, _, _, _ = self.algo_obj.mcts_render()
