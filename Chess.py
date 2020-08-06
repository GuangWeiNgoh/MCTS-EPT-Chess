# from treelib import Node, Tree
import sys
# !{sys.executable} -m pip install python-chess
# !{sys.executable} -m pip install -U treelib
# pip install python-chess
# pip install -U treelib # not needed
# pip install anytree
# pip install graphviz
# pip install streamlit
# pip install plotly==4.9.0
# pip install graphviz
# pip install pydotplus
# pip install cairosvg

import asyncio
import chess
# import chess.uci
import chess.engine
import chess.svg
import chess.pgn
import streamlit as st
import numpy as np
import pandas as pd
# import plotly.figure_factory as ff
import plotly.express as px
import numpy as np
import graphviz as graphviz
import pydotplus
import time
import datetime
import json
import base64  # svg
# import cairosvg  # svg to png to animate board
# import concurrent.futures
# import threading
import random

from chess.engine import Cp, Mate, MateGiven
from MCTS import MCTS
from MCTS_EPT import MCTSEPT
from graphviz import Source
from PIL import Image
from Playout import Playout
# from streamlit.ReportThread import add_report_ctx


# chess.svg.piece(chess.Piece.from_symbol("R"))
# board = chess.Board("8/8/8/8/4N3/8/8/8 w - - 0 1")
# squares = board.attacks(chess.E4)
# chess.svg.board(board=board, squares=squares)


# class MyGameBuilder(chess.pgn.GameBuilder):
#     def handle_error(self, error):
#         pass  # Ignore error


# # Open PGN data file
# pgn = open("./data/pgn/kasparov-deep-blue-1997.pgn")
# game = chess.pgn.read_game(pgn, Visitor=MyGameBuilder)

# # game = chess.pgn.Game()
# print(game.headers)

# while not board.is_game_over():
#     result = engine.play(board, chess.engine.Limit(time=0.1))
#     board.push(result.move)

# Print legal moves
# print("\n")
# print(board.legal_moves)

# Make moves in SAN notation
# http://cfajohnson.com/chess/SAN/


# board.push_san("e4")
# board.push_san("e5")
# board.push_san("Qh5")
# board.push_san("Nc6")
# board.push_san("Bc4")
# board.push_san("Nf6")
# board.push_san("Qxf7")

# Prints FEN
# https://support.chess.com/article/658-what-are-pgn-fen
# print(board.fen())
# print(board.shredder_fen())

# Adjust board layout with FEN
# board = chess.Board("8/8/8/2k5/4K3/8/8/8 w - - 4 45")

# Checks piece at specific position
# print(board.piece_at(chess.C4))


def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img id="boardsvg" src="data:image/svg+xml;base64,%s" width="400" height="400"/>' % b64
    # boardsvg.write(html, unsafe_allow_html=True)
    st.write(html, unsafe_allow_html=True, key='boardsvg')


# def animate_board():
#     boardholder = st.empty()
#     count = 0
#     while(1):
#         if count % 2 == 0:
#             board = chess.Board(
#                 'r2q1rk1/pp1n1ppp/2pbpn2/3p4/6b1/1P1P1NP1/PBPNPPBP/R2Q1RK1 w - - 3 9')
#             board_svg = chess.svg.board(board=board)
#             cairosvg.svg2png(board_svg, write_to="board.png")
#             boardimg = Image.open('board.png')
#             time.sleep(0.5)
#             boardholder.image(boardimg)
#         else:
#             board = chess.Board(
#                 'r1bq1rk1/2p1bpp1/p1np1n1p/1p2p3/3PP3/1BP2N1P/PP3PP1/RNBQR1K1 b - - 0 10')
#             board_svg = chess.svg.board(board=board)
#             cairosvg.svg2png(board_svg, write_to="board.png")
#             boardimg = Image.open('board.png')
#             time.sleep(0.5)
#             boardholder.image(boardimg)
#         count += 1


def run_algo(simulation, calc_time):
    # initialize root node with children at depth 1
    root_node = simulation.algo_init()
    if board.turn:
        player = True
    else:
        player = False

    calc_time = datetime.timedelta(seconds=calc_time)
    st.write('Calculation time: ' + str(calc_time))
    timer_status = st.empty()
    start_time = datetime.datetime.utcnow()  # current time
    while datetime.datetime.utcnow() - start_time < calc_time:  # run simulation until allowed time is reached
        # if datetime.datetime.utcnow() - start_time + multiplier*interval >= interval:
        #****TIMER SLOWS DOWN PROGRAM, REMOVE LINE BELOW TO OPTIMIZE****#
        timer_status.text(datetime.datetime.utcnow() - start_time)
        end_sim = simulation.algo(root_node, player)
        if end_sim:
            break
    timer_status.text('Done!')
    best_move, weight_list, winsim_list, score_list, total_wins, total_sims = simulation.algo_render()
    return best_move, weight_list, winsim_list, score_list, total_wins, total_sims


def show_stats(best_move, weight_list, winsim_list, score_list, total_wins, total_sims, algo):
    st.header('Move Statistics')
    st.subheader('Total Wins/Simulations: ' +
                 str(total_wins) + '/' + str(total_sims))
    # st.subheader('Total Win Rate: ' +
    #              str(round(total_wins/total_sims*100, 2)) + '%')

    # dot_graph = pydotplus.graphviz.graph_from_dot_file('./tree.dot')
    # dot_graph.write_png("tree.png")
    if algo == 'MCTS':
        plot_label = 'Win Percentage (%)'
        df_label = 'win/sim'
    else:
        plot_label = 'Advantage Percentage (%)'
        df_label = 'adv/sim'

    move_stats_list = pd.DataFrame(
        {'move': weight_list,
         df_label: winsim_list,
         'score': score_list,
         })

    move_stats_list.sort_values(by=['score'], inplace=True, ascending=False)
    # move_stats_list.sort_values(by=['score'], ascending=False)

    fig = px.bar(move_stats_list, x='move', y='score',
                 hover_data=['move', 'score'], color='score',
                 labels={'move': 'Move Played', 'score': plot_label}, height=400, width=800)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader('Best Move: ' + str(best_move))

    st.dataframe(move_stats_list.style.highlight_max(axis=0), 1000, 1000)
    # st.write(move_stats_list, use_container_width=True)

    st.header('Monte Carlo Tree JSON')
    # with open('test.json') as json_file:
    #     data = json.load(json_file)
    # data_json = json.dumps(data)
    # st.json(data_json)

    # st.header('Monte Carlo Tree Generated')
    # image = Image.open('tree.png')
    # st.image(image, caption='',
    #          use_column_width=True)

    st.success('Done!')
    st.balloons()


# rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
# r1bqkbnr/p1pp1ppp/1pn5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 2 4
# rn2kbn1/2Bppp2/bp4p1/2P5/2BPP2p/p4N1P/PP3PP1/R2QK2R w KQq - 1 14
# Qa4 Qb3 Bd5 Bxa6 winning
# r2q1rk1/pp1n1ppp/2pbpn2/3p4/6b1/1P1P1NP1/PBPNPPBP/R2Q1RK1 w - - 3 9
# h3 e4 c4 Re1
# r1bq1rk1/2p1bpp1/p1np1n1p/1p2p3/3PP3/1BP2N1P/PP3PP1/RNBQR1K1 b - - 0 10
# Re8 Bb7 Bd7 Na5

# Streamlit
st.title('MCTS Chess Dashboard')
fen = st.text_input(
    'Input FEN', 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
try:
    board = chess.Board(fen)
    # board.push_san("Qxf7")
    # board.push_san("e4")
    # board.push_san("e5")
    # board.push(random.choice(list(board.legal_moves)))
    if board.turn:
        st.text('WHITE to play')
    else:
        st.text('BLACK to play')
    board_svg = chess.svg.board(board=board)
    render_svg(board_svg)
except:
    st.write('Invalid Fen')


# # Evalutate score using stockfish evaluation
# engine = chess.engine.SimpleEngine.popen_uci("stockfish.exe")
# print("\n")
# print(datetime.datetime.utcnow())
# # info = engine.analyse(board, chess.engine.Limit(time=0.1))
# info = engine.analyse(board, chess.engine.Limit(depth=20), multipv=4)
# # print("Score:", info["score"])
# print(board.san(info[0]["pv"][0]))
# print(board.san(info[1]["pv"][0]))
# print(board.san(info[2]["pv"][0]))
# print(board.san(info[3]["pv"][0]))
# print(datetime.datetime.utcnow())
# engine.quit()  # Exit stockfish engine

st.sidebar.title("Parameters")
st.sidebar.text("")
calc_time = st.sidebar.number_input('Calculation time (seconds)', 1)
st.sidebar.subheader("MCTS")
c_value = st.sidebar.number_input(
    'UCT exploration constant', 1.4, key='c_value')
max_moves = st.sidebar.slider(
    'Maximum moves per simulation (MCTS)', 0, 1000, 500)
st.sidebar.subheader("MCTS-EPT")
ept_root_c_value = st.sidebar.number_input(
    'UCT exploration constant @ root', 3, key='ept_root_c_value')
ept_c_value = st.sidebar.number_input(
    'UCT exploration constant', 1.4, key='ept_c_value')
terminal_depth = st.sidebar.slider(
    'Playout terminal depth (MCTS-EPT)', 0, 50, 5)

st.text("")
algo = st.radio("Select Algorithm", ('MCTS-EPT', 'MCTS'))

# Call algo on button click
if st.button('Generate move'):
    if algo == 'MCTS':
        simulation = MCTS(board, time=calc_time,
                          max_moves=max_moves, C=c_value)
        best_move, weight_list, winsim_list, score_list, total_wins, total_sims = run_algo(
            simulation, calc_time)
    elif algo == 'MCTS-EPT':
        simulation = MCTSEPT(board, time=calc_time,
                             terminal_depth=terminal_depth, C=ept_c_value, root_C=ept_root_c_value)
        best_move, weight_list, winsim_list, score_list, total_wins, total_sims = run_algo(
            simulation, calc_time)
    else:
        st.write('No algorithm selected')
    show_stats(best_move, weight_list, winsim_list,
               score_list, total_wins, total_sims, algo)

st.header('Playout vs Stockfish')

num_games = st.number_input(
    'Number of games', 1, key='num_games')

opponent_depth = st.slider(
    'Stockfish search depth', 0, 30, 10, key='engine_depth')

if st.button('Start playout'):
    st.text('Player and opponent stats')
    st.text('Improve SVG')
    st.text('Change depth to time?')

    if algo == 'MCTS':
        algo = MCTS(board, time=calc_time,
                    max_moves=max_moves, C=c_value)
        playout = Playout(board, num_games, opponent_depth, algo)
        # playout.run_algo_playout()
        playout.iterate()

    elif algo == 'MCTS-EPT':
        algo = MCTSEPT(board, time=calc_time,
                       terminal_depth=terminal_depth, C=ept_c_value, root_C=ept_root_c_value)
        playout = Playout(board, num_games, opponent_depth, algo)
        # playout.run_algo_playout()
        playout.iterate()

    else:
        st.write('No algorithm selected')
