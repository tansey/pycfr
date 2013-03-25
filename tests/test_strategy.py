import sys
import os
sys.path.insert(0,os.path.realpath('.'))
from pokerstrategy import *
from pokergames import *

print 'Testing Strategy'

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
profile = StrategyProfile(hskuhn_rules, [eq0,eq1])
result = profile.best_response(1)
br = result[0]
ev = result[1]
print "Eq0 BR: {0}".format(ev)
assert(len(br.policy) == 6)
assert(br.probs('Q:/c:') == [0,1,0])
assert(br.probs('K:/c:') == [0,1,0])
assert(br.probs('A:/c:') == [0,1,0])
assert(br.probs('Q:/r:') == [1,0,0])
assert(br.probs('K:/r:') == [0,1,0])
assert(br.probs('A:/r:') == [0,1,0])
print ""

sys.exit(0)

leduc_rules = leduc_rules()
leduc_gt = leduc_gametree()

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
result = profile.best_response(1)
print "Nash0 BR: {0}".format(result[1])

result = profile.best_response(0)
print "Nash1 BR: {0}".format(result[1])

profile = StrategyProfile(leduc_rules, [eq0,eq1])
result = profile.best_response(1)
print "Eq0 BR: {0}".format(result[1])

result = profile.best_response(0)
print "Eq1 BR: {0}".format(result[1])

profile = StrategyProfile(leduc_rules, [rand0, rand1])
result = profile.best_response(1)
print "Rand0 BR: {0}".format(result[1])

result = profile.best_response(0)
print "Rand1 BR: {0}".format(result[1])

print ""

print 'All passed!'