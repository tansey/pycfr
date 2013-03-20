from pokertrees import *

class Strategy(object):
    def __init__(self, player, policy = {}):
        self.player = player
        self.policy = policy

    def build_default(self, gametree):
        for infoset in gametree.information_sets:
            node = infoset[0]
            if node.player == self.player:
                prob = 1.0 / float(len(node.children))
                probs = [0,0,0]
                for action in range(3):
                    if node.valid(action):
                        probs[action] = prob
                policy[node.player_view] = probs

    def probdist(self, infoset):
        assert(infoset in policy)
        return policy[infoset]

    def load_from_file(self, filename):
        pass

    def save_to_file(self, filename):
        pass