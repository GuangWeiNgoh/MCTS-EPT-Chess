# MCTS
from __future__ import division

import chess
import chess.engine
# import chess.svg
# import chess.pgn
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
from MCTS_EPT_Node_2 import MCTSEPT2Node
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
        self.C = kwargs.get('C', 1.4)  # UCT exploration constant
        self.root_C = kwargs.get('root_C', 8.4)
        self.original_player = kwargs.get('player', None)
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish.exe")

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
        # check if current is leaf node
        # else select child that maximizes UCB1
        # while (node.children):  # traverse down until no children left (leaf node)
        while not(node.is_leaf):
            if node.depth == 0:  # use root_C for selection from root node
                c_value = self.root_C
            else:
                c_value = self.C

            if node.sims == 0:  # only for root node
                node = node.children[0]
            else:
                max_uct = -math.inf
                uct_score = -math.inf
                log_value = log(node.sims)
                for each in node.children:
                    # print(c_value)
                    if each.sims == 0:
                        uct_score = math.inf
                    else:
                        uct_score = ((each.score) + (c_value *
                                                     sqrt(log_value/each.sims)))
                        # uct_score = ((each.score) + (self.C *
                        #                              sqrt(log_value/each.sims)))
                    if uct_score > max_uct:
                        max_uct = uct_score
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
                    globals()[str(original_state.fen())+str(i)] = MCTSEPT2Node(state=str(original_state.fen()),
                                                                               advs=0, sims=0, key=str(original_state.fen())+str(i), parent=globals()[node.key], weight=board_state.san(move))

                    # For case where node is expanded and new node is terminal node
                    if original_state.is_game_over():  # check if it is a terminal node
                        globals()[str(original_state.fen())+str(i)
                                  ].termnode = True  # set as terminal node
                        # set terminal result to false if draw or loss
                        globals()[str(original_state.fen()) +
                                  str(i)].termresult = False
                        if original_state.is_checkmate():  # assign winner only if checkmate
                            if original_state.turn == self.original_player:
                                globals()[str(original_state.fen()) +
                                          str(i)].termresult = False
                            else:
                                globals()[str(original_state.fen()) +
                                          str(i)].termresult = True

                    break
                else:
                    i += 1  # increment index if exists

    # **********************************************************************************************************************

    def run_simulation(self, node):
        # convert fen string back to board object
        board_state = chess.Board(node.state)
        for move in range(self.terminal_depth):

            board_state.push(random.choice(list(board_state.legal_moves)))
            # try:
            #     make = random.choice(list(board_state.legal_moves))
            #     board_state.push(make)

            # except:
            #     print('Illegal move during simulation')
            #     print(board_state)
            #     print(node.advs)
            #     print(node.sims)
            #     while(node.parent):
            #         print(node.weight)
            #         node = node.parent
            #     print(make)

            if board_state.is_game_over():

                if board_state.is_checkmate():  # assign winner only if checkmate
                    if board_state.turn == self.original_player:
                        return False  # is draw considered a loss for mcts-ept?
                    else:
                        return True
                return False
                # break

        info = self.engine.analyse(board_state, chess.engine.Limit(time=0.01))
        if self.original_player:
            try:
                pov_score = int(info["score"].white().__str__())
                if pov_score > 0:
                    return True
                else:
                    return False
            except:
                pov_score = info["score"].white().__str__()
                if pov_score[1] == '+':
                    return True
                else:
                    return False
        else:
            try:
                pov_score = int(info["score"].black().__str__())
                if pov_score > 0:
                    return True
                else:
                    return False
            except:
                pov_score = info["score"].black().__str__()
                if pov_score[1] == '+':
                    return True
                else:
                    return False

    # **********************************************************************************************************************

    def run_backpropagation(self, node, result):
        if result:  # update simulated node and all parents with 1/1 if win
            node.advs += 1
            node.sims += 1
            while(node.parent):
                node.parent.advs += 1
                node.parent.sims += 1
                node = node.parent
        else:  # update simulated node and all parents with 0/1 if lose
            node.advs += 0
            node.sims += 1
            while(node.parent):
                node.parent.advs += 0
                node.parent.sims += 1
                node = node.parent

    # **********************************************************************************************************************

    def algo(self, root):
        result = False
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

        elif(selected_node.termnode == True):  # If terminal node is reselected by UCT
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
        globals()[str(self.starting_board_state.fen())+str(0)] = MCTSEPT2Node(state=str(self.starting_board_state.fen()),
                                                                              advs=0, sims=0, key=str(self.starting_board_state.fen())+str(0))

        # generate legal moves for starting state
        self.run_expansion(
            globals()[str(self.starting_board_state.fen())+str(0)])
        # move_list = list(self.starting_board_state.legal_moves)

        # for move in move_list:  # add all legal move nodes to tree
        #     original_state = self.starting_board_state.copy()
        #     # original_state.push_san(move)
        #     original_state.push(move)
        #     globals()[str(original_state.fen())+str(0)] = MCTSEPTNode(state=str(original_state.fen()),
        #                                                               advs=0, sims=0, key=str(original_state.fen())+str(0), parent=globals()[str(self.starting_board_state.fen())+str(0)], weight=self.starting_board_state.san(move))

        return globals()[str(self.starting_board_state.fen())+str(0)]

    # **********************************************************************************************************************

    def algo_render(self):
        # self.engine.quit()

        # print("\n")
        # for pre, _, node in RenderTree(globals()[str(self.starting_board_state.fen())+str(0)]):
        #     treestr = u"%s%s" % (pre, node.weight)
        #     print(treestr.ljust(8), node.advs, node.sims, node.score)
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
                  str(round(child.score*100, 2)) + "% Advantage")
            weight_list.append(child.weight)
            winsim_list.append(str(child.advs) + '/' + str(child.sims))
            score_list.append(round(child.score*100, 2))
            if child.score > best_score:
                best_score = child.score
                # best_move = child.weight

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

        return best_move, weight_list, winsim_list, score_list, globals()[str(self.starting_board_state.fen())+str(0)].advs, globals()[str(self.starting_board_state.fen())+str(0)].sims

    def json_export(self):
        exporter = JsonExporter(
            indent=2, sort_keys=True, dictexporter=None)
        filename = "tree.json"
        filehandle = open(filename, 'w')
        filehandle.write(exporter.export(
            globals()[str(self.starting_board_state.fen())+str(0)]))
