from pokertrees import *

class Strategy(object):
    def __init__(self, player):
        self.player = player
        self.policy = {}

    def build_default(self, gametree):
        for key in gametree.information_sets:
            node = gametree.information_sets[key][0]
            if node.player == self.player:
                prob = 1.0 / float(len(node.children))
                probs = [0,0,0]
                for action in range(3):
                    if node.valid(action):
                        probs[action] = prob
                self.policy[node.player_view] = probs

    def probs(self, infoset):
        assert(infoset in self.policy)
        return self.policy[infoset]

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
            self.gametree = GameTree(self.rules)
        if self.gametree.root is None:
            self.gametree.build()
        return self.ev_helper(self.gametree.root, 1)

    def ev_helper(self, root, pathprob):
        if type(root) is TerminalNode:
            payoffs = [x*pathprob for x in root.payoffs]
            return payoffs
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

    def best_response(self, player):
        """
        Calculates the best response of the given player to the strategy profile.
        Returns a tuple of the best response strategy and its expected value.
        TODO: Extend this to calculate best response of all players simultaneously.
        """
        if self.publictree is None:
            self.publictree = PublicTree(self.rules)
        if self.publictree.root is None:
            self.publictree.build()
        response = Strategy(player)
        ev = sum(self.br_helper(self.publictree.root, [{(): 1} for _ in range(self.rules.players)], response))
        return (response, ev)

    def br_helper(self, root, reachprobs, response):
        if type(root) is TerminalNode:
            payoffs = [0 for _ in root.holecards[response.player]]
            print 'Bet history: {0}'.format(root.bet_history)
            for showdown in root.payoffs:
                prob = 1
                print '\tShowdown: {0}'.format(showdown)
                for i,hc in enumerate(showdown):
                    print '\t\tPlayer: {0} HC: {1} Reachprobs: {2}'.format(i,hc,reachprobs[i])
                    prob *= reachprobs[i][hc]
                print '\tShowdown prob: {0}'.format(prob)
                hc_idx = root.holecards[response.player].index(showdown[response.player])
                print '\thc_idx: {0}'.format(hc_idx)
                payoffs[hc_idx] += prob * root.payoffs[showdown][response.player]
            print 'Payoffs for player {0}: {1}'.format(response.player, payoffs)
            return payoffs
        if type(root) is HolecardChanceNode:
            assert(len(root.children) == 1)
            next_reachprobs = []
            for player in range(self.rules.players):
                next_player_reachprobs = {}
                for hc in root.children[0].holecards[player]:
                    prevlen = len(hc) - root.todeal
                    next_player_reachprobs[hc] = reachprobs[player][hc[0:prevlen]] / float(self.choose(len(root.deck) - prevlen,root.todeal))
                next_reachprobs.append(next_player_reachprobs)
            return self.br_helper(root.children[0], next_reachprobs, response)
        if type(root) is BoardcardChanceNode:
            payoffs = [0 for _ in root.holecards[response.player]]
            for bc in root.children:
                subpayoffs = self.br_helper(bc, reachprobs, response)
                for i,v in enumerate(subpayoffs):
                    payoffs[i] += v
            return payoffs
        # It's an ActionNode for an opponent
        if root.player != response.player:
            strategy = self.strategies[root.player]
            actionprobs = {}
            for hc in root.holecards[root.player]:
                infoset = self.rules.infoset_format(root.player, hc, root.board, root.bet_history)
                actionprobs[hc] = strategy.probs(infoset)
            payoffs = [0 for _ in root.holecards[response.player]]
            if root.fold_action:
                self.br_opponent_action(root, reachprobs, actionprobs, response, FOLD, payoffs)
            if root.call_action:
                self.br_opponent_action(root, reachprobs, actionprobs, response, CALL, payoffs)
            if root.raise_action:
                self.br_opponent_action(root, reachprobs, actionprobs, response, RAISE, payoffs)
            return payoffs
        # It's an ActionNode for the response player
        action_payoffs = [None, None, None]
        if root.fold_action:
            action_payoffs[FOLD] = self.br_helper(root.fold_action, reachprobs, response)
        if root.call_action:
            action_payoffs[CALL] = self.br_helper(root.call_action, reachprobs, response)
        if root.raise_action:
            action_payoffs[RAISE] = self.br_helper(root.raise_action, reachprobs, response)
        payoffs = []
        for i,hc in enumerate(root.holecards[root.player]):
            infoset = self.rules.infoset_format(root.player, hc, root.board, root.bet_history)
            maxv = None
            max_actions = None
            if root.fold_action:
                maxv = action_payoffs[FOLD][i]
                max_actions = [FOLD]
            if root.call_action and (maxv is None or action_payoffs[CALL][i] >= maxv):
                if maxv is None or action_payoffs[CALL][i] > maxv:
                    maxv = action_payoffs[CALL][i]
                    max_actions = [CALL]
                else:
                    max_actions.append(CALL)
            if root.raise_action and (maxv is None or action_payoffs[RAISE][i] >= maxv):
                if maxv is None or action_payoffs[RAISE][i] > maxv:
                    maxv = action_payoffs[RAISE][i]
                    max_actions = [RAISE]
                else:
                    max_actions.append(RAISE)
            action_probs = [0,0,0]
            for action in max_actions:
                action_probs[action] = 1.0 / len(max_actions)
            response.policy[infoset] = action_probs
            payoffs.append(maxv)
        return payoffs

    def br_opponent_action(self, root, reachprobs, actionprobs, response, action, payoffs):
        next_reachprobs = deepcopy(reachprobs)
        next_reachprobs[root.player] = { hc: reachprobs[root.player][hc] * actionprobs[hc][action] for hc in root.holecards[root.player] }
        if action == FOLD:
            child = root.fold_action
        elif action == CALL:
            child = root.call_action
        else:
            child = root.raise_action
        subpayoffs = self.br_helper(child, next_reachprobs, response)
        for i,v in enumerate(subpayoffs):
            payoffs[i] += v

    def choose(self, n, k):
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

