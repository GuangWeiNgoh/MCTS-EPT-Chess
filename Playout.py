# Playout Controller

import chess
import chess.engine
import chess.svg
import chess.syzygy  # endgame tablebases
import time
import datetime
import streamlit as st
import cairosvg  # svg to png to animate board
import MinimaxAlphaBetaPruning
import random  # random move if opponent engine best move None
import base64  # svg
import StaticEval

from MCTS import MCTS
from MCTS_EPT import MCTSEPT
from MCTS_EPT_2_CP_Norm import MCTSEPT2
from MCTS_EPT_3_Nega import MCTSEPT3
from PIL import Image


class Playout(object):

    def __init__(self, board, games, opponent, depth, algo_obj, opponent_calc_time, opponent_ept_root_c_value, opponent_ept_c_value):
        self.starting_board_state = board
        self.board_state = board
        self.num_games = games
        self.opponent = opponent
        self.search_depth = depth
        self.algo_obj = algo_obj  # instance of mcts/mcts-ept
        self.evaluation_engine = chess.engine.SimpleEngine.popen_uci(
            "stockfish.exe")
        # if opponent == 'Stockfish 11':
        #     self.opponent_engine = chess.engine.SimpleEngine.popen_uci(
        #         "stockfish.exe")
        # self.opponent_engine = chess.engine.SimpleEngine.popen_uci(
        #     "./Engines/Acqua/acqua.exe")
        # self.opponent_engine = chess.engine.SimpleEngine.popen_uci(
        #     "./Engines/Alaric/Alaric707.exe")
        # 1200 Elo
        if opponent == 'Irina (1200 Elo)':
            self.opponent_engine = chess.engine.SimpleEngine.popen_uci(
                "./Engines/Irina/irina.exe")
        # 1800 Elo
        elif opponent == 'CDrill (1800 Elo)':
            self.opponent_engine = chess.engine.SimpleEngine.popen_uci(
                "./Engines/Cdrill/CDrill_1800_Build_4.exe")
        # 2058 Elo
        elif opponent == 'Clarabit (2058 Elo)':
            self.opponent_engine = chess.engine.SimpleEngine.popen_uci(
                "./Engines/Clarabit/clarabit_100_x32_win.exe")
        elif opponent == 'MCTS-EPT':
            self.opponent_algo = MCTSEPT(board, time=opponent_calc_time,
                                         terminal_depth=depth, C=opponent_ept_c_value, root_C=opponent_ept_root_c_value, player=False)
        elif opponent == 'MCTS-EPT (CP Normalized)':
            self.opponent_algo = MCTSEPT2(board, time=opponent_calc_time,
                                          terminal_depth=depth, C=opponent_ept_c_value, root_C=opponent_ept_root_c_value, player=False)
        elif opponent == 'MCTS-EPT (CP Normalized) w/ Implicit Minimax Backups':
            self.opponent_algo = MCTSEPT3(board, time=opponent_calc_time,
                                          terminal_depth=depth, C=opponent_ept_c_value, root_C=opponent_ept_root_c_value, player=False)

        globals()['num_moves_played'] = st.empty()
        self.moves_played = 0
        globals()['num_moves_played'].text(
            'Moves played: ' + str(self.moves_played))

        globals()['cp_score'] = st.empty()
        # self.update_cp()

        globals()['boardholder'] = st.empty()
        self.flip_board = False
        self.animate_board(None)  # render starting board position

        globals()['scoreboard'] = st.empty()
        globals()['scoreboard'].text(
            'Wins: ' + str(0) + '\nLosses: ' + str(0) + '\nDraws: ' + str(0))

        self.win_count = 0
        self.lose_count = 0
        self.draw_count = 0
        self.last_game_status = ''  # stores game status of previous game

        # *******************************************************************************************************************************

    def minimaxRoot(self, depth, board, isMaximizing):
        possibleMoves = board.legal_moves
        bestMove = -9999
        bestMoveFinal = None
        for x in possibleMoves:
            move = chess.Move.from_uci(str(x))
            board.push(move)
            value = max(bestMove, self.minimax(
                depth - 1, board, -10000, 10000, not isMaximizing))
            board.pop()
            if(value > bestMove):
                print("Best score: ", str(bestMove))
                print("Best move: ", str(bestMoveFinal))
                bestMove = value
                bestMoveFinal = move
        return bestMoveFinal

    def minimax(self, depth, board, alpha, beta, is_maximizing):
        if(depth == 0):
            # return -self.stock_eval(board)
            # return -(Playout.Playout.minimax_eval(board))
            # return -evaluation(board)
            return -StaticEval.evaluate_board(board)
        possibleMoves = board.legal_moves
        if(is_maximizing):
            bestMove = -9999
            for x in possibleMoves:
                move = chess.Move.from_uci(str(x))
                board.push(move)
                bestMove = max(bestMove, self.minimax(
                    depth - 1, board, alpha, beta, not is_maximizing))
                board.pop()
                alpha = max(alpha, bestMove)
                if beta <= alpha:
                    return bestMove
            return bestMove
        else:
            bestMove = 9999
            for x in possibleMoves:
                move = chess.Move.from_uci(str(x))
                board.push(move)
                bestMove = min(bestMove, self.minimax(
                    depth - 1, board, alpha, beta, not is_maximizing))
                board.pop()
                beta = min(beta, bestMove)
                if(beta <= alpha):
                    return bestMove
            return bestMove

    def calculateMove(self, board):
        possible_moves = board.legal_moves
        if(len(possible_moves) == 0):
            print("No more possible moves...Game Over")
            sys.exit()
        bestMove = None
        bestValue = -9999
        n = 0
        for x in possible_moves:
            move = chess.Move.from_uci(str(x))
            board.push(move)
            # boardValue = -self.stock_eval(board)
            # boardValue = -(Playout.Playout.minimax_eval(board))
            # boardValue = -evaluation(board)
            boardValue = -StaticEval.evaluate_board(board)
            board.pop()
            if(boardValue > bestValue):
                bestValue = boardValue
                bestMove = move

        return bestMove

    def stock_eval(self, board):
        # engine = chess.engine.SimpleEngine.popen_uci("stockfish.exe")
        info = self.evaluation_engine.analyse(
            board, chess.engine.Limit(depth=3))
        try:
            evaluation = int(info["score"].white().__str__())
        except:
            pov_score = info["score"].white().__str__()
            if pov_score[1] == '+':  # mate in x
                return 6382
            else:
                return -6382
        # engine.close()
        return evaluation

    # *******************************************************************************************************************************

    def animate_board(self, move):  # save board state to svg then png to display
        board_svg = chess.svg.board(
            board=self.board_state, lastmove=move, flipped=self.flip_board)

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
        info = self.evaluation_engine.analyse(
            self.board_state, chess.engine.Limit(depth=3))
        stat_eval = StaticEval.evaluate_board(self.board_state)
        if self.algo_obj.original_player:
            globals()['cp_score'].text(
                'Stockfish Eval: ' + info["score"].white().__str__() + '                 Static Eval: ' + str(stat_eval))
        else:
            globals()['cp_score'].text(
                'Stockfish Eval: ' + info["score"].black().__str__() + '                 Stat Eval: ' + str(-stat_eval))

    def stockfish_move(self):
        # print(datetime.datetime.utcnow())
        # opponent_engine = chess.engine.SimpleEngine.popen_uci(
        #     "stockfish.exe")
        info = self.evaluation_engine.analyse(
            self.board_state, chess.engine.Limit(depth=self.search_depth))
        # info = opponent_engine.analyse(
        #     self.board_state, chess.engine.Limit(time=0.005))
        # print(datetime.datetime.utcnow())
        best_move = info["pv"][0]
        # opponent_engine.quit()
        return best_move

    def engine_move(self):
        # info = self.opponent_engine.analyse(
        #     self.board_state, chess.engine.Limit(time=self.search_depth))
        # print(info)
        # best_move = info["pv"][0]
        result = self.opponent_engine.play(
            self.board_state, chess.engine.Limit(time=self.search_depth))
        # board.push(result.move)
        return result.move
        # return best_move

    def minimax_move(self):
        # print(datetime.datetime.utcnow())
        # best_move = MinimaxAlphaBetaPruning.minimaxRoot(
        #     self.search_depth, self.board_state, True)
        best_move = self.minimaxRoot(
            self.search_depth, self.board_state, True)
        # print(datetime.datetime.utcnow())
        return best_move

    # def minimax_eval(self, board):
    #     info = self.evaluation_engine.analyse(
    #         board, chess.engine.Limit(depth=3))
    #     evaluation = int(info["score"].white().__str__())
    #     return evaluation

    def check_game_over(self):  # checks if game has ended, return true if ended
        game_over = False
        if self.board_state.is_game_over():
            game_over = True  # stop game and reset
            if self.board_state.is_checkmate():  # assign winner only if checkmate
                if self.board_state.turn == self.algo_obj.original_player:
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

    def check_tablebase(self):
        game_over = False
        with chess.syzygy.open_tablebase("syzygy/3-4-5") as tablebase:
            dtz = tablebase.get_dtz(self.board_state)
            # print(tablebase.get_wdl(self.board_state))
            # print(tablebase.get_dtz(self.board_state))
            # print(tablebase.probe_wdl(board))
            # print(tablebase.probe_dtz(board))
        if dtz != None:
            print('DTZ: ' + str(dtz))
            game_over = True
            if dtz == 0:
                self.draw_count += 1
                self.last_game_status = 'Draw (DTZ:0)'
            elif dtz > 0:
                self.win_count += 1
                self.last_game_status = 'Won (DTZ:' + str(dtz) + ')'
            elif dtz < 0:
                self.lose_count += 1
                self.last_game_status = 'Lost (DTZ:' + str(dtz) + ')'
        return game_over

    def player_turn(self):
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

    def opponent_turn(self):
        # opponent turn
        if self.opponent == 'Stockfish 11':
            opponent_best_move = self.stockfish_move()
        elif self.opponent == 'Minimax with Alpha-Beta Pruning':
            opponent_best_move = self.minimax_move()
        elif self.opponent == 'MCTS-EPT' or self.opponent == 'MCTS-EPT (CP Normalized)' or self.opponent == 'MCTS-EPT (CP Normalized) w/ Implicit Minimax Backups':
            # update algo board state with current board, important for restarting games
            self.opponent_algo.starting_board_state = self.board_state.copy()
            # initialize root node with children at depth 1
            root_node = self.opponent_algo.algo_init()

            start_time = datetime.datetime.utcnow()  # current time
            # run simulation until allowed time is reached
            while datetime.datetime.utcnow() - start_time < self.opponent_algo.calc_time:
                end_sim = self.opponent_algo.algo(root_node)
                if end_sim:
                    break
            best_move, _, _, _, _, _ = self.opponent_algo.algo_render()

            # parse from san to uci for last move on svg
            opponent_best_move = self.board_state.parse_san(best_move)
        else:
            opponent_best_move = self.engine_move()
        try:
            self.board_state.push(opponent_best_move)
        except:
            # random move if opponent engine best move None
            self.board_state.push(random.choice(
                list(self.board_state.legal_moves)))
        # time.sleep(0.5)  # delay to see board state after mcts
        self.animate_board(opponent_best_move)
        self.update_cp()

    def run_algo_playout(self, game_number):

        if game_number % 2 == 0:
            self.opponent_turn()
            end_game = self.check_game_over()
            if end_game:
                return end_game

            self.player_turn()
            end_game = self.check_game_over()
            if end_game:
                return end_game

        else:
            self.player_turn()
            end_game = self.check_game_over()
            if end_game:
                return end_game

            self.opponent_turn()
            end_game = self.check_game_over()
            if end_game:
                return end_game

        # tablebase_end_game = self.check_tablebase()
        # if tablebase_end_game:
        #     return tablebase_end_game
        print(self.moves_played)
        if self.moves_played == 50:
            info = self.evaluation_engine.analyse(
                self.board_state, chess.engine.Limit(depth=3))
            stat_eval = StaticEval.evaluate_board(self.board_state)
            if self.algo_obj.original_player:
                self.last_game_status = 'Inconclusive (Stockfish: ' + \
                    info["score"].white().__str__() + \
                    ' | Static: ' + str(stat_eval) + ')'
            else:
                self.last_game_status = 'Inconclusive (Stockfish: ' + \
                    info["score"].black().__str__() + ' | Static: ' + \
                    str(-stat_eval) + ')'
            end_game = True

        return end_game  # continue game is end_game == False

    def iterate(self):
        for each_game in range(self.num_games):
            game_number = each_game + 1
            end = False
            self.board_state = self.starting_board_state.copy()
            self.moves_played = 0
            if game_number % 2 == 0:
                # alternate starting players
                self.algo_obj.original_player = False
                self.flip_board = True
                if self.opponent == 'MCTS-EPT':
                    self.opponent_algo.original_player = True
            else:
                self.algo_obj.original_player = True
                self.flip_board = False
                if self.opponent == 'MCTS-EPT':
                    self.opponent_algo.original_player = False

            while(not(end)):
                end = self.run_algo_playout(game_number)
                print('Wins: ' + str(self.win_count))
                print('Loses: ' + str(self.lose_count))
                print('\n')

            globals()['scoreboard'].text(
                'Wins: ' + str(self.win_count) + '\nLosses: ' + str(self.lose_count) + '\nDraws: ' + str(self.draw_count))
            st.text('Game ' + str(game_number) +
                    ' - ' + str(self.last_game_status) + ' - ' + str(self.moves_played) + ' Moves')
        try:
            self.opponent_engine.quit()
        except:
            print('No uci opponent engine created')
