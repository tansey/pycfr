from itertools import combinations
from itertools import permutations
from collections import Counter
from card import Card
from hand_evaluator import HandEvaluator
from copy import deepcopy

CHANCE_PLAYER = -1
FOLD = 0
CALL = 1
RAISE = 2

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

def evaluate_twocard_hand(hand):
    if hand[0].rank == hand[1].rank:
        return 15*14+hand[0].rank
    return max(hand[0].rank, hand[1].rank) * 14 + min(hand[0].rank, hand[1].rank)

class RoundInfo(object):
    def __init__(self, boardcards, betsize, maxbets):
        self.boardcards = boardcards
        self.betsize = betsize
        self.maxbets = maxbets

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
        for r in rounds:
            assert(len(r.maxbets) == players)
        self.players = players
        self.deck = deck
        self.holecards = holecards
        self.roundinfo = rounds
        self.ante = ante
        self.blinds = blinds
        self.history_format = history_format
        self.information_sets = {}

    def build(self):
        # Assume everyone is in
        players_in = [True] * self.players
        # Collect antes
        committed = [self.ante] * self.players
        next_player = 0
        bets = [0] * self.players
        # Collect blinds
        if self.blinds != None:
            for blind in self.blinds:
                committed[next_player] += blind
                bets[next_player] = int((committed[next_player] - self.ante) / self.roundinfo[0].betsize)
                next_player = (next_player + 1) % self.players
        holes = [[]] * self.players
        board = ()
        self.root = HolecardChanceNode(None, committed, holes, board, self.deck, "", self.holecards)
        # Deal holecards
        all_hc = self.deal_holecards()
        # Create a child node for every possible distribution
        for hc in all_hc:
            cur_holes = hc
            f = ()
            for c in cur_holes:
                f = f + c
            cur_deck = filter(lambda x: not (x in f), self.deck)
            self.build_rounds(self.root, players_in, committed, cur_holes, board, cur_deck, "", 0, bets, next_player)

    def deal_holecards(self):
        a = combinations(self.deck, self.holecards)
        return filter(lambda x: all_unique(x), permutations(a, self.players))

    def build_rounds(self, root, players_in, committed, holes, board, deck, bet_history, round_idx, bets = None, next_player = 0):
        if round_idx == len(self.roundinfo):
            self.showdown(root, players_in, committed, holes, board, deck, bet_history)
            return
        bet_history += "/"
        cur_round = self.roundinfo[round_idx]
        while not players_in[next_player]:
            next_player = (next_player + 1) % self.players
        if cur_round.boardcards:
            self.deal_boardcards(root, next_player, players_in, committed, holes, board, deck, bet_history, round_idx)
        else:
            if bets is None:
                bets = [0] * self.players
            self.build_bets(root, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, players_in.count(True), 0, bets)

    def deal_boardcards(self, root, next_player, players_in, committed, holes, board, deck, bet_history, round_idx):
        cur_round = self.roundinfo[round_idx]
        bnode = BoardcardChanceNode(root, committed, holes, board, deck, bet_history, cur_round.boardcards)
        all_bc = combinations(deck, cur_round.boardcards)
        for bc in all_bc:
            cur_board = board + bc
            cur_deck = filter(lambda x: not (x in bc), deck)
            self.build_bets(bnode, next_player, players_in, committed, holes, cur_board, cur_deck, bet_history, round_idx, players_in.count(True), 0, [0] * self.players)

    def build_bets(self, root, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets_this_round):
        # if everyone else folded, end the hand
        if players_in.count(True) == 1:
            self.showdown(root, players_in, committed, holes, board, deck, bet_history)
            return
        # if everyone checked or the last raisor has been called, end the round
        if actions_this_round >= min_actions_this_round and self.all_called_last_raisor_or_folded(players_in, bets_this_round):
            self.build_rounds(root, players_in, committed, holes, board, deck, bet_history, round_idx + 1)
            return
        cur_round = self.roundinfo[round_idx]
        anode = ActionNode(root, committed, holes, board, deck, bet_history, next_player)
        # add the node to the information set
        if not (anode.player_view in self.information_sets):
            self.information_sets[anode.player_view] = []
        self.information_sets[anode.player_view].append(anode)
        # get the next player to act
        next_player = (next_player + 1) % self.players
        while not players_in[next_player]:
            next_player = (next_player + 1) % self.players
        # add a folding option if someone has bet more than this player
        if committed[anode.player] < max(committed):
            self.add_fold_child(anode, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets_this_round)
        # add a calling/checking option
        self.add_call_child(anode, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets_this_round)
        # add a raising option if this player has not reached their max bet level
        if cur_round.maxbets[anode.player] > max(bets_this_round):
            self.add_raise_child(anode, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets_this_round)

    def all_called_last_raisor_or_folded(self, players_in, bets):
        betlevel = max(bets)
        for i,v in enumerate(bets):
            if players_in[i] and bets[i] < betlevel:
                return False
        return True

    def add_fold_child(self, root, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets_this_round):
        players_in[root.player] = False
        bet_history += 'f'
        self.build_bets(root, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round + 1, bets_this_round)
        root.fold_action = root.children[-1]
        players_in[root.player] = True

    def add_call_child(self, root, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets_this_round):
        player_commit = committed[root.player]
        player_bets = bets_this_round[root.player]
        committed[root.player] = max(committed)
        bets_this_round[root.player] = max(bets_this_round)
        bet_history += 'c'
        self.build_bets(root, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round + 1, bets_this_round)
        root.call_action = root.children[-1]
        committed[root.player] = player_commit
        bets_this_round[root.player] = player_bets

    def add_raise_child(self, root, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets_this_round):
        cur_round = self.roundinfo[round_idx]
        prev_betlevel = bets_this_round[root.player]
        prev_commit = committed[root.player]
        bets_this_round[root.player] = max(bets_this_round) + 1
        committed[root.player] += (bets_this_round[root.player] - prev_betlevel) * cur_round.betsize
        bet_history += 'r'
        self.build_bets(root, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round + 1, bets_this_round)
        root.raise_action = root.children[-1]
        bets_this_round[root.player] = prev_betlevel
        committed[root.player] = prev_commit

    def showdown(self, root, players_in, committed, holes, board, deck, bet_history):
        if players_in.count(True) == 1:
            winners = [i for i,v in enumerate(players_in) if v]
        else:
            handsize = len(holes[0]) + len(board)
            if handsize == 1:
                scores = [(hc + board)[0].rank for hc in holes]
            elif handsize == 2:
                temphands = [hc + board for hc in holes]
                scores = [evaluate_twocard_hand(hc) for hc in temphands]
            else:
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
        TerminalNode(root, committed, holes, board, deck, bet_history, payoffs)

    def holecard_distributions(self):
        x = Counter(combinations(self.deck, self.holecards))
        d = float(sum(x.values()))
        return zip(x.keys(),[y / d for y in x.values()])

class Node(object):
    def __init__(self, parent, committed, holecards, board, deck, bet_history):
        self.committed = deepcopy(committed)
        self.holecards = deepcopy(holecards)
        self.board = deepcopy(board)
        self.deck = deepcopy(deck)
        self.bet_history = deepcopy(bet_history)
        if parent:
            self.parent = parent
            self.parent.add_child(self)

    def add_child(self, child):
        if self.children is None:
            self.children = [child]
        else:
            self.children.append(child)

class TerminalNode(Node):
    def __init__(self, parent, committed, holecards, board, deck, bet_history, payoffs):
        Node.__init__(self, parent, committed, holecards, board, deck, bet_history)
        self.payoffs = payoffs

class HolecardChanceNode(Node):
    def __init__(self, parent, committed, holecards, board, deck, bet_history, todeal):
        Node.__init__(self, parent, committed, holecards, board, deck, bet_history)
        self.todeal = todeal
        self.children = []

class BoardcardChanceNode(Node):
    def __init__(self, parent, committed, holecards, board, deck, bet_history, todeal):
        Node.__init__(self, parent, committed, holecards, board, deck, bet_history)
        self.todeal = todeal
        self.children = []

class ActionNode(Node):
    def __init__(self, parent, committed, holecards, board, deck, bet_history, player):
        Node.__init__(self, parent, committed, holecards, board, deck, bet_history)
        self.player = player
        self.children = []
        self.raise_action = None
        self.call_action = None
        self.fold_action = None
        self.player_view = "{0}{1}:{2}".format("".join([str(x) for x in self.holecards[self.player]]), "".join([str(x) for x in self.board]), self.bet_history)

    def valid(self, action):
        if action == FOLD:
            return self.fold_action
        if action == CALL:
            return self.call_action
        if action == RAISE:
            return self.raise_action
        raise Exception("Unknown action {0}. Action must be FOLD, CALL, or RAISE".format(action))

class OpponentNode(Node):
    def __init__(self, parent, opponent):
        Node.__init__(self, parent)
        self.opponent = opponent