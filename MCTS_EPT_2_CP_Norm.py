# MCTS
from __future__ import division

import chess
import chess.engine
# import chess.svg
# import chess.pgn
import chess.polyglot  # opening book
import time
import datetime
import random
import ast
import json
import math
import sys
import StaticEval  # static evaluation function
from copy import deepcopy
# from treelib import Node, Tree
# from graphviz import Digraph
from MCTS_EPT_2_Node import MCTSEPT2Node
from anytree import NodeMixin, RenderTree, LevelOrderIter
from pprint import pprint
from collections import OrderedDict
from anytree.exporter import DictExporter
from anytree.exporter import JsonExporter
from anytree.exporter import DotExporter
from anytree.exporter import UniqueDotExporter
from anytree.importer import JsonImporter
from math import log, sqrt


class MCTSEPT2(object):

    def __init__(self, board, **kwargs):
        # Takes an instance of a Board and optionally some keyword
        # arguments.  Initializes the list of game states and the
        # statistics tables.
        # pass
        print("\n")
        print("******* MCTS-EPT CP Norm Object Created *******")
        print("\n")
        self.starting_board_state = board.copy()
        self.calc_seconds = kwargs.get('time', 30)  # default set at 30 seconds
        # converts seconds into mm:ss format
        self.calc_time = datetime.timedelta(seconds=self.calc_seconds)
        print("Calculation time: " + str(self.calc_time))
        print("\n")
        self.terminal_depth = kwargs.get('terminal_depth', 5)
        print("Playout terminal depth: " + str(self.terminal_depth))
        print("\n")
        self.C = kwargs.get('C', 1.4)  # UCB1 exploration constant
        self.root_C = kwargs.get('root_C', 8.4)
        self.original_player = kwargs.get('player', None)
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish.exe")
        self.lock_depth = False  # lock depth to 1 when mate score is found

    # **********************************************************************************************************************

    def load_tree(self):
        with open('test.json') as json_file:
            data = json.load(json_file)

        print(data)
        print("\n")
        data_json = json.dumps(data)
        importer = JsonImporter()
        d0 = importer.import_(data_json)
        print(RenderTree(d0))
        # https://anycache.readthedocs.io/en/latest/

    # **********************************************************************************************************************

    def run_selection(self, node):
        # select child that maximizes UCB1
        while not(node.is_leaf):
            if node.depth == 0:  # use root_C for selection from root node
                c_value = self.root_C
            else:
                c_value = self.C

            if node.sims == 0:  # only for root node
                node = node.children[0]
            else:
                max_ucb = -math.inf
                ucb_score = -math.inf
                log_value = log(node.sims)
                for each in node.children:
                    if each.sims == 0:
                        ucb_score = math.inf
                    else:
                        # UCT
                        # ucb_score = ((each.score) + (c_value *
                        #                              sqrt((2*log_value)/each.sims)))
                        # UCB1
                        # ucb_score = ((each.score) + (c_value *
                        #                              sqrt(log_value/each.sims)))
                        # UCB1-Tuned
                        # variance = each.score * (1 - each.score)
                        ucb_score = each.score + c_value * sqrt((log_value/each.sims) * min(1/4, (each.score * (1 - each.score) +
                                                                                                  sqrt(2*log_value/each.sims))))
                    if ucb_score > max_ucb:
                        max_ucb = ucb_score
                        node = each
        return node

    # **********************************************************************************************************************

    def opening_expansion(self, node, opening_moves):
        board_state = chess.Board(node.state)
        for move in opening_moves:  # add all legal move nodes to tree
            original_state = board_state.copy()
            # original_state.push_san(move)
            original_state.push(move)
            i = 0
            while(1):
                try:
                    # check if node object exists in global variables
                    globals()[str(original_state.fen())+str(i)]
                except:
                    # create node if does not exist
                    globals()[str(original_state.fen())+str(i)] = MCTSEPT2Node(state=str(original_state.fen()), key=str(
                        original_state.fen())+str(i), parent=globals()[node.key], weight=board_state.san(move))

                    # For case where node is expanded and new node is terminal node
                    if original_state.is_game_over():  # check if it is a terminal node
                        globals()[str(original_state.fen())+str(i)
                                  ].termnode = True  # set as terminal node
                        # set terminal result to false if draw or loss
                        globals()[str(original_state.fen()) +
                                  str(i)].termresult = 0.0
                        if original_state.is_checkmate():  # assign winner only if checkmate
                            if original_state.turn == self.original_player:
                                globals()[str(original_state.fen()) +
                                          str(i)].termresult = 0.0
                            else:
                                globals()[str(original_state.fen()) +
                                          str(i)].termresult = 1.0

                    break
                else:
                    i += 1  # increment index if exists

    # **********************************************************************************************************************

    def move_ordering(self, board, depth):
        # print(datetime.datetime.utcnow())
        move_list = list(board.legal_moves)
        eval_list = []
        for move in move_list:
            board.push(move)
            score = StaticEval.evaluate_board(board)
            # if depth % 2 == 0:
            #     # score = self.stockfish_eval(board)
            #     score = StaticEval.evaluate_board(board)
            # else:
            #     # score = 1-(self.stockfish_eval(board))
            #     score = -(StaticEval.evaluate_board(board))
            eval_list.append((move, score))
            board.pop()
        import operator
        ordered_list = sorted(
            eval_list, key=operator.itemgetter(1), reverse=True)
        # print(ordered_list)
        # print(datetime.datetime.utcnow())
        return ordered_list
        # for move in ordered_list[:5]:
        #     print(move[0])

    # **********************************************************************************************************************

    def ordered_expansion(self, node, count):
        board_state = chess.Board(node.state)

        # order legal moves with stockfish eval
        ordered_list = self.move_ordering(board_state, node.depth)
        for move in ordered_list[:count]:  # add top 5 legal move nodes to tree
            # for move in ordered_list:
            original_state = board_state.copy()
            # original_state.push_san(move)
            original_state.push(move[0])
            i = 0
            # print(type(move[0]))
            while(1):
                try:
                    # check if node object exists in global variables
                    globals()[str(original_state.fen())+str(i)]
                except:
                    # create node if does not exist
                    globals()[str(original_state.fen())+str(i)] = MCTSEPT2Node(state=str(original_state.fen()), key=str(
                        original_state.fen())+str(i), parent=globals()[node.key], weight=board_state.san(move[0]))

                    # For case where node is expanded and new node is terminal node
                    if original_state.is_game_over():  # check if it is a terminal node
                        globals()[str(original_state.fen())+str(i)
                                  ].termnode = True  # set as terminal node
                        # set terminal result to false if draw or loss
                        globals()[str(original_state.fen()) +
                                  str(i)].termresult = 0.0
                        if original_state.is_checkmate():  # assign winner only if checkmate
                            if original_state.turn == self.original_player:
                                globals()[str(original_state.fen()) +
                                          str(i)].termresult = 0.0
                            else:
                                globals()[str(original_state.fen()) +
                                          str(i)].termresult = 1.0

                    break
                else:
                    i += 1  # increment index if exists

    # **********************************************************************************************************************

    def run_expansion(self, node):
        board_state = chess.Board(node.state)

        move_list = list(board_state.legal_moves)
        for move in move_list:  # add all legal move nodes to tree
            original_state = board_state.copy()
            # original_state.push_san(move)
            original_state.push(move)
            i = 0
            while(1):
                try:
                    # check if node object exists in global variables
                    globals()[str(original_state.fen())+str(i)]
                except:
                    # create node if does not exist
                    globals()[str(original_state.fen())+str(i)] = MCTSEPT2Node(state=str(original_state.fen()), key=str(
                        original_state.fen())+str(i), parent=globals()[node.key], weight=board_state.san(move))

                    # For case where node is expanded and new node is terminal node
                    if original_state.is_game_over():  # check if it is a terminal node
                        globals()[str(original_state.fen())+str(i)
                                  ].termnode = True  # set as terminal node
                        # set terminal result to false if draw or loss
                        globals()[str(original_state.fen()) +
                                  str(i)].termresult = 0.0
                        if original_state.is_checkmate():  # assign winner only if checkmate
                            if original_state.turn == self.original_player:
                                globals()[str(original_state.fen()) +
                                          str(i)].termresult = 0.0
                            else:
                                globals()[str(original_state.fen()) +
                                          str(i)].termresult = 1.0

                    break
                else:
                    i += 1  # increment index if exists

    # **********************************************************************************************************************

    def stockfish_eval(self, board_state):
        # info = self.engine.analyse(board_state, chess.engine.Limit(time=0.01))
        info = self.engine.analyse(board_state, chess.engine.Limit(depth=3))
        if self.original_player:
            try:
                pov_score = int(info["score"].white().__str__())
                if pov_score > 5000:  # set cp limit to 5000 so that mate score takes precedence
                    pov_score = 5000
                score = 1 / (1 + (10 ** -(pov_score / 400)))
                return score  # returns 1 if pov_score > +6382
            except:
                pov_score = info["score"].white().__str__()
                if pov_score[1] == '+':  # mate in x
                    # x * 100 to make a difference when normalizing
                    mate_in = int(pov_score[2:]) * 100
                    # return value close to 1 depending on x
                    score = 1 / (1 + (10 ** -((6382-mate_in) / 400)))
                    return score
                    # return 1.0
                else:
                    # x * 100 to make a difference when normalizing
                    mate_in = int(pov_score[2:]) * 100
                    # return value close to 1 depending on x
                    score = 1 / (1 + (10 ** -((-6382+mate_in) / 400)))
                    return score
                    # return 0.0
        else:
            try:
                pov_score = int(info["score"].black().__str__())
                if pov_score > 5000:  # set cp limit to 5000 so that mate score takes precedence
                    pov_score = 5000
                score = 1 / (1 + (10 ** -(pov_score / 400)))
                return score  # returns 1 if pov_score > +6382
            except:
                pov_score = info["score"].black().__str__()
                if pov_score[1] == '+':  # mate in x
                    # x * 100 to make a difference when normalizing
                    mate_in = int(pov_score[2:]) * 100
                    # return value close to 1 depending on x
                    score = 1 / (1 + (10 ** -((6382-mate_in) / 400)))
                    return score
                    # return 1.0
                else:
                    # x * 100 to make a difference when normalizing
                    mate_in = int(pov_score[2:]) * 100
                    # return value close to 1 depending on x
                    score = 1 / (1 + (10 ** -((-6382+mate_in) / 400)))
                    return score
                    # return 0.0

    # **********************************************************************************************************************

    def minimax(self, depth, board, alpha, beta, is_maximizing):
        if(depth == 0):
            # return -stock_eval(board)
            # return -(Playout.Playout.minimax_eval(board))
            # return -evaluation(board)
            return StaticEval.evaluate_board(board)
        legalMoves = list(board.legal_moves)
        if(is_maximizing):
            bestMove = -9999
            for move in legalMoves:
                # move = chess.Move.from_uci(str(x))
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
            for move in legalMoves:
                # move = chess.Move.from_uci(str(x))
                board.push(move)
                bestMove = min(bestMove, self.minimax(
                    depth - 1, board, alpha, beta, not is_maximizing))
                board.pop()
                beta = min(beta, bestMove)
                if(beta <= alpha):
                    return bestMove
            return bestMove

    # **********************************************************************************************************************

    def run_simulation(self, node):
        # convert fen string back to board object
        board_state = chess.Board(node.state)

        # directed playout with move ordering
        # if self.lock_depth == False:
        #     while(node.children):
        #         # print(len(node.children))
        #         node = node.children[random.randint(0, len(node.children)-1)]
        #         # print(node.weight)
        #         # print('Directed')
        #         board_state.push_san(node.weight)
        #         node.sims += 1
        #         if board_state.is_game_over():
        #             if board_state.is_checkmate():  # assign winner only if checkmate
        #                 if board_state.turn == self.original_player:
        #                     return 0.0
        #                 else:
        #                     return 1.0
        #             return 0.0  # is draw considered a loss for mcts-ept?

        # random playout
        for move in range(self.terminal_depth):
            # if node.children:
            #     # print(len(node.children))
            #     node = node.children[random.randint(0, len(node.children)-1)]
            #     # print(node.weight)
            #     # print('Directed')
            #     board_state.push_san(node.weight)
            # else:
            #     # print('Random')
            #     board_state.push(random.choice(list(board_state.legal_moves)))
            board_state.push(random.choice(list(board_state.legal_moves)))
            if board_state.is_game_over():
                if board_state.is_checkmate():  # assign winner only if checkmate
                    if board_state.turn == self.original_player:
                        return 0.0
                    else:
                        return 1.0
                return 0.0  # is draw considered a loss for mcts-ept?

        # # minimax playout
        # # set maximizing to True if on original player depth
        # if node.depth % 2 == 0:
        #     is_maximizing = False
        # else:
        #     is_maximizing = True
        # # call minimax playout
        # minimax_value = self.minimax(2, board_state, -math.inf,
        #                              math.inf, is_maximizing)

        # score = self.stockfish_eval(board_state)

        stat_eval = StaticEval.evaluate_board(
            board_state)  # use static eval otherwise
        if self.original_player:
            score = 1 / (1 + (10 ** -(stat_eval / 400)))
        else:
            score = 1 / (1 + (10 ** -((-stat_eval) / 400)))

        # if self.lock_depth == True:
        #     # use stockfish when mate score found
        #     score = self.stockfish_eval(board_state)
        # else:
        #     stat_eval = StaticEval.evaluate_board(
        #         board_state)  # use static eval otherwise
        #     if self.original_player:
        #         score = 1 / (1 + (10 ** -(stat_eval / 400)))
        #     else:
        #         score = 1 / (1 + (10 ** -((-stat_eval) / 400)))

        return score

    # **********************************************************************************************************************

    def run_backpropagation(self, node, result):
        node.winsum += result
        node.sims += 1
        while(node.parent):
            node.parent.winsum += result
            node.parent.sims += 1
            node = node.parent

    # **********************************************************************************************************************

    def algo(self, root):
        result = 0.0
        # ran_sim = False
        selected_node = self.run_selection(root)
        end_sim = False
        if(selected_node.sims == 0):

            if selected_node.termnode == False:  # run simulation if it is not terminal
                result = self.run_simulation(
                    selected_node)
                # ran_sim = True  # true if a sim was ran in this iteration
            else:
                result = selected_node.termresult  # return terminal result if it is terminal

        elif(selected_node.termnode == True):  # If terminal node is reselected by UCB1
            result = selected_node.termresult

        # elif(selected_node.sims == (self.calc_seconds*1) or selected_node.sims == (self.calc_seconds*10) or selected_node.sims == (self.calc_seconds*30) or selected_node.sims == (self.calc_seconds*40)):
        #     # expand depth at respective intervals
        #     for node in LevelOrderIter(selected_node):
        #         if selected_node.sims == (self.calc_seconds*1):
        #             if node.depth == 2:
        #                 break
        #             if node.is_leaf:
        #                 self.ordered_expansion(node, 4)
        #         elif selected_node.sims == (self.calc_seconds*10):
        #             if node.depth == 3:
        #                 break
        #             if node.is_leaf:
        #                 self.ordered_expansion(node, 3)
        #         elif selected_node.sims == (self.calc_seconds*30):
        #             if node.depth == 4:
        #                 break
        #             if node.is_leaf:
        #                 self.ordered_expansion(node, 2)
        #         elif selected_node.sims == (self.calc_seconds*40):
        #             if node.depth == 5:
        #                 break
        #             if node.is_leaf:
        #                 self.ordered_expansion(node, 1)
        #     # run sim after expansion
        #     result = self.run_simulation(selected_node)

        # else:
        #     # run sim without expansion when not at intervals
        #     result = self.run_simulation(selected_node)

        else:
            # run expansion if node has been simulated before
            self.run_expansion(selected_node)
            # self.ordered_expansion(selected_node, 5)
            # print(exp)
            selected_node = selected_node.children[0]
            if selected_node.termnode == True:
                result = selected_node.termresult
            else:
                result = self.run_simulation(
                    selected_node)
            # ran_sim = True  # true if a sim was ran in this iteration

        self.run_backpropagation(selected_node, result)
        # if ran_sim:
        #     self.run_backpropagation(selected_node, result)
        return end_sim

    # **********************************************************************************************************************

    def algo_init(self):
        # add root node
        # globals() method returns the dictionary of the current global symbol table
        # used in this scenario to assign node to unique state key
        globals()[str(self.starting_board_state.fen())+str(0)] = MCTSEPT2Node(state=str(
            self.starting_board_state.fen()), key=str(self.starting_board_state.fen())+str(0))

        # check komodo polyglot opening book if move exists
        # with chess.polyglot.open_reader("./OpeningBook/komodo.bin") as reader:
        #     opening_moves = []
        #     for entry in reader.find_all(self.starting_board_state):
        #         opening_moves.append(entry.move)
        #         break
        #         # print(entry.move, entry.weight, entry.learn)
        # if opening_moves:
        #     self.opening_expansion(
        #         globals()[str(self.starting_board_state.fen())+str(0)], opening_moves)
        # else:
        #     # generate legal moves for starting state
        #     self.ordered_expansion(
        #         globals()[str(self.starting_board_state.fen())+str(0)], 8)

        # generate legal moves for starting state
        self.run_expansion(
            globals()[str(self.starting_board_state.fen())+str(0)])
        # self.ordered_expansion(
        #     globals()[str(self.starting_board_state.fen())+str(0)], 8)

        # lock depth to follow mate score
        # mate_info = self.engine.analyse(
        #     self.starting_board_state, chess.engine.Limit(depth=3))
        # if self.original_player:
        #     # if mate_info["score"].white().__str__()[1] == '+':
        #     #     self.terminal_depth = 0
        #     #     self.lock_depth = True
        #     try:
        #         if mate_info["score"].white().__str__()[1] == '+':
        #             self.terminal_depth = 0
        #             self.lock_depth = True
        #         # lock depth when high advantage, extra moves wash out meaning
        #         # elif int(mate_info["score"].white().__str__()) > 2000 and int(mate_info["score"].white().__str__()) > 6382:
        #         #     self.terminal_depth = 0
        #         #     self.lock_depth = True
        #     except:
        #         print(mate_info["score"].white().__str__())
        # else:
        #     if mate_info["score"].black().__str__()[1] == '+':
        #         self.terminal_depth = 0
        #         self.lock_depth = True
        #     # elif int(mate_info["score"].black().__str__()) > 2000 and int(mate_info["score"].black().__str__()) > 6382:
        #     #     self.terminal_depth = 0
        #     #     self.lock_depth = True

        return globals()[str(self.starting_board_state.fen())+str(0)]

    # **********************************************************************************************************************

    def algo_render(self):
        # self.engine.quit()

        # print("\n")
        # for pre, _, node in RenderTree(globals()[str(self.starting_board_state.fen())+str(0)]):
        #     treestr = u"%s%s" % (pre, node.weight)
        #     print(treestr.ljust(8), round(node.winsum, 2),
        #           node.sims, round(node.score, 2))
        # print("\n")

        print("Total Wins/Simulations: " + str(globals()
                                               [str(self.starting_board_state.fen())+str(0)].winsum) + "/" + str(globals()[str(self.starting_board_state.fen())+str(0)].sims))
        print("Total Win Probablity: " +
              str(round(globals()[str(self.starting_board_state.fen())+str(0)].score*100, 2)) + "%")
        print("\n")

        weight_list = []
        winsim_list = []
        score_list = []
        tie_list = []  # for best moves that have tied scores
        best_score = -math.inf
        best_move = "invalid move"

        # find highest score in children
        for child in globals()[str(self.starting_board_state.fen())+str(0)].children:
            print(str(child.weight) + ": " +
                  str(round(child.score*100, 2)) + "% Win Rate")
            weight_list.append(child.weight)
            winsim_list.append(
                str(round(child.winsum, 2)) + '/' + str(child.sims))
            score_list.append(round(child.score*100, 2))
            if child.score > best_score:
                best_score = child.score

        # append weights of children with highest scores
        for child in globals()[str(self.starting_board_state.fen())+str(0)].children:
            if child.score == best_score:
                tie_list.append(child.weight)

        print("\nBest Move List: ")
        print(tie_list)
        best_move = random.choice(tie_list)  # random move from highest scores

        print("\n")
        print("Best Move: " + str(best_move))
        print("\n")

        self.json_export()

        # for line in DotExporter(globals()[str(self.starting_board_state.fen())+str(0)]):
        #     print(line)

        # dot_export = UniqueDotExporter(
        #     globals()[str(self.starting_board_state.fen())+str(0)], nodenamefunc=self.nodenamefunc, nodeattrfunc=self.nodeattrfunc, edgeattrfunc=self.edgeattrfunc)

        # dot_export = UniqueDotExporter(
        #     globals()[str(self.starting_board_state.fen())+str(0)], nodeattrfunc=lambda n: 'label="%s"' % (n.id))

        # DotExporter(globals()[str(self.starting_board_state.fen())+str(0)]).to_dotfile(
        #     "tree.dot")

        delete_list = []
        for element in globals():
            if element.startswith('r'):
                if not (element.startswith(str(self.starting_board_state.fen())+str(0)) or element.startswith('ra')):
                    delete_list.append(element)
        for element in delete_list:
            del globals()[element]

        return best_move, weight_list, winsim_list, score_list, round(globals()[str(self.starting_board_state.fen())+str(0)].winsum, 2), globals()[str(self.starting_board_state.fen())+str(0)].sims

    def json_export(self):
        exporter = JsonExporter(
            indent=2, sort_keys=True, dictexporter=None)
        filename = "tree.json"
        filehandle = open(filename, 'w')
        filehandle.write(exporter.export(
            globals()[str(self.starting_board_state.fen())+str(0)]))
