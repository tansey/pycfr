import sys
import os
sys.path.insert(0,os.path.realpath('.'))
from pokertrees import *
from pokergames import *

print 'Testing GameTree'
rules = GameRules(players = 2, deck = [Card(14,1),Card(13,2),Card(13,1),Card(12,1)], rounds = [RoundInfo(holecards=1,boardcards=0,betsize=1,maxbets=[2,2]),RoundInfo(holecards=0,boardcards=1,betsize=2,maxbets=[2,2])], ante = 1, blinds = [1,2], handeval=leduc_eval)
tree = GameTree(rules)
tree.build()
assert(type(tree.root) == HolecardChanceNode)
assert(len(tree.root.children) == 12)
assert(type(tree.root.children[0]) == ActionNode)
assert(tree.root.children[0].player == 0)
assert(len(tree.root.children[0].children) == 2)
assert(tree.root.children[0].player_view == "As:/:")
# /f
assert(type(tree.root.children[0].children[0]) == TerminalNode)
assert(tree.root.children[0].children[0].payoffs == [-2,2])
assert(tree.root.children[0].children[0].bet_history == '/f')
# /c
assert(type(tree.root.children[0].children[1]) == ActionNode)
assert(tree.root.children[0].children[1].bet_history == '/c')
assert(len(tree.root.children[0].children[1].children) == 1)
assert(tree.root.children[0].children[1].player == 1)
assert(tree.root.children[0].children[1].fold_action is None)
assert(tree.root.children[0].children[1].call_action != None)
assert(tree.root.children[0].children[1].raise_action is None)
assert(tree.root.children[0].children[1].player_view == "Kh:/c:")
# /cc/ [boardcard]
assert(type(tree.root.children[0].children[1].children[0]) == BoardcardChanceNode)
assert(tree.root.children[0].children[1].children[0].bet_history == '/cc/')
assert(len(tree.root.children[0].children[1].children[0].children) == 2)
# /cc/ [action]
assert(type(tree.root.children[0].children[1].children[0].children[0]) == ActionNode)
assert(tree.root.children[0].children[1].children[0].children[0].bet_history == '/cc/')
assert(len(tree.root.children[0].children[1].children[0].children[0].children) == 2)
assert(tree.root.children[0].children[1].children[0].children[0].player == 0)
assert(tree.root.children[0].children[1].children[0].children[0].fold_action is None)
assert(tree.root.children[0].children[1].children[0].children[0].call_action != None)
assert(tree.root.children[0].children[1].children[0].children[0].raise_action != None)
assert(tree.root.children[0].children[1].children[0].children[0].player_view == 'AsKs:/cc/:')
# /cc/r
assert(type(tree.root.children[0].children[1].children[0].children[0].children[1]) == ActionNode)
assert(tree.root.children[0].children[1].children[0].children[0].children[1].bet_history == '/cc/r')
assert(len(tree.root.children[0].children[1].children[0].children[0].children[1].children) == 3)
assert(tree.root.children[0].children[1].children[0].children[0].children[1].player == 1)
assert(tree.root.children[0].children[1].children[0].children[0].children[1].fold_action != None)
assert(tree.root.children[0].children[1].children[0].children[0].children[1].call_action != None)
assert(tree.root.children[0].children[1].children[0].children[0].children[1].raise_action != None)
assert(tree.root.children[0].children[1].children[0].children[0].children[1].player_view == 'KhKs:/cc/r:')
# /cc/c
assert(type(tree.root.children[0].children[1].children[0].children[0].children[0]) == ActionNode)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].bet_history == '/cc/c')
assert(len(tree.root.children[0].children[1].children[0].children[0].children[0].children) == 2)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].player == 1)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].fold_action is None)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].call_action != None)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].raise_action != None)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].player_view == 'KhKs:/cc/c:')
# /cc/cc
assert(type(tree.root.children[0].children[1].children[0].children[0].children[0].children[0]) == TerminalNode)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[0].bet_history == '/cc/cc')
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[0].payoffs == [-3,3])
# /cc/cr
assert(type(tree.root.children[0].children[1].children[0].children[0].children[0].children[1]) == ActionNode)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].bet_history == '/cc/cr')
assert(len(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].children) == 3)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].player == 0)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].fold_action != None)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].call_action != None)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].raise_action != None)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].player_view == 'AsKs:/cc/cr:')
# /cc/crr
assert(type(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].children[2]) == ActionNode)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].children[2].bet_history == '/cc/crr')
assert(len(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].children[2].children) == 2)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].children[2].player == 1)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].children[2].fold_action != None)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].children[2].call_action != None)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].children[2].raise_action is None)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].children[2].player_view == 'KhKs:/cc/crr:')
# /cc/crrf
assert(type(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].children[2].children[0]) == TerminalNode)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].children[2].children[0].bet_history == '/cc/crrf')
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].children[2].children[0].payoffs == [5,-5])
# /cc/crrc
assert(type(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].children[2].children[1]) == TerminalNode)
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].children[2].children[1].bet_history == '/cc/crrc')
assert(tree.root.children[0].children[1].children[0].children[0].children[0].children[1].children[2].children[1].payoffs == [-7,7])
print 'All passed!'

print 'Testing PublicTree'
tree = PublicTree(rules)
tree.build()

assert(type(tree.root) == HolecardChanceNode)
assert(len(tree.root.children) == 1)
# /
assert(type(tree.root.children[0]) == ActionNode)
assert(tree.root.children[0].player == 0)
assert(tree.root.children[0].player_view == ('As:/:', 'Kh:/:', 'Ks:/:', 'Qs:/:'))
assert(len(tree.root.children[0].children) == 2)
assert(tree.root.children[0].fold_action != None)
assert(tree.root.children[0].call_action != None)
assert(tree.root.children[0].raise_action == None)
# /f
assert(type(tree.root.children[0].children[0]) == TerminalNode)
assert(tree.root.children[0].children[0].payoffs == { ((Card(14,1),),(Card(13,1),)): [-2,2], ((Card(14,1),),(Card(13,2),)): [-2,2], ((Card(14,1),),(Card(12,1),)): [-2,2], ((Card(13,1),),(Card(14,1),)): [-2,2], ((Card(13,1),),(Card(13,2),)): [-2,2], ((Card(13,1),),(Card(12,1),)): [-2,2], ((Card(13,2),),(Card(14,1),)): [-2,2], ((Card(13,2),),(Card(13,1),)): [-2,2], ((Card(13,2),),(Card(12,1),)): [-2,2], ((Card(12,1),),(Card(14,1),)): [-2,2], ((Card(12,1),),(Card(13,2),)): [-2,2], ((Card(12,1),),(Card(13,1),)): [-2,2] })
# /c
assert(type(tree.root.children[0].children[1]) == ActionNode)
assert(tree.root.children[0].children[1].player == 1)
assert(tree.root.children[0].children[1].player_view == ('As:/c:', 'Kh:/c:', 'Ks:/c:', 'Qs:/c:'))
assert(len(tree.root.children[0].children[1].children) == 1)
# /cc/ [boardcard]
assert(type(tree.root.children[0].children[1].children[0]) == BoardcardChanceNode)
assert(tree.root.children[0].children[1].children[0].bet_history == '/cc/')
assert(len(tree.root.children[0].children[1].children[0].children) == 4)
# xAs:/cc/ [action]
assert(type(tree.root.children[0].children[1].children[0].children[0]) == ActionNode)
assert(tree.root.children[0].children[1].children[0].children[0].bet_history == '/cc/')
assert(len(tree.root.children[0].children[1].children[0].children[0].children) == 2)
assert(tree.root.children[0].children[1].children[0].children[0].player == 0)
assert(tree.root.children[0].children[1].children[0].children[0].fold_action is None)
assert(tree.root.children[0].children[1].children[0].children[0].call_action != None)
assert(tree.root.children[0].children[1].children[0].children[0].raise_action != None)
assert(tree.root.children[0].children[1].children[0].children[0].player_view == ('KhAs:/cc/:','KsAs:/cc/:','QsAs:/cc/:'))
# xAs:/cc/r
assert(type(tree.root.children[0].children[1].children[0].children[0].children[1]) == ActionNode)
assert(tree.root.children[0].children[1].children[0].children[0].children[1].bet_history == '/cc/r')
assert(len(tree.root.children[0].children[1].children[0].children[0].children[1].children) == 3)
assert(tree.root.children[0].children[1].children[0].children[0].children[1].player == 1)
assert(tree.root.children[0].children[1].children[0].children[0].children[1].fold_action != None)
assert(tree.root.children[0].children[1].children[0].children[0].children[1].call_action != None)
assert(tree.root.children[0].children[1].children[0].children[0].children[1].raise_action != None)
assert(tree.root.children[0].children[1].children[0].children[0].children[1].player_view == ('KhAs:/cc/r:','KsAs:/cc/r:','QsAs:/cc/r:'))
# xAs:/cc/rc
assert(type(tree.root.children[0].children[1].children[0].children[0].children[1].children[1]) == TerminalNode)
assert(tree.root.children[0].children[1].children[0].children[0].children[1].children[1].bet_history == '/cc/rc')
assert(tree.root.children[0].children[1].children[0].children[0].children[1].children[1].payoffs == { ((Card(13,1),),(Card(13,2),)): [0,0], ((Card(13,1),),(Card(12,1),)): [5,-5], ((Card(13,2),),(Card(13,1),)): [0,0], ((Card(13,2),),(Card(12,1),)): [5,-5], ((Card(12,1),),(Card(13,2),)): [-5,5], ((Card(12,1),),(Card(13,1),)): [-5,5] })
# xKh:/cc/rc
assert(type(tree.root.children[0].children[1].children[0].children[1].children[1].children[1]) == TerminalNode)
assert(tree.root.children[0].children[1].children[0].children[1].children[1].children[1].bet_history == '/cc/rc')
assert(tree.root.children[0].children[1].children[0].children[1].children[1].children[1].payoffs == { ((Card(13,1),),(Card(14,1),)): [5,-5], ((Card(13,1),),(Card(12,1),)): [5,-5], ((Card(14,1),),(Card(13,1),)): [-5,5], ((Card(14,1),),(Card(12,1),)): [5,-5], ((Card(12,1),),(Card(14,1),)): [-5,5], ((Card(12,1),),(Card(13,1),)): [-5,5] })
print 'All passed!'





