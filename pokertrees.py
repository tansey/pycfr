from itertools import combinations
from itertools import permutations
from collections import Counter
from card import Card
from hand_evaluator import HandEvaluator

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
            self.showdown(root, players_in, committed, holes, board, deck)
            return
        cur_round = self.roundinfo[round_idx]
        if cur_round.boardcards != None and len(cur_round.boardcards) > 0:
            self.deal_boardcards(root, players_in, committed, holes, board, deck, round_idx)
        else:
            self.build_bets(root, players_in, committed, holes, board, deck, round_idx)

    def deal_boardcards(self, root, players_in, committed, holes, board, deck, round_idx):
        cur_round = self.roundinfo[round_idx]
        bnode = BoardcardChanceNode(root, committed, holes, board, deck, cur_round.boardcards)
        all_bc = combinations(deck, cur_round.boardcards)
        for bc in all_bc:
            cur_board = board + bc
            cur_deck = filter(lambda x: not (x in bc), deck)
            self.build_bets(self, bnode, players_in, committed, holes, cur_board, cur_deck, round_idx)

    def build_bets(self, root, players_in, committed, holes, board, deck, round_idx, min_actions_this_round, actions_this_round, bets_this_round):
        if actions_this_round >= min_actions_this_round:
            # if everyone else folded, end the hand
            if players_in.count(True) == 1:
                self.showdown(root, players_in, committed, holes, board, deck)
                return
            # if everyone checked or the last raisor has been called, end the round
            if self.all_called_last_raisor_or_folded(players_in, bets_this_round):
                build_rounds(root, players_in, committed, holes, board, deck, round_idx + 1)
                return
        cur_round = self.roundinfo[round_idx]
        anode = ActionNode(root, committed, holecards, board, deck, self.next_player)
        self.next_player = (self.next_player + 1) % self.players
        if committed[anode.player] < max(committed):
            self.add_fold_child(root, players_in, committed, holes, board, deck, round_idx, min_actions_this_round, actions_this_round, bets_this_round)
        self.add_call_child(root, players_in, committed, holes, board, deck, round_idx, min_actions_this_round, actions_this_round, bets_this_round)
        if cur_round.maxbets[anode.player] > max(bets):
            self.add_raise_child(root, players_in, committed, holes, board, deck, round_idx, min_actions_this_round, actions_this_round, bets_this_round)

    def all_called_last_raisor_or_folded(self, players_in, bets):
        betlevel = max(bets)
        for i in enumerate(bets):
            if players_in[i] and bets[i] < betlevel:
                return False
        return True

    def add_fold_child(self, root, players_in, committed, holes, board, deck, round_idx, min_actions_this_round, actions_this_round, bets_this_round):
        players_in[root.player] = False
        self.build_bets(root, players_in, committed, holes, board, deck, round_idx, min_actions_this_round, actions_this_round, bets_this_round)
        players_in[root.player] = True

    def add_call_child(self, root, players_in, committed, holes, board, deck, round_idx, min_actions_this_round, actions_this_round, bets_this_round):
        player_commit = committed[root.player]
        committed[root.player] = max(committed)
        self.build_bets(root, players_in, committed, holes, board, deck, round_idx, min_actions_this_round, actions_this_round, bets_this_round)
        committed[root.player] = player_commit

    def add_raise_child(self, root, players_in, committed, holes, board, deck, round_idx, min_actions_this_round, actions_this_round, bets_this_round):
        cur_round = self.roundinfo(cur_round)
        prev_betlevel = bets[root.player]
        prev_commit = committed[root.player]
        bets[root.player] = max(bets) + 1
        committed[root.player] += (bets[root.player] - prev_betlevel) * cur_round.betsize
        self.build_bets(root, players_in, committed, holes, board, deck, round_idx, min_actions_this_round, actions_this_round, bets_this_round)
        bets[root.player] = prev_betlevel
        committed[root.player] = prev_commit

    def showdown(self, root, players_in, committed, holes, board, deck):
        scores = [HandEvaluator.evaluate_hand(hc, board) for hc in holes]
        winners = []
        maxscore = -1
        for i,s in enumerate(scores):
            if players_in[i]:
                if len(winners) == 0 or s > maxscore:
                    maxscore = s
                    winners = [i]
                elif s == maxscore:
                    winners.append(i)
        pot = sum(committed)
        payoff = pot / float(len(winners))
        payoffs = [-x for x in committed]
        for w in winners:
            payoffs[w] += payoff
        TerminalNode(root, committed, holecards, board, deck, payoffs)

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
    def __init__(self, parent, committed, holecards, board, deck, player):
        Node.__init__(self, parent, committed, holecards, board, deck)
        self.player = player
        self.children = []

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