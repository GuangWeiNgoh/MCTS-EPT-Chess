# Playout Controller

import chess
import chess.engine
import chess.svg
import time
import datetime
import streamlit as st
import cairosvg  # svg to png to animate board
import MinimaxAlphaBetaPruning

from MCTS import MCTS
from MCTS_EPT import MCTSEPT
from PIL import Image


class Playout(object):

    def __init__(self, board, games, depth, algo_obj):
        self.starting_board_state = board
        self.board_state = board
        self.num_games = games
        self.search_depth = depth
        self.algo_obj = algo_obj
        globals()['boardholder'] = st.empty()
        globals()['scoreboard'] = st.empty()
        globals()['scoreboard'].text(
            'Player ' + str(0) + ' - ' + str(0) + ' Opponent')
        self.animate_board(None)  # render starting board position
        if board.turn:
            self.original_player = True
        else:
            self.original_player = False
        self.win_count = 0
        self.lose_count = 0

    def animate_board(self, move):
        board_svg = chess.svg.board(
            board=self.board_state, lastmove=move)
        cairosvg.svg2png(board_svg, write_to="board.png")
        boardimg = Image.open('board.png')
        # time.sleep(0.5)
        globals()['boardholder'].image(boardimg)

    def run_algo_playout(self):
        # initialize root node with children at depth 1
        # update algo board state with current board
        self.algo_obj.starting_board_state = self.board_state.copy()
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

        # parse from san to uci for last move on svg
        best_move_uci = self.board_state.parse_san(best_move)
        self.board_state.push_san(best_move)
        # try:
        #     self.board_state.push_san(best_move_uci)
        # except:
        #     print(self.board_state.fen())
        #     print(list(self.board_state.legal_moves))
        self.animate_board(best_move_uci)

        if self.board_state.is_game_over():
            if self.board_state.is_checkmate():  # assign winner only if checkmate
                if self.board_state.turn == self.original_player:
                    self.lose_count += 1
                else:
                    self.win_count += 1
            return False  # stop game and reset

        # # print(datetime.datetime.utcnow())
        # opponent_engine = chess.engine.SimpleEngine.popen_uci(
        #     "stockfish.exe")
        # info = opponent_engine.analyse(
        #     self.board_state, chess.engine.Limit(depth=self.search_depth))
        # # info = opponent_engine.analyse(
        # #     self.board_state, chess.engine.Limit(time=0.005))
        # # print(datetime.datetime.utcnow())
        # opponent_best_move = info["pv"][0]
        # opponent_engine.quit()

        opponent_best_move = MinimaxAlphaBetaPruning.calculateMove(
            self.board_state)

        self.board_state.push(opponent_best_move)
        # opponent_engine.quit()
        time.sleep(0.5)
        self.animate_board(opponent_best_move)

        if self.board_state.is_game_over():
            if self.board_state.is_checkmate():  # assign winner only if checkmate
                if self.board_state.turn == self.original_player:
                    self.lose_count += 1
                else:
                    self.win_count += 1
            return False  # stop game and reset

        return True  # continue game

    def iterate(self):
        for i in range(self.num_games):
            result = True
            self.board_state = self.starting_board_state.copy()
            while(result):
                result = self.run_algo_playout()
                globals()['scoreboard'].text(
                    'Player ' + str(self.win_count) + ' - ' + str(self.lose_count) + ' Opponent')
                print('Wins: ' + str(self.win_count))
                print('Loses: ' + str(self.lose_count))
                print('\n')
