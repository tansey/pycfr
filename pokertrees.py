from itertools import combinations
from collections import Counter
import random

CHANCE_PLAYER = -1

class GameTree(object):
    def __init__(self, players, deck, holecards, rounds, ante, blinds, history_format = '{holecards}:{boardcards}:{bets}'):
        assert(players >= 2)
        assert(ante >= 0)
        assert(rounds != None)
        assert(deck != None)
        assert(len(rounds) > 0)
        assert(len(deck) > 1)
        self.players = players
        self.deck = deck
        self.holecards = holecards
        self.rounds = rounds
        self.ante = ante
        self.blinds = blinds
        self.history_format = history_format

    def build(self):
        hc = self.holecard_distributions()
        pot = self.ante * self.players
        self.root = ChanceNode(None, hc)

    def holecard_distributions(self):
        x = Counter(combinations(self.deck, self.holecards))
        d = float(sum(x.values()))
        return zip(x.keys(),[y / d for y in x.values()])
        
class RoundInfo(object):
    def __init__(self, boardcards, betsize, maxbets):
        self.boardcards = boardcards,
        self.betsize = betsize
        self.maxbets = maxbets

class Node(object):
    def __init__(self, parent):
        if parent:
            self.parent = parent
            self.parent.add_child(self)

    def all_but_one_folded(self, players_in):
        return len(filter(lambda x: x,players_in)) == 1

    def all_checked(self, players_in, bets):
        return len(history) == len(players_in) and max(bets) == 0

    def all_called_last_raisor_or_folded(self, players_in, bets):
        betlevel = max(bets)
        for i in enumerate(bets):
            if players_in[i] and bets[i] < betlevel:
                return False
        return True

    def add_child(self, child):
        if self.children is None:
            self.children = [child]
        else:
            self.children.append(child)

class TerminalNode(Node):
    def __init__(self, parent, payoffs):
        Node.__init__(self, parent)
        self.payoffs = payoffs

class HolecardChanceNode(Node):
    def __init__(self, parent, committed, holecards, board, deck, player, todeal):
        Node.__init__(self, parent)
        self.committed = deepcopy(committed)
        self.holecards = deepcopy(holecards)
        self.board = deepcopy(board)
        self.deck = deepcopy(deck)
        self.player = player
        self.children = []

class ActionNode(Node):
    def __init__(self, parent, committed, holecards, board, deck, player, roundinfo):
        Node.__init__(self, parent)
        self.committed = deepcopy(committed)
        self.holecards = deepcopy(holecards)
        self.board = deepcopy(board)
        self.deck = deepcopy(deck)
        self.player = player
        self.children = []
        if committed[player] < max(committed):
            self.add_fold_child()
        self.add_call_child(roundinfo)
        if roundinfo.maxbets[player] * roundinfo.betsize > committed[player]:
            self.add_raise_child(roundinfo)

    def add_fold_child(self):
        pass

    def add_call_child(self, roundinfo):
        pass

    def add_raise_child(self, roundinfo):
        pass

class PlayerTree(GameTree):
    def __init__(self, player, players, deck, holecards, rounds, ante, blinds, history_format = '{holecards}:{boardcards}:{bets}'):
        GameTree.__init__(self, players, deck, holecards, rounds, ante, blinds, history_format)
        self.player = player

    def build(self):
        pass

class OpponentNode(Node):
    def __init__(self, parent, opponent):
        Node.__init__(self, parent)
        self.opponent = opponent