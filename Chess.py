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
# import concurrent.futures
# import threading
import random

from chess.engine import Cp, Mate, MateGiven
from MCTS import MCTS
from MCTS_EPT import MCTSEPT
from graphviz import Source
from PIL import Image
# from streamlit.ReportThread import add_report_ctx


# chess.svg.piece(chess.Piece.from_symbol("R"))
# board = chess.Board("8/8/8/8/4N3/8/8/8 w - - 0 1")
# squares = board.attacks(chess.E4)
# chess.svg.board(board=board, squares=squares)


class MyGameBuilder(chess.pgn.GameBuilder):
    def handle_error(self, error):
        pass  # Ignore error


# Open PGN data file
pgn = open("./data/pgn/kasparov-deep-blue-1997.pgn")
game = chess.pgn.read_game(pgn, Visitor=MyGameBuilder)

# game = chess.pgn.Game()
print(game.headers)

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
    html = r'<img src="data:image/svg+xml;base64,%s" width="400" height="400"/>' % b64
    st.write(html, unsafe_allow_html=True)


def run_mcts(board, calc_time, max_moves, c_value):
    simulation = MCTS(board, time=calc_time, max_moves=max_moves, C=c_value)
    # initialize root node with children at depth 1
    root_node = simulation.mcts_init()
    if board.turn:
        player = True
    else:
        player = False

    calc_time = datetime.timedelta(seconds=calc_time)
    st.write('Calculation time: ' + str(calc_time))
    timer_status = st.empty()
    # interval = datetime.timedelta(seconds=1)
    # multiplier = 0
    start_time = datetime.datetime.utcnow()  # current time
    while datetime.datetime.utcnow() - start_time < calc_time:  # run simulation until allowed time is reached
        # if datetime.datetime.utcnow() - start_time + multiplier*interval >= interval:
        #****TIMER SLOWS DOWN PROGRAM, REMOVE LINE BELOW TO OPTIMIZE****#
        timer_status.text(datetime.datetime.utcnow() - start_time)
        end_sim = simulation.mcts(root_node, player)
        if end_sim:
            break
    timer_status.text('Done!')
    best_move, weight_list, winsim_list, score_list, total_wins, total_sims = simulation.mcts_render()
    return best_move, weight_list, winsim_list, score_list, total_wins, total_sims


def run_mcts_ept(board, calc_time, terminal_depth, c_value):
    st.write('EPT Ran')
    simulation = MCTSEPT(board, time=calc_time,
                         terminal_depth=terminal_depth, C=c_value)
    # initialize root node with children at depth 1
    root_node = simulation.mcts_ept_init()
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
        end_sim = simulation.mctsept(root_node, player)
        if end_sim:
            break
    timer_status.text('Done!')
    best_move, weight_list, winsim_list, score_list, total_wins, total_sims = simulation.mcts_ept_render()
    return best_move, weight_list, winsim_list, score_list, total_wins, total_sims


def show_stats(best_move, weight_list, winsim_list, score_list, total_wins, total_sims):
    st.header('Move Statistics')
    st.subheader('Total Wins/Simulations: ' +
                 str(total_wins) + '/' + str(total_sims))
    # st.subheader('Total Win Rate: ' +
    #              str(round(total_wins/total_sims*100, 2)) + '%')

    dot_graph = pydotplus.graphviz.graph_from_dot_file('./tree.dot')
    dot_graph.write_png("tree.png")

    move_stats_list = pd.DataFrame(
        {'move': weight_list,
         'win/sim': winsim_list,
         'score': score_list,
         })

    fig = px.bar(move_stats_list, x='move', y='score',
                 hover_data=['move', 'score'], color='score',
                 labels={'move': 'Move Played', 'score': 'Win Percentage (%)'}, height=400, width=800)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader('Best Move: ' + str(best_move))

    st.dataframe(move_stats_list.style.highlight_max(axis=0), 1000, 1000)
    # st.write(move_stats_list, use_container_width=True)

    st.header('Monte Carlo Tree JSON')
    # with open('test.json') as json_file:
    #     data = json.load(json_file)
    # data_json = json.dumps(data)
    # st.json(data_json)

    st.header('Monte Carlo Tree Generated')
    image = Image.open('tree.png')
    st.image(image, caption='',
             use_column_width=True)

    st.success('Done!')
    st.balloons()


# rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
# r1bqkbnr/p1pp1ppp/1pn5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 2 4
# rnb1kbn1/2Bppp2/1p4p1/2P5/2BPP2p/p4N1P/PP3PP1/R2QK2R b KQq - 0 13

# Streamlit
st.title('MCTS Chess Dashboard')
fen = st.text_input(
    'Input FEN', 'r1bqkbnr/p1pp1ppp/1pn5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 2 4')
try:
    board = chess.Board(fen)
    # board.push_san("Qxf7")
    # board.push_san("e4")
    # board.push_san("e5")
    # board.push(random.choice(list(board.legal_moves)))
    render_svg(chess.svg.board(board=board))
except:
    st.write('Invalid Fen')

# # Evalutate score using stockfish evaluation
# # engine = chess.uci.popen_engine("stockfish.exe")
# engine = chess.engine.SimpleEngine.popen_uci("stockfish.exe")
# print("\n")
# print(datetime.datetime.utcnow())
# info = engine.analyse(board, chess.engine.Limit(time=0.1))
# # info = engine.analyse(board, chess.engine.Limit(depth=20))
# print("Score:", info["score"])
# print(info)
# print("\n")
# print(datetime.datetime.utcnow())
# engine.quit()  # Exit stockfish engine

print("\n")
if board.turn:
    print('Original player: WHITE')
else:
    print('Original player: BLACK')

st.sidebar.title("Parameters")
st.sidebar.text("")
calc_time = st.sidebar.number_input('Calculation time (seconds)', 10)
c_value = st.sidebar.number_input('UCT exploration constant', 1.4)
max_moves = st.sidebar.slider(
    'Maximum moves per simulation (MCTS)', 0, 1000, 500)
terminal_depth = st.sidebar.slider(
    'Playout terminal depth (MCTS-EPT)', 0, 50, 5)

st.text("")
algo = st.radio("Select Algorithm", ('MCTS', 'MCTS-EPT'))

# Call algo on button click
if st.button('Run'):
    if algo == 'MCTS':
        best_move, weight_list, winsim_list, score_list, total_wins, total_sims = run_mcts(
            board, calc_time, max_moves, c_value)
    elif algo == 'MCTS-EPT':
        best_move, weight_list, winsim_list, score_list, total_wins, total_sims = run_mcts_ept(
            board, calc_time, terminal_depth, c_value)
    else:
        st.write('No algorithm selected')
    show_stats(best_move, weight_list, winsim_list,
               score_list, total_wins, total_sims)
