# MCTS
from __future__ import division

import chess
# import chess.engine
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
from MCTS_Node import MCTSNode
from anytree import NodeMixin, RenderTree
from pprint import pprint
from collections import OrderedDict
from anytree.exporter import DictExporter
from anytree.exporter import JsonExporter
from anytree.exporter import DotExporter
from anytree.exporter import UniqueDotExporter
from anytree.importer import JsonImporter
from math import log, sqrt


class MCTS(object):

    def __init__(self, board, **kwargs):
        # Takes an instance of a Board and optionally some keyword
        # arguments.  Initializes the list of game states and the
        # statistics tables.
        # pass
        print("\n")
        print("******* MCTS Object Created *******")
        print("\n")
        self.starting_board_state = board.copy()
        seconds = kwargs.get('time', 30)  # default set at 30 seconds
        # converts seconds into mm:ss format
        self.calc_time = datetime.timedelta(seconds=seconds)
        print("Calculation time: " + str(self.calc_time))
        print("\n")
        self.max_moves = kwargs.get('max_moves', 100)
        print("Maximum moves: " + str(self.max_moves))
        print("\n")
        self.C = kwargs.get('C', 1.4)  # UCT exploration constant
        self.original_player = kwargs.get('player', None)

    # **********************************************************************************************************************

    def create_tree(self):

        d0 = MCTSNode(state=str(self.starting_board_state.fen()),
                      wins=1, sims=3)
        # parent_state = self.starting_board_state.copy()
        self.starting_board_state.push_san("e4")
        d1n1 = MCTSNode(state=str(self.starting_board_state.fen()),
                        wins=0, sims=1, parent=d0)
        self.starting_board_state.push_san("e5")
        d1n2 = MCTSNode(state=str(self.starting_board_state.fen()),
                        wins=1, sims=2, parent=d0)
        self.starting_board_state.push_san("Qh5")
        d2n1 = MCTSNode(state=str(self.starting_board_state.fen()),
                        wins=1, sims=1, parent=d1n2)
        # d1n2.sims = 3
        print(RenderTree(d0))
        print("\n")

        # backpropagation function
        sim_node = d2n1
        while(sim_node.parent):
            sim_node.parent.wins += 1
            sim_node.parent.sims += 1
            sim_node = sim_node.parent

        for pre, _, node in RenderTree(d0):
            treestr = u"%s%s" % (pre, node.score)
            print(treestr.ljust(8), node.wins, node.sims)
        print("\n")
        # exporter = DictExporter(dictcls=OrderedDict, attriter=sorted)
        # pprint(exporter.export(d0))
        # print("\n")
        exporter = JsonExporter(indent=2, sort_keys=True)
        # print(exporter.export(d0))
        filename = "test.json"
        filehandle = open(filename, 'w')
        filehandle.write(exporter.export(d0))

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

    # def nodenamefunc(self, node):
    #     return '%s:%s' % (node.name, node.depth)

    # def nodeattrfunc(self, node):
    #     return '%s:%s' % (node.wins, node.sims)

    # def edgeattrfunc(self, node, child):
    #     return child.weight

    # **********************************************************************************************************************

    def get_move_list(self, board):
        # convert legal moves to str type
        legal_moves = str(board.legal_moves)
        legal_moves = legal_moves.replace(" ", "")  # removes spaces

        # find start and end indexes of brackets
        start = legal_moves.find("(") + 1
        end = legal_moves.find(")")
        # extract moves from legal_moves string
        legal_moves_sub = legal_moves[start:end]

        # seperate moves by comma and store into list
        legal_move_list = legal_moves_sub.split(",")
        # print(legal_move_list)
        # print("\n")

        return legal_move_list

    # **********************************************************************************************************************

    def random_legal_move(self, move_list):
        # select random move to make from list of legal moves
        random_move = random.choice(move_list)
        # print(random_move)
        # print("\n")
        return random_move  # returns random legal move

    # **********************************************************************************************************************

    def run_selection(self, node):
        # check if current is leaf node
        # else select child that maximizes UCB1
        # while (node.children):  # traverse down until no children left (leaf node)
        while not(node.is_leaf):
            # node = node.children[0]
            if node.sims == 0:  # only for root node
                node = node.children[0]
            else:
                max_uct = -math.inf
                uct_score = -math.inf
                log_value = log(node.sims)
                # if node.children == []:
                #     print("empty")
                for each in node.children:
                    if each.sims == 0:
                        uct_score = math.inf
                    else:
                        uct_score = ((each.score) + (self.C *
                                                     sqrt(log_value/each.sims)))
                    if uct_score > max_uct:
                        max_uct = uct_score
                        node = each

                    # if max_uct == -math.inf:
                    #     board_state = chess.Board(node.state)
                    #     print(board_state)
                    #     print(board_state.is_game_over())
                    #     print(board_state.legal_moves)
                    #     print("new")
                    # else:
                    #     try:
                    #         node = node.children[0]
                    #     except:
                    #         board_state = chess.Board(node.state)
                    #         print(board_state)
                    #         print(board_state.is_game_over())
                    #         print(board_state.legal_moves)

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
                    globals()[str(original_state.fen())+str(i)] = MCTSNode(state=str(original_state.fen()),
                                                                           wins=0, sims=0, key=str(original_state.fen())+str(i), parent=globals()[node.key], weight=board_state.san(move))

                    # For case where node is expanded and new node is terminal node
                    if original_state.is_game_over():  # check if it is a terminal node
                        globals()[str(original_state.fen())+str(i)
                                  ].termnode = True  # set as terminal node
                        if original_state.is_checkmate():  # assign winner only if checkmate
                            if original_state.turn == self.original_player:
                                globals()[str(original_state.fen()) +
                                          str(i)].termresult = False
                            else:
                                globals()[str(original_state.fen()) +
                                          str(i)].termresult = True
                        else:
                            # set terminal result to false if draw
                            globals()[str(original_state.fen()) +
                                      str(i)].termresult = False

                    break
                else:
                    i += 1  # increment index if exists

    # **********************************************************************************************************************

    def run_simulation(self, node):
        # convert fen string back to board object
        board_state = chess.Board(node.state)
        # print(node.weight)
        # print(board_state)
        for move in range(self.max_moves):
            # move_list = self.get_move_list(board_state)
            # make_move = self.random_legal_move(move_list)

            # board_state.push_san(make_move)

            board_state.push(random.choice(list(board_state.legal_moves)))

            # winner = "UNKNOWN"
            if board_state.is_game_over():

                if board_state.is_checkmate():  # assign winner only if checkmate
                    if board_state.turn == self.original_player:
                        return False
                    else:
                        return True

                    # if winner == self.original_player:  # if winner is the original player, return true
                    #     return True
                    # else:
                    #     return False
                break
        return False

    # **********************************************************************************************************************

    def run_backpropagation(self, node, result):
        if result:  # update simulated node and all parents with 1/1 if win
            node.wins += 1
            node.sims += 1
            while(node.parent):
                node.parent.wins += 1
                node.parent.sims += 1
                node = node.parent
        else:  # update simulated node and all parents with 0/1 if lose
            node.wins += 0
            node.sims += 1
            while(node.parent):
                node.parent.wins += 0
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
                result = self.run_simulation(selected_node)
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
                result = self.run_simulation(selected_node)
            # ran_sim = True  # true if a sim was ran in this iteration

        # print(selected_node.weight)
        # print(selected_node.termnode)
        # print(selected_node.termresult)

        self.run_backpropagation(selected_node, result)
        # if ran_sim:
        #     self.run_backpropagation(selected_node, result)
        return end_sim

    # **********************************************************************************************************************

    def algo_init(self):
        # add root node
        # globals() method returns the dictionary of the current global symbol table
        # used in this scenario to assign node to unique state key
        globals()[str(self.starting_board_state.fen())+str(0)] = MCTSNode(state=str(self.starting_board_state.fen()),
                                                                          wins=0, sims=0, key=str(self.starting_board_state.fen())+str(0))

        # generate legal moves for starting state
        self.run_expansion(
            globals()[str(self.starting_board_state.fen())+str(0)])

        # move_list = list(self.starting_board_state.legal_moves)

        # for move in move_list:  # add all legal move nodes to tree
        #     original_state = self.starting_board_state.copy()
        #     # original_state.push_san(move)
        #     original_state.push(move)
        #     globals()[str(original_state.fen())+str(0)] = MCTSNode(state=str(original_state.fen()),
        #                                                            wins=0, sims=0, key=str(original_state.fen())+str(0), parent=globals()[str(self.starting_board_state.fen())+str(0)], weight=self.starting_board_state.san(move))

        return globals()[str(self.starting_board_state.fen())+str(0)]

    # **********************************************************************************************************************

    def algo_render(self):
        # print("\n")
        # for pre, _, node in RenderTree(globals()[str(self.starting_board_state.fen())+str(0)]):
        #     treestr = u"%s%s" % (pre, node.weight)
        #     print(treestr.ljust(8), node.wins, node.sims, node.score)
        # print("\n")

        # print("Total Wins/Simulations: " + str(globals()
        #                                        [str(self.starting_board_state.fen())+str(0)].wins) + "/" + str(globals()[str(self.starting_board_state.fen())+str(0)].sims))
        # print("Total Win Rate: " +
        #       str(round(globals()[str(self.starting_board_state.fen())+str(0)].score*100, 2)) + "%")
        # print("\n")

        weight_list = []
        winsim_list = []
        score_list = []
        best_score = -math.inf
        best_move = "invalid move"
        for child in globals()[str(self.starting_board_state.fen())+str(0)].children:
            print(str(child.weight) + ": " +
                  str(round(child.score*100, 2)) + "% Win Rate")
            weight_list.append(child.weight)
            winsim_list.append(str(child.wins) + '/' + str(child.sims))
            score_list.append(round(child.score*100, 2))
            if child.score > best_score:
                best_score = child.score
                best_move = child.weight
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

        return best_move, weight_list, winsim_list, score_list, globals()[str(self.starting_board_state.fen())+str(0)].wins, globals()[str(self.starting_board_state.fen())+str(0)].sims

    def json_export(self):
        exporter = JsonExporter(
            indent=2, sort_keys=True, dictexporter=None)
        filename = "tree.json"
        filehandle = open(filename, 'w')
        filehandle.write(exporter.export(
            globals()[str(self.starting_board_state.fen())+str(0)]))

    def algo_iter(self):

        # determine whose turn it is in the starting state
        if self.starting_board_state.turn:
            player = "WHITE"
        else:
            player = "BLACK"

        start_time = datetime.datetime.utcnow()  # current time
        while datetime.datetime.utcnow() - start_time < self.calc_time:
            # run simulation until allowed time is reached
            end_sim = self.mcts(
                globals()[str(self.starting_board_state.fen())+str(0)], player)
            if end_sim:
                break
