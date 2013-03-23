from pokertrees import *

def kuhn_eval(hc, board):
    return hc[0].rank

def half_street_kuhn_rules():
    players = 2
    deck = [Card(14,1),Card(13,1),Card(12,1)]
    ante = 1
    blinds = None
    rounds = [RoundInfo(holecards=1,boardcards=0,betsize=1,maxbets=[1,0])]
    return GameRules(players, deck, rounds, ante, blinds, handeval=kuhn_eval, infoset_format=leduc_format)

def half_street_kuhn_gametree():
    rules = half_street_kuhn_rules()
    tree = GameTree(rules)
    tree.build()
    return tree

def half_street_kuhn_publictree():
    rules = half_street_kuhn_rules()
    tree = PublicTree(rules)
    tree.build()
    return tree

def kuhn_rules():
    players = 2
    deck = [Card(14,1),Card(13,1),Card(12,1)]
    ante = 1
    blinds = None
    rounds = [RoundInfo(holecards=1,boardcards=0,betsize=1,maxbets=[1,1])]
    return GameRules(players, deck, rounds, ante, blinds, handeval=kuhn_eval, infoset_format=leduc_format) 

def kuhn_gametree():
    rules = kuhn_rules()
    tree = GameTree(rules)
    tree.build()
    return tree

def kuhn_publictree():
    rules = kuhn_rules()
    tree = PublicTree(rules)
    tree.build()
    return tree

def leduc_format(player, holecards, board, bet_history):
    cards = holecards[0].RANK_TO_STRING[holecards[0].rank]
    if len(board) > 0:
        cards += board[0].RANK_TO_STRING[board[0].rank]
    return "{0}:{1}:".format(cards, bet_history)

def leduc_eval(hc,board):
    hand = hc + board
    if hand[0].rank == hand[1].rank:
        return 15*14+hand[0].rank
    return max(hand[0].rank, hand[1].rank) * 14 + min(hand[0].rank, hand[1].rank)

def leduc_rules():
    players = 2
    deck = [Card(13,1),Card(13,2),Card(12,1),Card(12,2),Card(11,1),Card(11,2)]
    ante = 1
    blinds = None
    rounds = [RoundInfo(holecards=1,boardcards=0,betsize=2,maxbets=[2,2]),RoundInfo(holecards=0,boardcards=1,betsize=4,maxbets=[2,2])]
    return GameRules(players, deck, rounds, ante, blinds, handeval=leduc_eval, infoset_format=leduc_format)

def leduc_gametree():
    rules = leduc_rules()
    tree = GameTree(rules)
    tree.build()
    return tree

def leduc_publictree():
    rules = leduc_rules()
    tree = PublicTree(rules)
    tree.build()
    return tree    