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
# import concurrent.futures
# import threading


from MonteCarloTree import MonteCarloTree as MCTSTree
from graphviz import Source
from PIL import Image
from streamlit.ReportThread import add_report_ctx

# import MonteCarloTree as MCTSTree

# chess.svg.piece(chess.Piece.from_symbol("R"))
# board = chess.Board("8/8/8/8/4N3/8/8/8 w - - 0 1")
# squares = board.attacks(chess.E4)
# chess.svg.board(board=board, squares=squares)


async def timer_func(calc_time):
    class tqdm:
        def __init__(self, iterable, title=None):
            if title:
                st.write(title)
            self.prog_bar = st.progress(0)
            self.iterable = iterable
            self.length = len(iterable)
            self.i = 0

        def __iter__(self):
            for obj in self.iterable:
                yield obj
                self.i += 1
                current_prog = self.i / self.length
                self.prog_bar.progress(current_prog)
    for i in tqdm(range(calc_time), title='tqdm style progress bar'):
        # time.sleep(1)
        await asyncio.sleep(1)

    future.set_result("Completed")


async def mcts_func(board, calc_time, max_moves, c_value):
    simulation = MCTSTree(board, time=calc_time,
                          max_moves=max_moves, C=c_value)
    best_move, weight_list, winsim_list, score_list, total_wins, total_sims = simulation.mcts_iter()
    return best_move, weight_list, winsim_list, score_list, total_wins, total_sims


async def main():
    # class MyGameBuilder(chess.pgn.GameBuilder):
    #     def handle_error(self, error):
    #         pass  # Ignore error

    # # Open PGN data file
    # pgn = open("./data/pgn/kasparov-deep-blue-1997.pgn")
    # game = chess.pgn.read_game(pgn, Visitor=MyGameBuilder)

    # # game = chess.pgn.Game()
    # print(game.headers)

    # engine = chess.engine.SimpleEngine.popen_uci("stockfish.exe")

    # # board = chess.Board()
    # board = chess.Board(
    #     "r1bqkbnr/p1pp1ppp/1pn5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 2 4")
    # # while not board.is_game_over():
    # #     result = engine.play(board, chess.engine.Limit(time=0.1))
    # #     board.push(result.move)

    # # Print legal moves
    # print("\n")
    # print(board.legal_moves)

    # # Make moves in SAN notation
    # # http://cfajohnson.com/chess/SAN/

    # # board.push_san("e4")
    # # board.push_san("e5")
    # # board.push_san("Qh5")
    # # board.push_san("Nc6")
    # # board.push_san("Bc4")
    # # board.push_san("Nf6")
    # # board.push_san("Qxf7")

    # # Evalutate score using stockfish evaluation
    # # info = engine.analyse(board, chess.engine.Limit(time=0.1))
    # info = engine.analyse(board, chess.engine.Limit(depth=20))
    # print("\n")
    # print("Score:", info["score"])
    # print(info.get("score"), info.get("pv"))
    # print(info)

    # engine.quit()  # Exit stockfish engine

    # # Check game states
    # print("\n")
    # print("Checkmate:", board.is_checkmate())
    # print("Stalemate:", board.is_stalemate())
    # print("Insufficient Material:", board.is_insufficient_material())
    # print("Gameover:", board.is_game_over())

    # # Prints FEN
    # # https://support.chess.com/article/658-what-are-pgn-fen
    # # print(board.fen())
    # # print(board.shredder_fen())

    # # Adjust board layout with FEN
    # # board = chess.Board("8/8/8/2k5/4K3/8/8/8 w - - 4 45")

    # # Checks piece at specific position
    # # print(board.piece_at(chess.C4))

    # print("\n")
    # print(board)
    # print(board.legal_moves)

    # # Streamlit
    # st.title('MCTS Chess Visualization')

    # st.sidebar.title("Parameters\n\n\n")
    # calc_time = st.sidebar.number_input('Calculation time (seconds)', 5)
    # c_value = st.sidebar.number_input('UCT exploration constant', 1.4)
    # max_moves = st.sidebar.slider('Maximum moves per simulation', 0, 1000, 800)
    # latest_iteration = st.empty()
    # bar = st.progress(0)

    future = asyncio.Future()
    await asyncio.ensure_future(timer_func(future))
    print(future.result())
    # tasks = []
    # tasks.append(asyncio.ensure_future(mcts_func(board, calc_time, max_moves, c_value))
    # tasks.append(asyncio.ensure_future(timer_func(calc_time))
    # await asyncio.gather(*tasks)
    # mcts = loop.create_task(mcts_func(board, calc_time, max_moves, c_value))
    # timer = loop.create_task(timer_func(calc_time))
    # loop.run_until_complete(mcts, timer)
    # loop.close()

    # print("\n")
    # print("Passed")

    # # with st.spinner('Wait for it...'):
    # #     time.sleep(0)
    # st.success('Done!')

    # # Call MCTSTree
    # # simulation.create_tree()
    # # simulation.load_tree()
    # # board = chess.Board(
    # #     "r1bqkbnr/p1pp1ppp/1pn5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 2 4")

    # st.header('Move Statistics')

    # st.subheader('Total Wins/Simulations: ' +
    #              str(total_wins) + '/' + str(total_sims))
    # # st.subheader('Total Win Rate: ' +
    # #              str(round(total_wins/total_sims*100, 2)) + '%')

    # dot_graph=pydotplus.graphviz.graph_from_dot_file('./tree.dot')
    # dot_graph.write_png("tree.png")

    # move_stats_list=pd.DataFrame(
    #     {'move': weight_list,
    #      'win/sim': winsim_list,
    #      'score': score_list,
    #      })

    # fig=px.bar(move_stats_list, x='move', y='score',
    #              hover_data=['move', 'score'], color='score',
    #              labels={'move': 'Move Played', 'score': 'Win Percentage (%)'}, height=400, width=800)
    # st.plotly_chart(fig, use_container_width=True)

    # st.subheader('Best Move: ' + str(best_move))

    # st.dataframe(move_stats_list.style.highlight_max(axis=0), 1000, 1000)

    # st.header('Monte Carlo Tree Generated')
    # image=Image.open('tree.png')
    # st.image(image, caption='',
    #          use_column_width=True)

    # st.balloons()

# if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()
    # try:
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(main())
    # except Exception as e:
    #     pass
    # finally:
    #     loop.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close
