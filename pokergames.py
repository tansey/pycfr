from pokertrees import *

def half_street_kuhn():
    players = 2
    deck = [Card(14,1),Card(13,1),Card(12,1)]
    holecards = 1
    ante = 1
    blinds = None
    rounds = [RoundInfo(boardcards=0,betsize=1,maxbets=[1,0])]
    tree = GameTree(players, deck, holecards, rounds, ante, blinds)
    tree.build()
    return tree

def leduc():
    players = 2
    deck = [Card(14,1),Card(13,1),Card(12,1),Card(14,2),Card(13,2),Card(12,2)]
    holecards = 1
    ante = 1
    blinds = None
    rounds = [RoundInfo(boardcards=0,betsize=1,maxbets=[2,2]),RoundInfo(boardcards=1,betsize=2,maxbets=[2,2])]
    tree = GameTree(players, deck, holecards, rounds, ante, blinds)
    tree.build()
    return tree