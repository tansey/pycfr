import sys
import os
sys.path.insert(0,os.path.realpath('.'))
from pokerstrategy import *
from pokergames import *

def near(val, expected):
    return val >= (expected - 0.0001) and val <= (expected + 0.0001)

def validate_strategy(s, filename):
    validation_strategy = Strategy(s.player)
    validation_strategy.load_from_file(filename)
    assert(s.policy == validation_strategy.policy)

print ''
print ''
print 'Testing Strategy'
print ''
print ''


print 'No-action game with 1 holecard followed by 1 boardcard'
players = 2
deck = [Card(14,1),Card(13,1),Card(12,1),Card(11,1)]
ante = 1
blinds = None
rounds = [RoundInfo(holecards=1,boardcards=1,betsize=1,maxbets=[0,0])]
no_action_rules = GameRules(players, deck, rounds, ante, blinds, handeval=leduc_eval, infoset_format=leduc_format)
no_action_gametree = GameTree(no_action_rules)
no_action_gametree.build()
s0 = Strategy(0)
s0.build_default(no_action_gametree)
s1 = Strategy(1)
s1.build_default(no_action_gametree)
profile = StrategyProfile(no_action_rules, [s0,s1])
expected_value = profile.expected_value()
#print 'Expected values: [{0:.9f},{1:.9f}]'.format(expected_value[0], expected_value[1])
print 'Expected values: [{0},{1}]'.format(expected_value[0], expected_value[1])
assert(expected_value >= (-0.0001,-0.0001) and expected_value <= (0.0001,0.0001))
best_responses = profile.best_response()
br = best_responses[0]
brev = best_responses[1]
#print 'Best responses: {0}'.format([r.policy for r in br.strategies])
print 'Best response EV: {0}'.format(brev)
assert(brev >= (-0.0001,-0.0001) and brev <= (0.0001,0.0001))
print 'All passed!'
print ''


hskuhn_rules = half_street_kuhn_rules()
hskuhn_gametree = half_street_kuhn_gametree()

s0 = Strategy(0)
s0.policy = { 'A:/:': [0,0,1], 'K:/:': [0,1,0], 'Q:/:': [0,2.0/3.0,1.0/3.0] }

s1 = Strategy(1)
s1.policy = { 'A:/r:': [0,1,0], 'K:/r:': [2.0/3.0,1.0/3.0,0], 'Q:/r:': [1,0,0], 'A:/c:': [0,1,0], 'K:/c:': [0,1,0], 'Q:/c:': [0,1,0] }

eq0 = Strategy(0)
eq0.build_default(hskuhn_gametree)
eq0.save_to_file('tests/hskuhn_eq0.strat')

eq1 = Strategy(1)
eq1.build_default(hskuhn_gametree)
eq1.save_to_file('tests/hskuhn_eq1.strat')

print "Half-Street Kuhn Expected Value"
print "Nash0 vs. Nash1: {0}".format(StrategyProfile(hskuhn_rules, [s0,s1]).expected_value())
print "Nash0 vs. Eq1: {0}".format(StrategyProfile(hskuhn_rules, [s0,eq1]).expected_value())
print "Eq0 vs. Nash1: {0}".format(StrategyProfile(hskuhn_rules, [eq0,s1]).expected_value())
print "Eq0 vs. Eq1: {0}".format(StrategyProfile(hskuhn_rules, [eq0,eq1]).expected_value())
print ""

print "Half-Street Kuhn Best Response"
overbet0 = Strategy(0)
overbet0.policy = { 'Q:/:': [0,0.5,0.5], 'K:/:': [0,1,0], 'A:/:': [0,0,1] }
overbet1 = Strategy(1)
overbet1.policy = { 'Q:/c:': [0,1,0], 'K:/c:': [0,1,0], 'A:/c:': [0,1,0], 'Q:/r:': [1,0,0], 'K:/r:': [0.5,0.5,0], 'A:/r:': [0,1,0] }
profile = StrategyProfile(hskuhn_rules, [overbet0,overbet1])
result = profile.best_response()
br = result[0].strategies[0]
ev = result[1][0]
print "Overbet0 BR EV: {0}".format(ev)
print br.policy
assert(len(br.policy) == 3)
assert(br.probs('Q:/:') == [0,1,0])
assert(br.probs('K:/:') == [0,1,0])
assert(br.probs('A:/:') == [0,0,1])
assert(near(ev, 1.0/12.0))

br = result[0].strategies[1]
ev = result[1][1]
print "Overbet1 BR: {0}".format(ev)
assert(len(br.policy) == 6)
assert(br.probs('Q:/c:') == [0,1,0])
assert(br.probs('K:/c:') == [0,1,0])
assert(br.probs('A:/c:') == [0,1,0])
assert(br.probs('Q:/r:') == [1,0,0])
assert(br.probs('K:/r:') == [0,1,0])
assert(br.probs('A:/r:') == [0,1,0])
assert(near(ev, 0))

print 'All passed!'
print ""

#sys.exit(0)

leduc_rules = leduc_rules()
leduc_gt = PublicTree(leduc_rules)
leduc_gt.build()

s0 = Strategy(0)
s0.load_from_file('strategies/leduc/0.strat')
# Test a couple of arbitrary values
assert(s0.probs('J:/:') == [0.000000000, 0.927357111, 0.072642889])
assert(s0.probs('KJ:/rrc/rr:') == [0.546821151, 0.453178849, 0.000000000])
# Verify we loaded all of infosets
assert(len(s0.policy) == 144)

s1 = Strategy(1)
s1.load_from_file('strategies/leduc/1.strat')
# Test a couple of arbitrary values
assert(s1.probs('J:/r:') == [0.819456679, 0.125672407, 0.054870914])
assert(s1.probs('KJ:/rrc/crr:') == [0.000031258, 0.999968742, 0.000000000])
# Verify we loaded all of infosets
assert(len(s1.policy) == 144)

# Generate a default strategy for player 0
eq0 = Strategy(0)
eq0.build_default(leduc_gt)
eq0.save_to_file('tests/leduc_eq0.strat')
assert(len(eq0.policy) == 144)

# Generate a default strategy for player 1
eq1 = Strategy(1)
eq1.build_default(leduc_gt)
eq1.save_to_file('tests/leduc_eq1.strat')
assert(len(eq1.policy) == 144)

rand0 = Strategy(0)
rand0.load_from_file('strategies/leduc/random.strat')
rand1 = Strategy(1)
rand1.load_from_file('strategies/leduc/random.strat')

"""
All leduc test values were derived using the open_cfr implementation from UoAlberta
"""
print "Leduc Expected Value"
profile = StrategyProfile(leduc_rules, [s0,s1])
profile.gametree = leduc_gt
result = profile.expected_value()
print "Nash0 vs. Nash1 EV: {0}".format(result)
assert(result[0] >= -0.085653 and result[0] <= -0.085651)

profile = StrategyProfile(leduc_rules, [s0,eq1])
profile.gametree = leduc_gt
result = profile.expected_value()
print "Nash0 vs. Eq1 EV: {0}".format(result)
assert(result[0] >= 0.59143 and result[0] <= 0.59145)

profile = StrategyProfile(leduc_rules, [eq0,eq1])
profile.gametree = leduc_gt
result = profile.expected_value()
print "Eq0 vs. Eq1: {0}".format(result)
assert(result[0] >= -0.078126 and result[0] <= -0.078124)

profile = StrategyProfile(leduc_rules, [eq0,s1])
profile.gametree = leduc_gt
result = profile.expected_value()
print "Eq0 vs. Nash1 EV: {0}".format(result)
assert(result[0] >= -0.840442 and result[0] <= -0.840440)

profile = StrategyProfile(leduc_rules, [s0,rand1])
profile.gametree = leduc_gt
result = profile.expected_value()
print "Nash0 vs. Random: {0}".format(result)
assert(result[0] >= 0.591873 and result[0] <= 0.591875)

profile = StrategyProfile(leduc_rules, [rand0,s1])
profile.gametree = leduc_gt
result = profile.expected_value()
print "Random vs. Nash1: {0}".format(result)
assert(result[0] >= -0.84791 and result[0] <= -0.84790)

print ""

print "Leduc Best Response"
profile = StrategyProfile(leduc_rules, [s0,s1])
result = profile.best_response()
br = result[0].strategies[0]
ev = result[1][0]
print "Nash0 BR EV: {0}".format(ev)
br.save_to_file('tests/leduc_nash0_br.strat')
assert(near(ev, -0.0854363))
validate_strategy(br, 'strategies/leduc/nash_br0.strat')

br = result[0].strategies[1]
ev = result[1][1]
print "Nash1 BR EV: {0}".format(ev)
br.save_to_file('tests/leduc_nash1_br.strat')
assert(near(ev, 0.0858749))
validate_strategy(br, 'strategies/leduc/nash_br1.strat')

profile = StrategyProfile(leduc_rules, [eq0,eq1])
result = profile.best_response()
br = result[0].strategies[0]
ev = result[1][0]
print "Eq0 BR EV: {0}".format(ev)
assert(near(ev, 2.0875))
validate_strategy(br, 'strategies/leduc/equal_br0.strat')

br = result[0].strategies[1]
ev = result[1][1]
print "Eq1 BR EV: {0}".format(ev)
assert(near(ev, 2.65972))
validate_strategy(br, 'strategies/leduc/equal_br1.strat')

profile = StrategyProfile(leduc_rules, [rand0, rand1])
result = profile.best_response()
br = result[0].strategies[0]
ev = result[1][0]
print "Rand0 BR: {0}".format(ev)
assert(near(ev, 2.14414))
validate_strategy(br, 'strategies/leduc/random_br0.strat')

br = result[0].strategies[1]
ev = result[1][1]
print "Rand1 BR: {0}".format(ev)
assert(near(ev, 3.21721))
validate_strategy(br, 'strategies/leduc/random_br1.strat')

print ""

print 'All passed!'
