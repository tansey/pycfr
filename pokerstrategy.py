from pokertrees import *
import random

def choose(n, k):
    """
    A fast way to calculate binomial coefficients by Andrew Dalke (contrib).
    """
    if 0 <= k <= n:
        ntok = 1
        ktok = 1
        for t in xrange(1, min(k, n - k) + 1):
            ntok *= n
            ktok *= t
            n -= 1
        return ntok // ktok
    else:
        return 0

class Strategy(object):
    def __init__(self, player, filename=None):
        self.player = player
        self.policy = {}
        if filename is not None:
            self.load_from_file(filename)

    def build_default(self, gametree):
        for key in gametree.information_sets:
            infoset = gametree.information_sets[key]
            test_node = infoset[0]
            if test_node.player == self.player:
                for node in infoset:
                    prob = 1.0 / float(len(node.children))
                    probs = [0,0,0]
                    for action in range(3):
                        if node.valid(action):
                            probs[action] = prob
                    if type(node.player_view) is tuple:
                        for pview in node.player_view:
                            self.policy[pview] = [x for x in probs]
                    else:
                        self.policy[node.player_view] = probs

    def build_random(self, gametree):
        for key in gametree.information_sets:
            infoset = gametree.information_sets[key]
            test_node = infoset[0]
            if test_node.player == self.player:
                for node in infoset:
                    probs = [0 for _ in range(3)]
                    total = 0
                    for action in range(3):
                        if node.valid(action):
                            probs[action] = random.random()
                            total += probs[action]
                    probs = [x / total for x in probs]
                    if type(node.player_view) is tuple:
                        for pview in node.player_view:
                            self.policy[pview] = [x for x in probs]
                    else:
                        self.policy[node.player_view] = probs

    def probs(self, infoset):
        assert(infoset in self.policy)
        return self.policy[infoset]

    def sample_action(self, infoset):
        assert(infoset in self.policy)
        probs = self.policy[infoset]
        val = random.random()
        total = 0
        for i,p in enumerate(probs):
            total += p
            if p > 0 and val <= total:
                return i
        raise Exception('Invalid probability distribution. Infoset: {0} Probs: {1}'.format(infoset, probs))

    def load_from_file(self, filename):
        self.policy = {}
        f = open(filename, 'r')
        for line in f:
            line = line.strip()
            if line == "" or line.startswith('#'):
                continue
            tokens = line.split(' ')
            assert(len(tokens) == 4)
            key = tokens[0]
            probs = [float(x) for x in reversed(tokens[1:])]
            self.policy[key] = probs

    def save_to_file(self, filename):
        f = open(filename, 'w')
        for key in sorted(self.policy.keys()):
            val = self.policy[key]
            f.write("{0} {1:.9f} {2:.9f} {3:.9f}\n".format(key, val[2], val[1], val[0]))
        f.flush()
        f.close()

class StrategyProfile(object):
    def __init__(self, rules, strategies):
        assert(rules.players == len(strategies))
        self.rules = rules
        self.strategies = strategies
        self.gametree = None
        self.publictree = None

    def expected_value(self):
        """
        Calculates the expected value of each strategy in the profile.
        Returns an array of scalars corresponding to the expected payoffs.
        """
        if self.gametree is None:
            self.gametree = PublicTree(self.rules)
        if self.gametree.root is None:
            self.gametree.build()
        expected_values = self.ev_helper(self.gametree.root, [{(): 1} for _ in range(self.rules.players)])
        for ev in expected_values:
            assert(len(ev) == 1)
        return tuple(next(ev.itervalues()) for ev in expected_values) # pull the EV from the dict returned

    def old_ev_helper(self, root, pathprobs):
        if type(root) is TerminalNode:
            return self.ev_terminal_node(root, reachprobs)
        if type(root) is HolecardChanceNode or type(root) is BoardcardChanceNode:
            payoffs = [0] * self.rules.players
            prob = pathprob / float(len(root.children))
            for child in root.children:
                subpayoffs = self.ev_helper(child, prob)
                for i,p in enumerate(subpayoffs):
                    payoffs[i] += p
            return payoffs
        # Otherwise, it's an ActionNode
        probs = self.strategies[root.player].probs(root.player_view)
        payoffs = [0] * self.rules.players
        if root.fold_action and probs[FOLD] > 0.0000000001:
            subpayoffs = self.ev_helper(root.fold_action, pathprob * probs[FOLD])
            for i,p in enumerate(subpayoffs):
                payoffs[i] += p
        if root.call_action and probs[CALL] > 0.0000000001:
            subpayoffs = self.ev_helper(root.call_action, pathprob * probs[CALL])
            for i,p in enumerate(subpayoffs):
                payoffs[i] += p
        if root.raise_action and probs[RAISE] > 0.0000000001:
            subpayoffs = self.ev_helper(root.raise_action, pathprob * probs[RAISE])
            for i,p in enumerate(subpayoffs):
                payoffs[i] += p
        return payoffs

    def ev_helper(self, root, reachprobs):
        if type(root) is TerminalNode:
            return self.ev_terminal_node(root, reachprobs)
        if type(root) is HolecardChanceNode:
            return self.ev_holecard_node(root, reachprobs)
        if type(root) is BoardcardChanceNode:
            return self.ev_boardcard_node(root, reachprobs)
        return self.ev_action_node(root, reachprobs)

    def ev_terminal_node(self, root, reachprobs):
        payoffs = [None for _ in range(self.rules.players)]
        for player in range(self.rules.players):
            player_payoffs = {hc: 0 for hc in root.holecards[player]}
            counts = {hc: 0 for hc in root.holecards[player]}
            for hands,winnings in root.payoffs.items():
                prob = 1.0
                player_hc = None
                for opp,hc in enumerate(hands):
                    if opp == player:
                        player_hc = hc
                    else:
                        prob *= reachprobs[opp][hc]
                player_payoffs[player_hc] += prob * winnings[player]
                counts[player_hc] += 1
            for hc,count in counts.items():
                if count > 0:
                    player_payoffs[hc] /= float(count)
            payoffs[player] = player_payoffs
        return payoffs

    def ev_holecard_node(self, root, reachprobs):
        assert(len(root.children) == 1)
        prevlen = len(reachprobs[0].keys()[0])
        possible_deals = float(choose(len(root.deck) - prevlen,root.todeal))
        next_reachprobs = [{ hc: reachprobs[player][hc[0:prevlen]] / possible_deals for hc in root.children[0].holecards[player] } for player in range(self.rules.players)]
        subpayoffs = self.ev_helper(root.children[0], next_reachprobs)
        payoffs = [{ hc: 0 for hc in root.holecards[player] } for player in range(self.rules.players)]
        for player, subpayoff in enumerate(subpayoffs):
            for hand,winnings in subpayoff.items():
                hc = hand[0:prevlen]
                payoffs[player][hc] += winnings
        return payoffs

    def ev_boardcard_node(self, root, reachprobs):
        prevlen = len(reachprobs[0].keys()[0])
        possible_deals = float(choose(len(root.deck) - prevlen,root.todeal))
        payoffs = [{ hc: 0 for hc in root.holecards[player] } for player in range(self.rules.players)]
        for bc in root.children:
            next_reachprobs = [{ hc: reachprobs[player][hc] / possible_deals for hc in bc.holecards[player] } for player in range(self.rules.players)]
            subpayoffs = self.ev_helper(bc, next_reachprobs)
            for player,subpayoff in enumerate(subpayoffs):
                for hand,winnings in subpayoff.items():
                    payoffs[player][hand] += winnings
        return payoffs

    def ev_action_node(self, root, reachprobs):
        strategy = self.strategies[root.player]
        next_reachprobs = deepcopy(reachprobs)
        action_probs = { hc: strategy.probs(self.rules.infoset_format(root.player, hc, root.board, root.bet_history)) for hc in root.holecards[root.player] }
        action_payoffs = [None, None, None]
        if root.fold_action:
            next_reachprobs[root.player] = { hc: action_probs[hc][FOLD] * reachprobs[root.player][hc] for hc in root.holecards[root.player] }
            action_payoffs[FOLD] = self.ev_helper(root.fold_action, next_reachprobs)
        if root.call_action:
            next_reachprobs[root.player] = { hc: action_probs[hc][CALL] * reachprobs[root.player][hc] for hc in root.holecards[root.player] }
            action_payoffs[CALL] = self.ev_helper(root.call_action, next_reachprobs)
        if root.raise_action:
            next_reachprobs[root.player] = { hc: action_probs[hc][RAISE] * reachprobs[root.player][hc] for hc in root.holecards[root.player] }
            action_payoffs[RAISE] = self.ev_helper(root.raise_action, next_reachprobs)
        payoffs = []
        for player in range(self.rules.players):
            player_payoffs = { hc: 0 for hc in root.holecards[player] }
            for action,subpayoff in enumerate(action_payoffs):
                if subpayoff is None:
                    continue
                if root.player == player:
                    for hc,winnings in subpayoff[player].iteritems():
                        player_payoffs[hc] += winnings * action_probs[hc][action]
                else:
                    for hc,winnings in subpayoff[player].iteritems():
                        player_payoffs[hc] += winnings
            payoffs.append(player_payoffs)
        return payoffs

    def best_response(self):
        """
        Calculates the best response for each player in the strategy profile.
        Returns a list of tuples of the best response strategy and its expected value for each player.
        """
        if self.publictree is None:
            self.publictree = PublicTree(self.rules)
        if self.publictree.root is None:
            self.publictree.build()
        responses = [Strategy(player) for player in range(self.rules.players)]
        expected_values = self.br_helper(self.publictree.root, [{(): 1} for _ in range(self.rules.players)], responses)
        for ev in expected_values:
            assert(len(ev) == 1)
        expected_values = tuple(next(ev.itervalues()) for ev in expected_values) # pull the EV from the dict returned
        return (StrategyProfile(self.rules, responses), expected_values)

    def br_helper(self, root, reachprobs, responses):
        if type(root) is TerminalNode:
            return self.ev_terminal_node(root, reachprobs)
        if type(root) is HolecardChanceNode:
            return self.br_holecard_node(root, reachprobs, responses)
        if type(root) is BoardcardChanceNode:
            return self.br_boardcard_node(root, reachprobs, responses)
        return self.br_action_node(root, reachprobs, responses)

    def br_holecard_node(self, root, reachprobs, responses):
        assert(len(root.children) == 1)
        prevlen = len(reachprobs[0].keys()[0])
        possible_deals = float(choose(len(root.deck) - prevlen,root.todeal))
        next_reachprobs = [{ hc: reachprobs[player][hc[0:prevlen]] / possible_deals for hc in root.children[0].holecards[player] } for player in range(self.rules.players)]
        subpayoffs = self.br_helper(root.children[0], next_reachprobs, responses)
        payoffs = [{ hc: 0 for hc in root.holecards[player] } for player in range(self.rules.players)]
        for player, subpayoff in enumerate(subpayoffs):
            for hand,winnings in subpayoff.items():
                hc = hand[0:prevlen]
                payoffs[player][hc] += winnings
        return payoffs

    def br_boardcard_node(self, root, reachprobs, responses):
        prevlen = len(reachprobs[0].keys()[0])
        possible_deals = float(choose(len(root.deck) - prevlen,root.todeal))
        payoffs = [{ hc: 0 for hc in root.holecards[player] } for player in range(self.rules.players)]
        for bc in root.children:
            next_reachprobs = [{ hc: reachprobs[player][hc] / possible_deals for hc in bc.holecards[player] } for player in range(self.rules.players)]
            subpayoffs = self.br_helper(bc, next_reachprobs, responses)
            for player,subpayoff in enumerate(subpayoffs):
                for hand,winnings in subpayoff.items():
                    payoffs[player][hand] += winnings
        return payoffs

    def br_action_node(self, root, reachprobs, responses):
        strategy = self.strategies[root.player]
        next_reachprobs = deepcopy(reachprobs)
        action_probs = { hc: strategy.probs(self.rules.infoset_format(root.player, hc, root.board, root.bet_history)) for hc in root.holecards[root.player] }
        action_payoffs = [None, None, None]
        if root.fold_action:
            next_reachprobs[root.player] = { hc: action_probs[hc][FOLD] * reachprobs[root.player][hc] for hc in root.holecards[root.player] }
            action_payoffs[FOLD] = self.br_helper(root.fold_action, next_reachprobs, responses)
        if root.call_action:
            next_reachprobs[root.player] = { hc: action_probs[hc][CALL] * reachprobs[root.player][hc] for hc in root.holecards[root.player] }
            action_payoffs[CALL] = self.br_helper(root.call_action, next_reachprobs, responses)
        if root.raise_action:
            next_reachprobs[root.player] = { hc: action_probs[hc][RAISE] * reachprobs[root.player][hc] for hc in root.holecards[root.player] }
            action_payoffs[RAISE] = self.br_helper(root.raise_action, next_reachprobs, responses)
        payoffs = []
        for player in range(self.rules.players):
            if player is root.player:
                payoffs.append(self.br_response_action(root, responses, action_payoffs))
            else:
                player_payoffs = { hc: 0 for hc in root.holecards[player] }
                for subpayoff in action_payoffs:
                    if subpayoff is None:
                        continue
                    for hc,winnings in subpayoff[player].iteritems():
                        player_payoffs[hc] += winnings
                payoffs.append(player_payoffs)
        return payoffs

    def br_response_action(self, root, responses, action_payoffs):
        player_payoffs = { }
        max_strategy = responses[root.player]
        for hc in root.holecards[root.player]:
            max_action = None
            if action_payoffs[FOLD]:
                max_action = [FOLD]
                max_value = action_payoffs[FOLD][root.player][hc]
            if action_payoffs[CALL]:
                value = action_payoffs[CALL][root.player][hc]
                if max_action is None or value > max_value:
                    max_action = [CALL]
                    max_value = value
                elif max_value == value:
                    max_action.append(CALL)
            if action_payoffs[RAISE]:
                value = action_payoffs[RAISE][root.player][hc]
                if max_action is None or value > max_value:
                    max_action = [RAISE]
                    max_value = value
                elif max_value == value:
                    max_action.append(RAISE)
            probs = [0,0,0]
            for action in max_action:
                probs[action] = 1.0 / float(len(max_action))
            infoset = self.rules.infoset_format(root.player, hc, root.board, root.bet_history)
            max_strategy.policy[infoset] = probs
            player_payoffs[hc] = max_value
        return player_payoffs



