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
from copy import deepcopy
# from treelib import Node, Tree
# from graphviz import Digraph
from MCTS_EPT_2_Node import MCTSEPT2Node
from anytree import NodeMixin, RenderTree
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
        print("******* MCTS-EPT Object Created *******")
        print("\n")
        self.starting_board_state = board.copy()
        seconds = kwargs.get('time', 30)  # default set at 30 seconds
        # converts seconds into mm:ss format
        self.calc_time = datetime.timedelta(seconds=seconds)
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
        print("EPT 2")

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

    def run_selection(self, node):
        if self.lock_depth == True:
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
                        # ucb_score = ((each.score) + (c_value *
                        #                              sqrt((2*log_value)/each.sims)))
                        ucb_score = ((each.score) + (c_value *
                                                     sqrt(log_value/each.sims)))
                    if ucb_score > max_ucb:
                        max_ucb = ucb_score
                        node = each
        else:
            # select child that maximizes UCB1
            # traverse down until no children left (leaf node)
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
                            # ucb_score = ((each.score) + (c_value *
                            #                              sqrt((2*log_value)/each.sims)))
                            ucb_score = ((each.score) + (c_value *
                                                         sqrt(log_value/each.sims)))
                        if ucb_score > max_ucb:
                            max_ucb = ucb_score
                            node = each
        return node

    # **********************************************************************************************************************

    def run_expansion(self, node):
        board_state = chess.Board(node.state)

        # move_list = self.get_move_list(board_state)
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

    def run_simulation(self, node):
        # convert fen string back to board object
        board_state = chess.Board(node.state)

        for move in range(self.terminal_depth):

            board_state.push(random.choice(list(board_state.legal_moves)))

            if board_state.is_game_over():

                if board_state.is_checkmate():  # assign winner only if checkmate
                    if board_state.turn == self.original_player:
                        return 0.0
                    else:
                        return 1.0
                return 0.0  # is draw considered a loss for mcts-ept?

        info = self.engine.analyse(board_state, chess.engine.Limit(time=0.01))
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

        else:
            # run expansion if node has been simulated before
            self.run_expansion(selected_node)
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
        with chess.polyglot.open_reader("./OpeningBook/komodo.bin") as reader:
            opening_moves = []
            for entry in reader.find_all(self.starting_board_state):
                opening_moves.append(entry.move)
                # print(entry.move, entry.weight, entry.learn)
        if opening_moves:
            self.opening_expansion(
                globals()[str(self.starting_board_state.fen())+str(0)], opening_moves)
        else:
            # generate legal moves for starting state
            self.run_expansion(
                globals()[str(self.starting_board_state.fen())+str(0)])

        # # generate legal moves for starting state
        # self.run_expansion(
        #     globals()[str(self.starting_board_state.fen())+str(0)])

        mate_info = self.engine.analyse(
            self.starting_board_state, chess.engine.Limit(time=0.01))
        if self.original_player:
            # if mate_info["score"].white().__str__()[1] == '+':
            #     self.terminal_depth = 0
            #     self.lock_depth = True
            try:
                if mate_info["score"].white().__str__()[1] == '+':
                    self.terminal_depth = 0
                    self.lock_depth = True
            except:
                print(mate_info["score"].white().__str__())
        else:
            if mate_info["score"].black().__str__()[1] == '+':
                self.terminal_depth = 0
                self.lock_depth = True

        # print(mate_info["score"].white().__str__())
        # print(self.terminal_depth)

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

        # print("Total Advantages/Simulations: " + str(globals()
        #                                        [str(self.starting_board_state.fen())+str(0)].advs) + "/" + str(globals()[str(self.starting_board_state.fen())+str(0)].sims))
        # print("Total Win Rate: " +
        #       str(round(globals()[str(self.starting_board_state.fen())+str(0)].score*100, 2)) + "%")
        # print("\n")

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
