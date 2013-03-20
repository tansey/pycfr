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
            probs = [float(x) for x in tokens[1:]]
            self.policy[key] = probs

    def save_to_file(self, filename):
        f = open(filename, 'w')
        for key in sorted(self.policy.keys()):
            val = self.policy[key]
            f.write("{0} {1:.9f} {2:.9f} {3:.9f}\n".format(key, val[0], val[1], val[2]))
        f.flush()
        f.close()

class StrategyProfile(object):
    def __init__(self, gametree, strategies):
        assert(gametree.players == len(strategies))
        self.gametree = gametree
        self.strategies = strategies
