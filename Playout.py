# Playout Controller

import chess
import chess.engine
import chess.svg
import time
import datetime
import streamlit as st
import cairosvg  # svg to png to animate board

from MCTS import MCTS
from MCTS_EPT import MCTSEPT
from PIL import Image


class Playout(object):

    def __init__(self, board, games, depth, algo_obj):
        self.board_state = board
        self.num_games = games
        self.search_depth = depth
        self.algo_obj = algo_obj
        globals()['boardholder'] = st.empty()
        self.animate_board()  # render starting board position

    def animate_board(self):
        board_svg = chess.svg.board(board=self.board_state)
        cairosvg.svg2png(board_svg, write_to="board.png")
        boardimg = Image.open('board.png')
        # time.sleep(0.5)
        globals()['boardholder'].image(boardimg)

    def run_algo_playout(self):
        try:
            while(1):
                # initialize root node with children at depth 1
                root_node = self.algo_obj.algo_init()
                if self.board_state.turn:
                    player = True
                else:
                    player = False
                start_time = datetime.datetime.utcnow()  # current time
                # run simulation until allowed time is reached
                while datetime.datetime.utcnow() - start_time < self.algo_obj.calc_time:
                    end_sim = self.algo_obj.algo(root_node, player)
                    if end_sim:
                        break
                best_move, _, _, _, _, _ = self.algo_obj.algo_render()
                self.board_state.push_san(best_move)
                self.animate_board()

                # print(datetime.datetime.utcnow())
                opponent_engine = chess.engine.SimpleEngine.popen_uci(
                    "stockfish.exe")
                info = opponent_engine.analyse(
                    self.board_state, chess.engine.Limit(depth=self.search_depth))
                # print(datetime.datetime.utcnow())
                self.board_state.push(info["pv"][0])
                opponent_engine.quit()
                time.sleep(1)
                self.animate_board()
        except:
            opponent_engine.quit()
