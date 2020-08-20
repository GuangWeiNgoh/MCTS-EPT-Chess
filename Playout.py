# Playout Controller

import chess
import chess.engine
import chess.svg
import time
import datetime
import streamlit as st
import cairosvg  # svg to png to animate board
import MinimaxAlphaBetaPruning
import random  # random move if opponent engine best move None
import base64  # svg

from MCTS import MCTS
from MCTS_EPT import MCTSEPT
from PIL import Image


class Playout(object):

    def __init__(self, board, games, opponent, depth, algo_obj):
        self.starting_board_state = board
        self.board_state = board
        self.num_games = games
        self.opponent = opponent
        self.search_depth = depth
        self.algo_obj = algo_obj  # instance of mcts/mcts-ept
        self.opponent_engine = chess.engine.SimpleEngine.popen_uci(
            "stockfish.exe")
        if board.turn:
            self.original_player = True
        else:
            self.original_player = False

        globals()['num_moves_played'] = st.empty()
        self.moves_played = 0
        globals()['num_moves_played'].text(
            'Moves played: ' + str(self.moves_played))

        globals()['cp_score'] = st.empty()
        self.update_cp()

        globals()['boardholder'] = st.empty()
        self.animate_board(None)  # render starting board position

        globals()['scoreboard'] = st.empty()
        globals()['scoreboard'].text(
            'Wins: ' + str(0) + '\nLosses: ' + str(0) + '\nDraws: ' + str(0))

        self.win_count = 0
        self.lose_count = 0
        self.draw_count = 0
        self.last_game_status = ''  # stores game status of previous game

    def animate_board(self, move):  # save board state to svg then png to display
        board_svg = chess.svg.board(
            board=self.board_state, lastmove=move)

        # print(type(board_svg))
        # f = open("board.svg", "a")
        # f.write(board_svg)
        # f.close()
        # boardimg = Image.open('board.svg')

        cairosvg.svg2png(board_svg, write_to="board.png")
        boardimg = Image.open('board.png')
        globals()['boardholder'].image(boardimg, width=400)
        # globals()['boardholder'].image(board_svg, width=400)

    def update_cp(self):
        info = self.opponent_engine.analyse(
            self.board_state, chess.engine.Limit(time=0.1))
        if self.original_player:
            globals()['cp_score'].text(
                'CP: ' + info["score"].white().__str__())
        else:
            globals()['cp_score'].text(
                'CP: ' + info["score"].black().__str__())

    def stockfish_move(self):
        # print(datetime.datetime.utcnow())
        # opponent_engine = chess.engine.SimpleEngine.popen_uci(
        #     "stockfish.exe")
        info = self.opponent_engine.analyse(
            self.board_state, chess.engine.Limit(depth=self.search_depth))
        # info = opponent_engine.analyse(
        #     self.board_state, chess.engine.Limit(time=0.005))
        # print(datetime.datetime.utcnow())
        best_move = info["pv"][0]
        # opponent_engine.quit()
        return best_move

    def minimax_move(self):
        # print(datetime.datetime.utcnow())
        best_move = MinimaxAlphaBetaPruning.minimaxRoot(
            self.search_depth, self.board_state, True)
        # print(datetime.datetime.utcnow())
        return best_move

    def check_game_over(self):  # checks if game has ended, return true if ended
        game_over = False
        if self.board_state.is_game_over():
            game_over = True  # stop game and reset
            if self.board_state.is_checkmate():  # assign winner only if checkmate
                if self.board_state.turn == self.original_player:
                    self.lose_count += 1
                    self.last_game_status = 'Lost (Checkmate)'
                else:
                    self.win_count += 1
                    self.last_game_status = 'Won (Checkmate)'

            if self.board_state.is_stalemate():
                self.draw_count += 1
                self.last_game_status = 'Draw (Stalemate)'

            if self.board_state.is_insufficient_material():
                self.draw_count += 1
                self.last_game_status = 'Draw (Insufficient Material)'

            if self.board_state.is_seventyfive_moves():
                self.draw_count += 1
                self.last_game_status = 'Draw (75 Moves)'

            if self.board_state.is_fivefold_repetition():
                self.draw_count += 1
                self.last_game_status = 'Draw (Fivefold Repetition)'

        return game_over

    def run_algo_playout(self):

        # update algo board state with current board, important for restarting games
        self.algo_obj.starting_board_state = self.board_state.copy()

        # initialize root node with children at depth 1
        root_node = self.algo_obj.algo_init()

        start_time = datetime.datetime.utcnow()  # current time
        # run simulation until allowed time is reached
        while datetime.datetime.utcnow() - start_time < self.algo_obj.calc_time:
            end_sim = self.algo_obj.algo(root_node)
            if end_sim:
                break
        best_move, _, _, _, _, _ = self.algo_obj.algo_render()

        # parse from san to uci for last move on svg
        best_move_uci = self.board_state.parse_san(best_move)
        self.board_state.push_san(best_move)
        self.moves_played += 1  # update number of moves played from mcts pov
        globals()['num_moves_played'].text(
            'Moves played: ' + str(self.moves_played))
        self.animate_board(best_move_uci)
        self.update_cp()

        end_game = self.check_game_over()
        if end_game:
            return end_game

        # opponent turn
        if self.opponent == 'Stockfish 11':
            opponent_best_move = self.stockfish_move()
        else:
            opponent_best_move = self.minimax_move()
        try:
            self.board_state.push(opponent_best_move)
        except:
            # random move if opponent engine best move None
            self.board_state.push(random.choice(
                list(self.board_state.legal_moves)))
        time.sleep(0.5)  # delay to see board state after mcts
        self.animate_board(opponent_best_move)
        self.update_cp()

        end_game = self.check_game_over()
        if end_game:
            return end_game

        return end_game  # continue game is end_game == False

    def iterate(self):
        for each_game in range(self.num_games):
            game_number = each_game + 1
            end = False
            self.board_state = self.starting_board_state.copy()
            self.moves_played = 0

            while(not(end)):
                end = self.run_algo_playout()
                print('Wins: ' + str(self.win_count))
                print('Loses: ' + str(self.lose_count))
                print('\n')

            globals()['scoreboard'].text(
                'Wins: ' + str(self.win_count) + '\nLosses: ' + str(self.lose_count) + '\nDraws: ' + str(self.draw_count))
            st.text('Game ' + str(game_number) +
                    ' - ' + str(self.last_game_status) + ' - ' + str(self.moves_played) + ' Moves')
        self.opponent_engine.quit()
