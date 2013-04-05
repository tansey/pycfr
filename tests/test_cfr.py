import sys
import os
sys.path.insert(0,os.path.realpath('.'))
from pokerstrategy import *
from pokergames import *
from pokercfr import *

def near(val, expected):
    return val >= (expected - 0.0001) and val <= (expected + 0.0001)

print ''
print ''
print 'Testing CFR'
print ''
print ''

print 'Computer NE for Half-Street Kuhn poker'

hskuhn = half_street_kuhn_rules()
cfr = CounterfactualRegretMinimizer(hskuhn)
iterations_per_block = 1000
blocks = 10
for block in range(blocks):
    print 'Iterations: {0}'.format(block * iterations_per_block)
    cfr.run(iterations_per_block)
    result = cfr.profile.best_response()
    print 'Exploitability: {0}'.format(result[1])
print cfr.profile.strategies[0].policy
print cfr.profile.strategies[1].policy
print 'Done!'
print ''
sys.exit(0)
print 'Computing NE for Leduc poker'
leduc = leduc_rules()

cfr = CounterfactualRegretMinimizer(leduc)

iterations_per_block = 1000
blocks = 1000
for block in range(blocks):
    print 'Iterations: {0}'.format(block * iterations_per_block)
    cfr.run(iterations_per_block)
    result = cfr.profile.best_response()
    print 'Exploitability: {0}'.format(result[1])

print 'Done!'
print ''