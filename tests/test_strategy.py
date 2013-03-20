import sys
import os
sys.path.insert(0,os.path.realpath('.'))
from pokerstrategy import *
from pokergames import *

s0 = Strategy(0)
s0.load_from_file('strategies/leduc/0.strat')
# Test a couple of arbitrary values
assert(s0.probs('J:/:') == [0.072642889, 0.927357111, 0.000000000])
assert(s0.probs('KJ:/rrc/rr:') == [0.000000000, 0.453178849, 0.546821151])
# Verify we loaded all of infosets
assert(len(s0.policy) == 144)

s1 = Strategy(1)
s1.load_from_file('strategies/leduc/1.strat')
# Test a couple of arbitrary values
assert(s1.probs('J:/r:') == [0.054870914, 0.125672407, 0.819456679])
assert(s1.probs('KJ:/rrc/crr:') == [0.000000000, 0.999968742, 0.000031258])
# Verify we loaded all of infosets
assert(len(s1.policy) == 144)

# Generate a default strategy for player 0
equal_probs0 = Strategy(0)
equal_probs0.build_default(leduc())
equal_probs0.save_to_file('tests/equal_probs0.strat')
assert(len(equal_probs0.policy) == 144)

# Generate a default strategy for player 1
equal_probs1 = Strategy(1)
equal_probs1.build_default(leduc())
equal_probs1.save_to_file('tests/equal_probs1.strat')
assert(len(equal_probs1.policy) == 144)

print 'All passed!'