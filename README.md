pyCFR
=====

A python implementation of Counterfactual Regret Minimization (CFR) [1] for flop-style poker games like Texas Hold'em, Leduc, and Kuhn poker. The library currently implements vanilla CFR [1], Chance Sampling (CS) CFR [1,2], Outcome Sampling (CS) CFR [2], and Public Chance Sampling (PCS) CFR [3].

Note that this library is intended to automatically support relatively small games. It is written in pure python and is not optimized for speed nor memory usage. Full-scale Texas Hold'em will likely be too slow and too big to handle. You should use this library if you want to learn about CFR, you are doing research on toy problems, or you want to sanity check your implementation on a poker variant where no optimized code is publicly available.

Creating a game tree
--------------------
To generate a tree for a game, simply specify the rules of the game:

```python
from pokertrees import *
from pokergames import *
players = 2
deck = [Card(14,1),Card(13,2),Card(13,1),Card(12,1)]
rounds = [RoundInfo(holecards=1,boardcards=0,betsize=2,maxbets=[2,2]),RoundInfo(holecards=0,boardcards=1,betsize=4,maxbets=[2,2])]
ante = 1
blinds = [1,2]
gamerules = GameRules(players, deck, rounds, ante, blinds, handeval=leduc_eval)
gametree = GameTree(gamerules)
gametree.build()
```

Or use one of the pre-built games:

```python
from pokergames import *
gametree = leduc_gametree()
```

Evaluating a strategy profile
-----------------------------
You can calculate the expected value of a set of strategies for a game:

```python
from pokertrees import *
from pokergames import *
from pokerstrategy import *
rules = leduc_rules()

# load first player strategy
s0 = Strategy(0)
s0.load_from_file('strategies/leduc/0.strat')

# load second player strategy
s1 = Strategy(1)
s1.load_from_file('strategies/leduc/1.strat')

# Create a strategy profile for this game
profile = StrategyProfile(rules, [s0,s1])

ev = profile.expected_value()
```

Getting the best response strategy
----------------------------------
Given a strategy profile, you can calculate the best response strategy for each agent:

```python
from pokertrees import *
from pokergames import *
from pokerstrategy import *
rules = leduc_rules()

# load first player strategy
s0 = Strategy(0)
s0.load_from_file('strategies/leduc/0.strat')

# load second player strategy
s1 = Strategy(1)
s1.load_from_file('strategies/leduc/1.strat')

# Create a strategy profile for this game
profile = StrategyProfile(rules, [s0,s1])

# Calculates the best response for every agent and the value of that response
brev = profile.best_response()

# The first element is a StrategyProfile of all the best responses
best_response = brev[0]

# The second element is a list of expected values of the responses vs. the original strategy profile
expected_values = brev[1]
```

The underlying implementation of the best response calculation uses a generalized version of the public tree algorithm presented in [4].

Finding a Nash equilibrium
--------------------------
Given the rules for a game, you can run the Counterfactual Regret (CFR) Minimization algorithm:

```python
# Get the rules of the game
hskuhn = half_street_kuhn_rules()

# Create the CFR minimizer
from  pokercfr import CounterfactualRegretMinimizer
cfr = CounterfactualRegretMinimizer(hskuhn)

# Run a number of iterations, determining the exploitability of the agents periodically
iterations_per_block = 1000
blocks = 10
for block in range(blocks):
    print 'Iterations: {0}'.format(block * iterations_per_block)
    cfr.run(iterations_per_block)
    result = cfr.profile.best_response()
    print 'Best response EV: {0}'.format(result[1])
    print 'Total exploitability: {0}'.format(sum(result[1]))

# The final result is a strategy profile of epsilon-optimal agents
nash_strategies = cfr.profile
```

Tests
-----
Tests for the game tree code are implemented in the `tests` directory. WARNING: Tests using Leduc poker are slow due to the size of the game.

- test_gametree.py - Tests the game tree functionality against a leduc-like game and verifies some branches are built as expected.

- test_strategy.py - Tests the strategy functionality by loading some pre-computed near-optimal strategies for Leduc poker and a default equal-probability policy.

- test_cfr.py - Tests the CFR minimizer functionality by running it on half-street Kuhn poker and Leduc poker. WARNING: Leduc poker is slow due to the size of the game.

- test_cscfr.py - Tests the Chance Sampling (CS) CFR minimizer functionality by running it on half-street Kuhn poker and Leduc poker. 

- test_oscfr.py - Tests the Outcome Sampling (OS) CFR minimizer functionality by running it on half-street Kuhn poker and Leduc poker.

- test_pcscfr.py - Tests the Public Chance Sampling (PCS) CFR minimizer functionality by running it on half-street Kuhn poker and Leduc poker.

Note the tests are intended to be run from the main directory, e.g. `python test/test_gametree.py`. They make some assumptions about relative paths when importing modules and loading and saving files.

TODO
----
The following is a list of items that still need to be implemented:

- Add no-limit poker games
- Average Strategy CFR (AS-CFR) for no-limit games
- Add test cases for games where additional holecards come after the first round when there may be a variable number of players. It may currently work, but it's untested on any of the implemented CFR variants.


Contributors
------------

Wesley Tansey

Hand evaluator code courtesy of [Alvin Liang's library](https://github.com/aliang/pokerhand-eval).




References
----------
[1] Zinkevich, M., Johanson, M., Bowling, M., & Piccione, C. (2008). Regret minimization in games with incomplete information. Advances in neural information processing systems, 20, 1729-1736.

[2] Lanctot, M., Waugh, K., Zinkevich, M., & Bowling, M. (2009). Monte Carlo sampling for regret minimization in extensive games. Advances in Neural Information Processing Systems, 22, 1078-1086.

[3] Johanson, M., Bard, N., Lanctot, M., Gibson, R., & Bowling, M. (2012). Efficient Nash equilibrium approximation through Monte Carlo counterfactual regret minimization. In Proceedings of the 11th International Conference on Autonomous Agents and Multiagent Systems-Volume 2 (pp. 837-846). International Foundation for Autonomous Agents and Multiagent Systems.

[4] Johanson, M., Waugh, K., Bowling, M., & Zinkevich, M. (2011). Accelerating best response calculation in large extensive games. In Proceedings of the Twenty-Second international joint conference on Artificial Intelligence-Volume Volume One (pp. 258-265). AAAI Press.