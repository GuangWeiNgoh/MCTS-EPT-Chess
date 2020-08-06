# Playout Controller

import chess
import chess.engine
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
