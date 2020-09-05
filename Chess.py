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
# import chess.syzygy  # endgame tablebases
import streamlit as st
import numpy as np
import pandas as pd
# import plotly.figure_factory as ff
import plotly.express as px
import numpy as np
# import graphviz as graphviz
# import pydotplus
import time
import datetime
import json
import base64  # svg
# import cairosvg  # svg to png to animate board
# import concurrent.futures
# import threading
import random
import StaticEval

from chess.engine import Cp, Mate, MateGiven
from MCTS import MCTS
from MCTS_EPT import MCTSEPT
from MCTS_EPT_2 import MCTSEPT2
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


def run_algo(simulation, calc_time):
    # initialize root node with children at depth 1
    root_node = simulation.algo_init()
    # if board.turn:
    #     player = True
    # else:
    #     player = False

    calc_time = datetime.timedelta(seconds=calc_time)
    st.write('Calculation time: ' + str(calc_time))
    timer_status = st.empty()
    start_time = datetime.datetime.utcnow()  # current time
    while datetime.datetime.utcnow() - start_time < calc_time:  # run simulation until allowed time is reached
        # if datetime.datetime.utcnow() - start_time + multiplier*interval >= interval:
        #****TIMER SLOWS DOWN PROGRAM, REMOVE LINE BELOW TO OPTIMIZE****#
        timer_status.text(datetime.datetime.utcnow() - start_time)
        end_sim = simulation.algo(root_node)
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
    if algo == 'MCTS-EPT':
        plot_label = 'Advantage Percentage (%)'
        df_label = 'adv/sim'
    else:
        plot_label = 'Win Percentage (%)'
        df_label = 'win/sim'

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
    # with open('tree.json') as json_file:
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
# rn2kbn1/2Bppp2/bp4p1/2P5/Q1BPP2p/p4N1P/PP3PP1/R3K2R b KQq - 2 14
# r2q1rk1/pp1n1ppp/2pbpn2/3p4/6b1/1P1P1NP1/PBPNPPBP/R2Q1RK1 w - - 3 9
# h3 e4 c4 Re1
# r1bq1rk1/2p1bpp1/p1np1n1p/1p2p3/3PP3/1BP2N1P/PP3PP1/RNBQR1K1 b - - 0 10
# Re8 Bb7 Bd7 Na5

# black in check
# rn2kbn1/2BppB2/bp4p1/2P5/3PP2p/p4N1P/PP3PP1/R2QK2R b KQq - 0 14

# Mate in 3:
# r5rk/5p1p/5R2/4B3/8/8/7P/7K w q - 0 1
# r5rk/7p/R4p2/4B3/8/8/7P/7K w q - 0 2
# r6k/6rp/R4B2/8/8/8/7P/7K w q - 1 3

# Mate in 5:
# 6k1/3b3r/1p1p4/p1n2p2/1PPNpP1q/P3Q1p1/1R1RB1P1/5K2 b

# try board.pop() for expansion
# try max() function for selection
# check average time for minimax turn
# set calc time default similar to minimax turn time
# simplify selection function (duplicate codes)
# test without lock depth
# maybe limit max cp for non mate to 5000?
# upgrade streamlit to 0.65.0 (inline svg)
# implement static evaluation function
# select node that minimizes win percentage at opponent depth? (1-each.score at even depth)

# print(Mate(2).score(mate_score=100000))
# score = 1 / (1 + (10 ** -(6382 / 400)))
# print(score)

# Streamlit
st.beta_set_page_config(
    page_title="MCTS Chess Dashboard",
    page_icon="♟️",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title('MCTS Chess Dashboard')
fen = st.text_input(
    'Input FEN', 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
try:
    board = chess.Board(fen)
    # Evalutate score using stockfish evaluation
    # print(datetime.datetime.utcnow())
    engine = chess.engine.SimpleEngine.popen_uci("stockfish.exe")
    info = engine.analyse(board, chess.engine.Limit(depth=3))
    # info = engine.analyse(board, chess.engine.Limit(depth=20))
    # info = engine.analyse(board, chess.engine.Limit(depth=20), multipv=4)
    # print(board.san(info[0]["pv"][0]))
    # print(board.san(info[1]["pv"][0]))
    # print(board.san(info[2]["pv"][0]))
    # print(board.san(info[3]["pv"][0]))
    if board.turn:
        st.text('WHITE to play')
        st.text('CP: ' + str(info['score']))
    else:
        st.text('BLACK to play')
        st.text('CP: ' + str(info['score']))
    engine.quit()  # Exit stockfish engine
    board_svg = chess.svg.board(board=board)
    render_svg(board_svg)
except:
    st.write('Invalid Fen')

# with chess.syzygy.open_tablebase("syzygy/3-4-5") as tablebase:
#     board = chess.Board("8/2K5/4B3/3N4/8/8/4k3/8 b - - 0 1")
#     # board = chess.Board(
#     #     "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
#     print(tablebase.get_wdl(board))
#     print(tablebase.get_dtz(board))
#     # print(tablebase.probe_wdl(board))
#     # print(tablebase.probe_dtz(board))

st.sidebar.title("Parameters")
st.sidebar.text("")
calc_time = st.sidebar.number_input('Calculation time (seconds)', 5)

st.sidebar.subheader("MCTS")
c_value = st.sidebar.number_input(
    'UCT exploration constant', 1.4, key='c_value')
max_moves = st.sidebar.slider(
    'Maximum moves per simulation (MCTS)', 0, 1000, 500)

st.sidebar.subheader("MCTS-EPT")
ept_root_c_value = st.sidebar.number_input(
    'UCT exploration constant @ root', 3.0, key='ept_root_c_value')
ept_c_value = st.sidebar.number_input(
    'UCT exploration constant', 1.4, key='ept_c_value')
terminal_depth = st.sidebar.slider(
    'Playout terminal depth', 0, 50, 3, key='ept_depth')

st.sidebar.subheader("MCTS-EPT (CP Normalized)")
ept_2_root_c_value = st.sidebar.number_input(
    'UCT exploration constant @ root', 0.8, key='ept_2_root_c_value')
ept_2_c_value = st.sidebar.number_input(
    'UCT exploration constant', 0.8, key='ept_2_c_value')
terminal_depth_2 = st.sidebar.slider(
    'Playout terminal depth', 0, 50, 3, key='ept_2_depth')

st.text("")
algo = st.radio("Select Algorithm",
                ('MCTS-EPT (CP Normalized)', 'MCTS-EPT', 'MCTS'))

# Call algo on button click
if st.button('Generate move'):
    if algo == 'MCTS':
        simulation = MCTS(board, time=calc_time,
                          max_moves=max_moves, C=c_value, player=board.turn)
        best_move, weight_list, winsim_list, score_list, total_wins, total_sims = run_algo(
            simulation, calc_time)
    elif algo == 'MCTS-EPT':
        simulation = MCTSEPT(board, time=calc_time,
                             terminal_depth=terminal_depth, C=ept_c_value, root_C=ept_root_c_value, player=board.turn)
        best_move, weight_list, winsim_list, score_list, total_wins, total_sims = run_algo(
            simulation, calc_time)
    elif algo == 'MCTS-EPT (CP Normalized)':
        simulation = MCTSEPT2(board, time=calc_time,
                              terminal_depth=terminal_depth_2, C=ept_2_c_value, root_C=ept_2_root_c_value, player=board.turn)
        best_move, weight_list, winsim_list, score_list, total_wins, total_sims = run_algo(
            simulation, calc_time)
    else:
        st.write('No algorithm selected')
    show_stats(best_move, weight_list, winsim_list,
               score_list, total_wins, total_sims, algo)

st.header('Playout vs Opponent Engine')

num_games = st.number_input(
    'Number of games', 1, key='num_games')

opponent_selection = st.selectbox(
    'Opponent engine', ('MCTS-EPT', 'Minimax with Alpha-Beta Pruning', 'Irina (1200 Elo)', 'CDrill (1800 Elo)', 'Clarabit (2058 Elo)', 'Stockfish 11'))

if opponent_selection == 'Stockfish 11':
    opponent_depth = st.slider(
        'Stockfish search depth', 0, 20, 1, key='stockfish_depth')
    opponent_calc_time = 0
    opponent_ept_root_c_value = 0
    opponent_ept_c_value = 0
elif opponent_selection == 'Irina (1200 Elo)':
    opponent_depth = st.slider(
        'Irina search time', 0, 20, 5, key='irina_depth')
    opponent_calc_time = 0
    opponent_ept_root_c_value = 0
    opponent_ept_c_value = 0
elif opponent_selection == 'CDrill (1800 Elo)':
    opponent_depth = st.slider(
        'CDrill search time', 0, 20, 5, key='cdrill_depth')
    opponent_calc_time = 0
    opponent_ept_root_c_value = 0
    opponent_ept_c_value = 0
elif opponent_selection == 'Clarabit (2058 Elo)':
    opponent_depth = st.slider(
        'Clarabit search time', 0, 20, 5, key='clarabit_depth')
    opponent_calc_time = 0
    opponent_ept_root_c_value = 0
    opponent_ept_c_value = 0
elif opponent_selection == 'Minimax with Alpha-Beta Pruning':
    opponent_depth = st.slider(
        'Minimax search depth', 0, 20, 4, key='minimax_depth')
    opponent_calc_time = 0
    opponent_ept_root_c_value = 0
    opponent_ept_c_value = 0
else:
    opponent_calc_time = st.number_input(
        'Calculation time (seconds)', 5, key='opponent_calc_time')
    opponent_depth = st.slider(
        'MCTS-EPT terminal depth', 0, 20, 3, key='opponent_ept_depth')
    opponent_ept_root_c_value = st.number_input(
        'UCT exploration constant @ root', 3.0, key='opponent_ept_root_c_value')
    opponent_ept_c_value = st.number_input(
        'UCT exploration constant', 1.4, key='opponent_ept_c_value')


if st.button('Start playout'):
    # st.text('Player and opponent stats')
    # st.text('Improve SVG')
    # st.text('Change depth to time?')
    st.subheader(str(num_games)+' Game Playout')
    st.text(str(algo) + ' vs ' + str(opponent_selection) +
            ' (Time ' + str(opponent_depth) + ')')

    if algo == 'MCTS':
        algo = MCTS(board, time=calc_time,
                    max_moves=max_moves, C=c_value, player=board.turn)
        playout = Playout(board, num_games,
                          opponent_selection, opponent_depth, algo, opponent_calc_time, opponent_ept_root_c_value, opponent_ept_c_value)
        # playout.run_algo_playout()
        playout.iterate()

    elif algo == 'MCTS-EPT':
        algo = MCTSEPT(board, time=calc_time,
                       terminal_depth=terminal_depth, C=ept_c_value, root_C=ept_root_c_value, player=board.turn)
        playout = Playout(board, num_games,
                          opponent_selection, opponent_depth, algo, opponent_calc_time, opponent_ept_root_c_value, opponent_ept_c_value)
        # playout.run_algo_playout()
        playout.iterate()

    elif algo == 'MCTS-EPT (CP Normalized)':
        algo = MCTSEPT2(board, time=calc_time,
                        terminal_depth=terminal_depth_2, C=ept_2_c_value, root_C=ept_2_root_c_value, player=board.turn)
        playout = Playout(board, num_games,
                          opponent_selection, opponent_depth, algo, opponent_calc_time, opponent_ept_root_c_value, opponent_ept_c_value)
        # playout.run_algo_playout()
        playout.iterate()

    else:
        st.write('No algorithm selected')
