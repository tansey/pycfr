from itertools import combinations
from itertools import permutations
from collections import Counter
import random

CHANCE_PLAYER = -1

def overlap(t1, t2):
    for x in t1:
        if x in t2:
            return True
    return False

def all_unique(hc):
    for i in range(len(hc)-1):
        for j in range(i+1,len(hc)):
            if overlap(hc[i], hc[j]):
                return False
    return True


class GameTree(object):
    def __init__(self, players, deck, holecards, rounds, ante, blinds, history_format = '{holecards}:{boardcards}:{bets}'):
        assert(players >= 2)
        assert(ante >= 0)
        assert(rounds != None)
        assert(deck != None)
        assert(len(rounds) > 0)
        assert(len(deck) > 1)
        if blinds != None:
            if type(blinds) is int or type(blinds) is float:
                blinds = [blinds]
        self.players = players
        self.deck = deck
        self.holecards = holecards
        self.rounds = rounds
        self.ante = ante
        self.blinds = blinds
        self.history_format = history_format

    def build(self):
        # Assume everyone is in
        players_in = [True] * self.players
        # Collect antes
        committed = [self.ante] * self.players
        self.next_player = 0
        # Collect blinds
        if self.blinds != None:
            for blind in blinds:
                committed[self.next_player] += blind
                self.next_player = (self.next_player + 1) % self.players
        holes = [[]] * self.players
        board = []
        self.root = HolecardChanceNode(None, committed, holes, board, deck)
        # Deal holecards
        all_hc = self.holecard_distributions()
        # Create a child node for every possible distribution
        for hc in all_hc:
            cur_holes = hc
            f = ()
            for c in cur_holes:
                f = f + c
            cur_deck = filter(lambda x: not (x in f), self.deck)
            self.build_rounds(self.root, players_in, committed, cur_holes, board, cur_deck, 0)

    def deal_holecards(self):
        a = combinations(self.deck, self.holecards)
        return filter(lambda x: all_unique(x), permutations(a, self.players))

    def build_rounds(self, root, players_in, committed, holes, board, deck, round_idx):
        if round_idx == len(self.roundinfo):
            # showdown
            return
        cur_round = self.roundinfo[round_idx]
        if cur_round.boardcards != None and len(cur_round.boardcards) > 0:
            deal_boardcards(root, players_in, committed, holes, board, deck, round_idx)
        else:
            build_bets(root, players_in, committed, holes, board, deck, round_idx)

    def deal_boardcards(self, root, players_in, committed, holes, board, deck, round_idx):
        cur_round = self.roundinfo[round_idx]
        bnode = BoardcardChanceNode(root, committed, holes, board, deck, cur_round.boardcards)
        all_bc = combinations(deck, cur_round.boardcards)
        for bc in all_bc:
            cur_board = board + bc
            cur_deck = filter(lambda x: not (x in bc), deck)
            self.build_bets(self, bnode, players_in, committed, holes, cur_board, cur_deck, round_idx)

    def build_bets(self, root, players_in, committed, holes, board, deck, round_idx):
        self.build_rounds(root, players_in, committed, holes, board, deck, round_idx+1)

    def holecard_distributions(self):
        x = Counter(combinations(self.deck, self.holecards))
        d = float(sum(x.values()))
        return zip(x.keys(),[y / d for y in x.values()])
        
class RoundInfo(object):
    def __init__(self, boardcards, betsize, maxbets):
        self.boardcards = boardcards
        self.betsize = betsize
        self.maxbets = maxbets

class Node(object):
    def __init__(self, parent, committed, holecards, board, deck):
        self.committed = deepcopy(committed)
        self.holecards = deepcopy(holecards)
        self.board = deepcopy(board)
        self.deck = deepcopy(deck)
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
    def __init__(self, parent, committed, holecards, board, deck, payoffs):
        Node.__init__(self, parent, committed, holecards, board, deck)
        self.payoffs = payoffs

class HolecardChanceNode(Node):
    def __init__(self, parent, committed, holecards, board, deck, player, todeal):
        Node.__init__(self, parent, committed, holecards, board, deck)
        self.player = player
        self.todeal = todeal
        self.children = []

class BoardcardChanceNode(Node):
    def __init__(self, parent, committed, holecards, board, deck, todeal):
        Node.__init__(self, parent, committed, holecards, board, deck)
        self.todeal = todeal
        self.children = []        

class ActionNode(Node):
    def __init__(self, parent, committed, holecards, board, deck, player, roundinfo):
        Node.__init__(self, parent, committed, holecards, board, deck)
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