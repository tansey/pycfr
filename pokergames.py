from pokertrees import *

def kuhn_eval(hc, board):
    return hc[0].rank

def half_street_kuhn():
    players = 2
    deck = [Card(14,1),Card(13,1),Card(12,1)]
    ante = 1
    blinds = None
    rounds = [RoundInfo(holecards=1,boardcards=0,betsize=1,maxbets=[1,0])]
    tree = GameTree(players, deck, rounds, ante, blinds, handeval=kuhn_eval, infoset_format=leduc_format)
    tree.build()
    return tree

def kuhn():
    players = 2
    deck = [Card(14,1),Card(13,1),Card(12,1)]
    ante = 1
    blinds = None
    rounds = [RoundInfo(holecards=1,boardcards=0,betsize=1,maxbets=[1,1])]
    tree = GameTree(players, deck, rounds, ante, blinds, handeval=kuhn_eval, infoset_format=leduc_format)
    tree.build()
    return tree

def leduc_format(player, holecards, board, bet_history):
    cards = holecards[player][0].RANK_TO_STRING[holecards[player][0].rank]
    if len(board) > 0:
        cards += board[0].RANK_TO_STRING[board[0].rank]
    return "{0}:{1}:".format(cards, bet_history)

def leduc_eval(hc,board):
    hand = hc + board
    if hand[0].rank == hand[1].rank:
        return 15*14+hand[0].rank
    return max(hand[0].rank, hand[1].rank) * 14 + min(hand[0].rank, hand[1].rank)

def leduc():
    players = 2
    deck = [Card(13,1),Card(13,2),Card(12,1),Card(12,2),Card(11,1),Card(11,2)]
    ante = 1
    blinds = None
    rounds = [RoundInfo(holecards=1,boardcards=0,betsize=2,maxbets=[2,2]),RoundInfo(holecards=0,boardcards=1,betsize=4,maxbets=[2,2])]
    tree = GameTree(players, deck, rounds, ante, blinds, handeval=leduc_eval, infoset_format=leduc_format)
    tree.build()
    return tree