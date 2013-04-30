import sys
import os
sys.path.insert(0,os.path.realpath('.'))
from pokerstrategy import *
from pokergames import *
from pokercfr import *

def near(val, expected, distance=0.0001):
    return val >= (expected - distance) and val <= (expected + distance)

print ''
print ''
print 'Testing Public Chance Sampling (PCS) CFR'
print ''
print ''
"""
print 'Computing NE for Half-Street Kuhn poker'

hskuhn = half_street_kuhn_rules()
cfr = PublicChanceSamplingCFR(hskuhn)
iterations_per_block = 1000
blocks = 10
for block in range(blocks):
    print 'Iterations: {0}'.format(block * iterations_per_block)
    cfr.run(iterations_per_block)
    result = cfr.profile.best_response()
    print 'Best response EV: {0}'.format(result[1])
    print 'Total exploitability: {0}'.format(sum(result[1]))
print cfr.profile.strategies[0].policy
print cfr.profile.strategies[1].policy
print cfr.counterfactual_regret
print 'Verifying P1 policy'
assert(near(cfr.profile.strategies[0].policy['Q:/:'][CALL], 2.0 / 3.0, 0.01))
assert(near(cfr.profile.strategies[0].policy['Q:/:'][RAISE], 1.0 / 3.0, 0.01))
assert(near(cfr.profile.strategies[0].policy['K:/:'][CALL], 1, 0.01))
assert(near(cfr.profile.strategies[0].policy['K:/:'][RAISE], 0, 0.01))
assert(near(cfr.profile.strategies[0].policy['A:/:'][CALL], 0, 0.01))
assert(near(cfr.profile.strategies[0].policy['A:/:'][RAISE], 1.0, 0.01))
print 'Verifying P2 policy'
assert(near(cfr.profile.strategies[1].policy['Q:/r:'][FOLD], 1.0, 0.01))
assert(near(cfr.profile.strategies[1].policy['Q:/r:'][CALL], 0, 0.01))
assert(near(cfr.profile.strategies[1].policy['K:/r:'][FOLD], 2.0 / 3.0, 0.01))
assert(near(cfr.profile.strategies[1].policy['K:/r:'][CALL], 1.0 / 3.0, 0.01))
assert(near(cfr.profile.strategies[1].policy['A:/r:'][FOLD], 0, 0.01))
assert(near(cfr.profile.strategies[1].policy['A:/r:'][CALL], 1.0, 0.01))

print 'Done!'
print ''
"""
print 'Computing NE for Leduc poker'
leduc = leduc_rules()

cfr = PublicChanceSamplingCFR(leduc)

iterations_per_block = 1000
blocks = 1000
for block in range(blocks):
    print 'Iterations: {0}'.format(block * iterations_per_block)
    cfr.run(iterations_per_block)
    result = cfr.profile.best_response()
    print 'Best response EV: {0}'.format(result[1])
    print 'Total exploitability: {0}'.format(sum(result[1]))
print 'Done!'
print ''