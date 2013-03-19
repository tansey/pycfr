from pokertrees import *

players = 2
deck = [Card(14,1),Card(14,2),Card(13,1),Card(12,1)]
holecards = 1
rounds = [RoundInfo(0,1,2)]
ante = 1
blinds = [1,2]
tree = GameTree(players, deck, holecards, rounds, ante, blinds)
tree.build()