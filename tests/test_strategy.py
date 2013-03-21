import sys
import os
sys.path.insert(0,os.path.realpath('.'))
from pokerstrategy import *
from pokergames import *

hskuhn_gametree = half_street_kuhn()

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

print "Half-Street Kuhn"
print "Holecards: {0}".format(hskuhn_gametree.deal_holecards())
print "Nash0 vs. Nash1: {0}".format(StrategyProfile(hskuhn_gametree, [s0,s1]).expected_value())
print "Nash0 vs. Eq1: {0}".format(StrategyProfile(hskuhn_gametree, [s0,eq1]).expected_value())
print "Eq0 vs. Nash1: {0}".format(StrategyProfile(hskuhn_gametree, [eq0,s1]).expected_value())
print "Eq0 vs. Eq1: {0}".format(StrategyProfile(hskuhn_gametree, [eq0,eq1]).expected_value())
print ""

leduc_gametree = leduc()

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
eq0.build_default(leduc_gametree)
eq0.save_to_file('tests/leduc_eq0.strat')
assert(len(eq0.policy) == 144)

# Generate a default strategy for player 1
eq1 = Strategy(1)
eq1.build_default(leduc_gametree)
eq1.save_to_file('tests/leduc_eq1.strat')
assert(len(eq1.policy) == 144)

rand0 = Strategy(0)
rand0.load_from_file('strategies/leduc/random.strat')
rand1 = Strategy(1)
rand1.load_from_file('strategies/leduc/random.strat')

"""
All leduc test values were derived using the open_cfr implementation from UoAlberta
"""
print "Leduc"
result = StrategyProfile(leduc_gametree, [s0,s1]).expected_value()
print "Nash0 vs. Nash1 EV: {0}".format(result)
assert(result[0] >= -0.085653 and result[0] <= -0.085651)

print "Nash0 vs. Eq1 EV: {0}".format(StrategyProfile(leduc_gametree, [s0,eq1]).expected_value())
print "Eq0 vs. Nash1 EV: {0}".format(StrategyProfile(leduc_gametree, [eq0,s1]).expected_value())
print "Eq0 vs. Eq1: {0}".format(StrategyProfile(leduc_gametree, [eq0,eq1]).expected_value())

result = StrategyProfile(leduc_gametree, [s0,rand1]).expected_value()
print "Nash0 vs. Random: {0}".format(result)
assert(result[0] >= 0.591873 and result[0] <= 0.591875)

result = StrategyProfile(leduc_gametree, [rand0,s1]).expected_value()
print "Random vs. Nash1: {0}".format(result)
assert(result[0] >= -0.84791 and result[0] <= -0.84790)

print ""

print 'All passed!'