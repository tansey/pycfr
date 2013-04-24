from pokertrees import *
from pokerstrategy import *
import random

class CounterfactualRegretMinimizer(object):
    def __init__(self, rules):
        self.rules = rules
        self.profile = StrategyProfile(rules, [Strategy(i) for i in range(rules.players)])
        self.iterations = 0
        self.regret = []
        gametree = GameTree(rules)
        gametree.build()
        for s in self.profile.strategies:
            s.build_default(gametree)
            self.regret.append({ infoset: [0,0,0] for infoset in s.policy })
        self.tree = PublicTree(rules)
        self.tree.build()

    def run(self, num_iterations):
        for iteration in range(num_iterations):
            self.cfr()
            self.iterations += 1

    def cfr(self):
        self.cfr_helper(self.tree.root, [{(): 1} for _ in range(self.rules.players)])

    def cfr_helper(self, root, reachprobs):
        if type(root) is TerminalNode:
            return self.cfr_terminal_node(root, reachprobs)
        if type(root) is HolecardChanceNode:
            return self.cfr_holecard_node(root, reachprobs)
        if type(root) is BoardcardChanceNode:
            return self.cfr_boardcard_node(root, reachprobs)
        return self.cfr_action_node(root, reachprobs)

    def cfr_terminal_node(self, root, reachprobs):
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

    def cfr_holecard_node(self, root, reachprobs):
        assert(len(root.children) == 1)
        prevlen = len(reachprobs[0].keys()[0])
        possible_deals = float(choose(len(root.deck) - prevlen,root.todeal))
        next_reachprobs = [{ hc: reachprobs[player][hc[0:prevlen]] / possible_deals for hc in root.children[0].holecards[player] } for player in range(self.rules.players)]
        subpayoffs = self.cfr_helper(root.children[0], next_reachprobs)
        payoffs = [{ hc: 0 for hc in root.holecards[player] } for player in range(self.rules.players)]
        for player, subpayoff in enumerate(subpayoffs):
            for hand,winnings in subpayoff.items():
                hc = hand[0:prevlen]
                payoffs[player][hc] += winnings
        return payoffs

    def cfr_boardcard_node(self, root, reachprobs):
        prevlen = len(reachprobs[0].keys()[0])
        possible_deals = float(choose(len(root.deck) - prevlen,root.todeal))
        payoffs = [{ hc: 0 for hc in root.holecards[player] } for player in range(self.rules.players)]
        for bc in root.children:
            next_reachprobs = [{ hc: reachprobs[player][hc] / possible_deals for hc in bc.holecards[player] } for player in range(self.rules.players)]
            subpayoffs = self.cfr_helper(bc, next_reachprobs)
            for player,subpayoff in enumerate(subpayoffs):
                for hand,winnings in subpayoff.items():
                    payoffs[player][hand] += winnings
        return payoffs

    def cfr_action_node(self, root, reachprobs):
        # Calculate strategy from positive regret
        strategy = self.cfr_strategy_update(root)
        next_reachprobs = deepcopy(reachprobs)
        action_probs = { hc: strategy.probs(self.rules.infoset_format(root.player, hc, root.board, root.bet_history)) for hc in root.holecards[root.player] }
        action_payoffs = [None, None, None]
        if root.fold_action:
            next_reachprobs[root.player] = { hc: action_probs[hc][FOLD] * reachprobs[root.player][hc] for hc in root.holecards[root.player] }
            action_payoffs[FOLD] = self.cfr_helper(root.fold_action, next_reachprobs)
        if root.call_action:
            next_reachprobs[root.player] = { hc: action_probs[hc][CALL] * reachprobs[root.player][hc] for hc in root.holecards[root.player] }
            action_payoffs[CALL] = self.cfr_helper(root.call_action, next_reachprobs)
        if root.raise_action:
            next_reachprobs[root.player] = { hc: action_probs[hc][RAISE] * reachprobs[root.player][hc] for hc in root.holecards[root.player] }
            action_payoffs[RAISE] = self.cfr_helper(root.raise_action, next_reachprobs)
        payoffs = []
        for player in range(self.rules.players):
            player_payoffs = { hc: 0 for hc in root.holecards[player] }
            for i,subpayoff in enumerate(action_payoffs):
                if subpayoff is None:
                    continue
                for hc,winnings in subpayoff[player].iteritems():
                    # action_probs is baked into reachprobs for everyone except the acting player
                    if player == root.player:
                        player_payoffs[hc] += winnings * action_probs[hc][i]
                    else:
                        player_payoffs[hc] += winnings
            payoffs.append(player_payoffs)
        # Update regret calculations
        self.cfr_regret_update(root, action_payoffs, payoffs[root.player])
        return payoffs

    def cfr_strategy_update(self, root):
        if self.iterations == 0:
            return self.profile.strategies[root.player]
        for hc in root.holecards[root.player]:
            infoset = self.rules.infoset_format(root.player, hc, root.board, root.bet_history)
            prev_regret = self.regret[root.player][infoset]
            sumpos_regret = sum([max(0,x) for x in prev_regret])
            if sumpos_regret == 0:
                total_actions = len(root.children)
                probs = [0,0,0]
                if root.fold_action:
                    probs[FOLD] = 1.0 / total_actions
                if root.call_action:
                    probs[CALL] = 1.0 / total_actions
                if root.raise_action:
                    probs[RAISE] = 1.0 / total_actions
            else:
                probs = [max(0,x) / sumpos_regret for x in prev_regret]
            self.profile.strategies[root.player].policy[infoset] = probs
        return self.profile.strategies[root.player]

    def cfr_regret_update(self, root, action_payoffs, ev):
        for i,subpayoff in enumerate(action_payoffs):
            if subpayoff is None:
                continue
            for hc,winnings in subpayoff[root.player].iteritems():
                immediate_regret = max(winnings - ev[hc], 0)
                infoset = self.rules.infoset_format(root.player, hc, root.board, root.bet_history)
                prev_regret = self.regret[root.player][infoset][i]
                self.regret[root.player][infoset][i] = 1.0 / (self.iterations + 1) * (self.iterations * prev_regret + immediate_regret)

class ProperCounterfactualRegretMinimizer(object):
    def __init__(self, rules):
        self.rules = rules
        self.profile = StrategyProfile(rules, [Strategy(i) for i in range(rules.players)])
        self.current_profile = StrategyProfile(rules, [Strategy(i) for i in range(rules.players)])
        self.iterations = 0
        self.counterfactual_regret = []
        # Note: building the game tree is a convenience. It's not strictly necessary for the algorithm.
        gametree = GameTree(rules)
        gametree.build()
        for s in self.profile.strategies:
            s.build_default(gametree)
            self.counterfactual_regret.append({ infoset: [0,0,0] for infoset in s.policy })
        self.tree = PublicTree(rules)
        self.tree.build()

    def run(self, num_iterations):
        for iteration in range(num_iterations):
            self.cfr()
            self.iterations += 1

    def cfr(self):
        self.cfr_helper(self.tree.root, [{(): 1} for _ in range(self.rules.players)])

    def cfr_helper(self, root, reachprobs):
        if type(root) is TerminalNode:
            return self.cfr_terminal_node(root, reachprobs)
        if type(root) is HolecardChanceNode:
            return self.cfr_holecard_node(root, reachprobs)
        if type(root) is BoardcardChanceNode:
            return self.cfr_boardcard_node(root, reachprobs)
        return self.cfr_action_node(root, reachprobs)

    def cfr_terminal_node(self, root, reachprobs):
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

    def cfr_holecard_node(self, root, reachprobs):
        assert(len(root.children) == 1)
        prevlen = len(reachprobs[0].keys()[0])
        possible_deals = float(choose(len(root.deck) - prevlen,root.todeal))
        next_reachprobs = [{ hc: reachprobs[player][hc[0:prevlen]] / possible_deals for hc in root.children[0].holecards[player] } for player in range(self.rules.players)]
        subpayoffs = self.cfr_helper(root.children[0], next_reachprobs)
        payoffs = [{ hc: 0 for hc in root.holecards[player] } for player in range(self.rules.players)]
        for player, subpayoff in enumerate(subpayoffs):
            for hand,winnings in subpayoff.items():
                hc = hand[0:prevlen]
                payoffs[player][hc] += winnings
        return payoffs

    def cfr_boardcard_node(self, root, reachprobs):
        prevlen = len(reachprobs[0].keys()[0])
        possible_deals = float(choose(len(root.deck) - prevlen,root.todeal))
        payoffs = [{ hc: 0 for hc in root.holecards[player] } for player in range(self.rules.players)]
        for bc in root.children:
            next_reachprobs = [{ hc: reachprobs[player][hc] / possible_deals for hc in bc.holecards[player] } for player in range(self.rules.players)]
            subpayoffs = self.cfr_helper(bc, next_reachprobs)
            for player,subpayoff in enumerate(subpayoffs):
                for hand,winnings in subpayoff.items():
                    payoffs[player][hand] += winnings
        return payoffs

    def cfr_action_node(self, root, reachprobs):
        # Calculate strategy from counterfactual regret
        strategy = self.cfr_strategy_update(root)
        next_reachprobs = deepcopy(reachprobs)
        action_probs = { hc: strategy.probs(self.rules.infoset_format(root.player, hc, root.board, root.bet_history)) for hc in root.holecards[root.player] }
        action_payoffs = [None, None, None]
        if root.fold_action:
            next_reachprobs[root.player] = { hc: action_probs[hc][FOLD] * reachprobs[root.player][hc] for hc in root.holecards[root.player] }
            action_payoffs[FOLD] = self.cfr_helper(root.fold_action, next_reachprobs)
        if root.call_action:
            next_reachprobs[root.player] = { hc: action_probs[hc][CALL] * reachprobs[root.player][hc] for hc in root.holecards[root.player] }
            action_payoffs[CALL] = self.cfr_helper(root.call_action, next_reachprobs)
        if root.raise_action:
            next_reachprobs[root.player] = { hc: action_probs[hc][RAISE] * reachprobs[root.player][hc] for hc in root.holecards[root.player] }
            action_payoffs[RAISE] = self.cfr_helper(root.raise_action, next_reachprobs)
        payoffs = []
        for player in range(self.rules.players):
            player_payoffs = { hc: 0 for hc in root.holecards[player] }
            for i,subpayoff in enumerate(action_payoffs):
                if subpayoff is None:
                    continue
                for hc,winnings in subpayoff[player].iteritems():
                    # action_probs is baked into reachprobs for everyone except the acting player
                    if player == root.player:
                        player_payoffs[hc] += winnings * action_probs[hc][i]
                    else:
                        player_payoffs[hc] += winnings
            payoffs.append(player_payoffs)
        # Update regret calculations
        self.cfr_regret_update(root, action_payoffs, payoffs[root.player])
        return payoffs

    def cfr_strategy_update(self, root):
        if self.iterations == 0:
            return self.profile.strategies[root.player]
        for hc in root.holecards[root.player]:
            infoset = self.rules.infoset_format(root.player, hc, root.board, root.bet_history)
            prev_cfr = self.counterfactual_regret[root.player][infoset]
            sumpos_cfr = sum([max(0,x) for x in prev_cfr])
            if sumpos_cfr == 0:
                total_actions = len(root.children)
                probs = [0,0,0]
                if root.fold_action:
                    probs[FOLD] = 1.0 / total_actions
                if root.call_action:
                    probs[CALL] = 1.0 / total_actions
                if root.raise_action:
                    probs[RAISE] = 1.0 / total_actions
            else:
                probs = [max(0,x) / sumpos_cfr for x in prev_cfr]
            self.current_profile.strategies[root.player].policy[infoset] = probs
            self.profile.strategies[root.player].policy[infoset] = [1.0 / (self.iterations + 1.0) * (self.iterations * self.profile.strategies[root.player].policy[infoset][i] + probs[i]) for i in range(3)]
        return self.current_profile.strategies[root.player]

    def cfr_regret_update(self, root, action_payoffs, ev):
        for i,subpayoff in enumerate(action_payoffs):
            if subpayoff is None:
                continue
            for hc,winnings in subpayoff[root.player].iteritems():
                immediate_cfr = winnings - ev[hc]
                infoset = self.rules.infoset_format(root.player, hc, root.board, root.bet_history)
                prev_cfr = self.counterfactual_regret[root.player][infoset][i]
                self.counterfactual_regret[root.player][infoset][i] = 1.0 / (self.iterations + 1) * (self.iterations * prev_cfr + immediate_cfr)


class PublicChanceSamplingCFR(CounterfactualRegretMinimizer):
    def __init__(self, rules):
        CounterfactualRegretMinimizer.__init__(self, rules)
        self.init_helper(self.tree.root)

    def init_helper(self, node):
        node.visits = 0
        try:
            for child in node.children:
                self.init_helper(child)
        except AttributeError:
            return

    def cfr(self):
        self.board = random.sample(self.rules.deck, sum([x.boardcards for x in self.rules.roundinfo]))
        self.top_card = 0
        self.cfr_helper(self.tree.root, [{(): 1} for _ in range(self.rules.players)])

    def cfr_helper(self, root, reachprobs):
        root.visits += 1
        return CounterfactualRegretMinimizer.cfr_helper(self, root, reachprobs)

    def cfr_boardcard_node(self, root, reachprobs):
        num_dealt = len(root.children[0].board) - len(root.board)
        for bc in root.children:
            if self.boardmatch(num_dealt, bc):
                self.top_card += num_dealt
                results = self.cfr_helper(bc, reachprobs)
                self.top_card -= num_dealt
                return results
    
    def boardmatch(self, num_dealt, node):
        for next_card in range(self.top_card, self.top_card + num_dealt):
            if self.board[next_card] not in node.board:
                return False
        return True

    def cfr_regret_update(self, root, action_payoffs, ev):
        for i,subpayoff in enumerate(action_payoffs):
            if subpayoff is None:
                continue
            for hc,winnings in subpayoff[root.player].iteritems():
                immediate_regret = max(winnings - ev[hc], 0)
                infoset = self.rules.infoset_format(root.player, hc, root.board, root.bet_history)
                prev_regret = self.regret[root.player][infoset][i]
                self.regret[root.player][infoset][i] = 1.0 / (root.visits + 1) * (root.visits * prev_regret + immediate_regret)
