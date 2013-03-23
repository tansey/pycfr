from itertools import combinations
from itertools import permutations
from collections import Counter
from card import Card
from hand_evaluator import HandEvaluator
from copy import deepcopy
from functools import partial

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

def default_infoset_format(player, holecards, board, bet_history):
    return "{0}{1}:{2}:".format("".join([str(x) for x in holecards[player]]), "".join([str(x) for x in board]), bet_history)

class RoundInfo(object):
    def __init__(self, holecards, boardcards, betsize, maxbets):
        self.holecards = holecards
        self.boardcards = boardcards
        self.betsize = betsize
        self.maxbets = maxbets

class GameTree(object):
    def __init__(self, players, deck, rounds, ante, blinds, handeval = HandEvaluator.evaluate_hand, infoset_format=default_infoset_format):
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
        self.roundinfo = rounds
        self.ante = ante
        self.blinds = blinds
        self.handeval = handeval
        self.infoset_format = infoset_format
        self.information_sets = {}

    def build(self):
        # Assume everyone is in
        players_in = [True] * self.players
        # Collect antes
        committed = [self.ante] * self.players
        bets = [0] * self.players
        # Collect blinds
        next_player = self.collect_blinds(committed, bets, 0)
        holes = [()] * self.players
        board = ()
        bet_history = ""
        self.root = self.build_rounds(None, players_in, committed, holes, board, self.deck, bet_history, 0, bets, next_player)

    def collect_blinds(self, committed, bets, next_player):
        if self.blinds != None:
            for blind in self.blinds:
                committed[next_player] += blind
                bets[next_player] = int((committed[next_player] - self.ante) / self.roundinfo[0].betsize)
                next_player = (next_player + 1) % self.players
        return next_player

    def deal_holecards(self, deck, holecards, players):
        a = combinations(deck, holecards)
        return filter(lambda x: all_unique(x), permutations(a, players))

    def build_rounds(self, root, players_in, committed, holes, board, deck, bet_history, round_idx, bets = None, next_player = 0):
        if round_idx == len(self.roundinfo):
            return self.showdown(root, players_in, committed, holes, board, deck, bet_history)
        bet_history += "/"
        cur_round = self.roundinfo[round_idx]
        while not players_in[next_player]:
            next_player = (next_player + 1) % self.players
        if bets is None:
            bets = [0] * self.players
        min_actions_this_round = players_in.count(True)
        actions_this_round = 0
        if cur_round.holecards:
            return self.build_holecards(root, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets)
        if cur_round.boardcards:
            return self.build_boardcards(root, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets)
        return self.build_bets(root, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets)

    def get_next_player(self, cur_player, players_in):
        next_player = (cur_player + 1) % self.players
        while not players_in[next_player]:
            next_player = (next_player + 1) % self.players
        return next_player

    def build_holecards(self, root, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets):
        cur_round = self.roundinfo[round_idx]
        hnode = HolecardChanceNode(root, committed, holes, board, self.deck, "", cur_round.holecards)
        # Deal holecards
        all_hc = self.deal_holecards(deck, cur_round.holecards, players_in.count(True))
        # Create a child node for every possible distribution
        for cur_holes in all_hc:
            dealt_cards = ()
            cur_holes = list(cur_holes)
            cur_idx = 0
            for i,hc in enumerate(holes):
                # Only deal cards to players who are still in
                if players_in[i]:
                    cur_holes[cur_idx] = hc + cur_holes[cur_idx]
                    cur_idx += 1
            for hc in cur_holes:
                dealt_cards += hc
            cur_deck = filter(lambda x: not (x in dealt_cards), deck)
            if cur_round.boardcards:
                self.build_boardcards(hnode, next_player, players_in, committed, cur_holes, board, cur_deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets)
            else:
                self.build_bets(hnode, next_player, players_in, committed, cur_holes, board, cur_deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets)
        return hnode

    def build_boardcards(self, root, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets):
        cur_round = self.roundinfo[round_idx]
        bnode = BoardcardChanceNode(root, committed, holes, board, deck, bet_history, cur_round.boardcards)
        all_bc = combinations(deck, cur_round.boardcards)
        for bc in all_bc:
            cur_board = board + bc
            cur_deck = filter(lambda x: not (x in bc), deck)
            self.build_bets(bnode, next_player, players_in, committed, holes, cur_board, cur_deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets)
        return bnode

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
        anode = ActionNode(root, committed, holes, board, deck, bet_history, next_player, self.infoset_format)
        # add the node to the information set
        if not (anode.player_view in self.information_sets):
            self.information_sets[anode.player_view] = []
        self.information_sets[anode.player_view].append(anode)
        # get the next player to act
        next_player = self.get_next_player(next_player, players_in)
        # add a folding option if someone has bet more than this player
        if committed[anode.player] < max(committed):
            self.add_fold_child(anode, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets_this_round)
        # add a calling/checking option
        self.add_call_child(anode, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets_this_round)
        # add a raising option if this player has not reached their max bet level
        if cur_round.maxbets[anode.player] > max(bets_this_round):
            self.add_raise_child(anode, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets_this_round)
        return anode

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
            scores = [self.handeval(hc, board) for hc in holes]
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
        return TerminalNode(root, committed, holes, board, deck, bet_history, payoffs)

    def holecard_distributions(self):
        x = Counter(combinations(self.deck, self.holecards))
        d = float(sum(x.values()))
        return zip(x.keys(),[y / d for y in x.values()])

def multi_infoset_format(infoset_format, player, holecards, board, bet_history):
        pass

class PublicTree(GameTree):
    def __init__(self, players, deck, rounds, ante, blinds, handeval = HandEvaluator.evaluate_hand, infoset_format=default_infoset_format):
        GameTree.__init__(players, deck, rounds, ante, blinds, handeval, partial(multi_infoset_format, infoset_format=infoset_format))

    def build_holecards(self, root, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets):
        cur_round = self.roundinfo[round_idx]
        hnode = HolecardChanceNode(root, committed, holes, board, self.deck, "", cur_round.holecards)
        # Deal holecards
        all_hc = self.deal_holecards(deck, cur_round.holecards, players_in.count(True))
        for cur_holes in all_hc:
            dealt_cards = ()
            cur_holes = list(cur_holes)
            cur_idx = 0
            for i,hc in enumerate(holes):
                if players_in[i]:
                    cur_holes[cur_idx] = hc + cur_holes[cur_idx]
                    cur_idx += 1
        if cur_round.boardcards:
            self.build_boardcards(hnode, next_player, players_in, committed, cur_holes, board, cur_deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets)
        else:
            self.build_bets(hnode, next_player, players_in, committed, cur_holes, board, cur_deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets)
        return hnode

    def build_boardcards(self, root, next_player, players_in, committed, holes, board, deck, bet_history, round_idx, min_actions_this_round, actions_this_round, bets):
        pass

    # infosets: [ infosets_0, infosets_1, ... ]
    # infosets_i: { 'infoset_0': [state0, state1, ... ], 'infoset_1': [state0, state1, ... ], ... }
    # reach_probs: [ reach_probs_0, reach_probs_1, ... ]
    # reach_probs_i: { 'infoset_0': prob0 }
    def showdown(self, root, players_in, committed, holes, board, deck, bet_history):
        """
        payoffs = []
        # for every player
        for i in range(self.players):
            player_payoffs = {}
            # for every information set that the player may be in
            for infoset in infosets[i]:
                info_r = 0 # the reward for this info set
                total_prob = 0 # the cumulative probability given opponent cards
                # for every state in the information set
                for state in infosets[i][infoset]:
                    # the probability of opponents allowing you to reach this state
                    reach_prob = get_reach_prob(reach_probs, state, i)
                    info_r += state.payoffs[i] * reach_prob # add the reward for this state
                    total_prob += reach_prob # add this probability to the total for this infoset
                player_payoffs[infoset] = info_r / total_prob, set the normalized value for this infoset
            payoffs.append(player_payoffs)
        return payoffs
        """
        pass

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
    def __init__(self, parent, committed, holecards, board, deck, bet_history, player, infoset_format):
        Node.__init__(self, parent, committed, holecards, board, deck, bet_history)
        self.player = player
        self.children = []
        self.raise_action = None
        self.call_action = None
        self.fold_action = None
        self.player_view = infoset_format(player, holecards, board, bet_history)

    def valid(self, action):
        if action == FOLD:
            return self.fold_action
        if action == CALL:
            return self.call_action
        if action == RAISE:
            return self.raise_action
        raise Exception("Unknown action {0}. Action must be FOLD, CALL, or RAISE".format(action))
