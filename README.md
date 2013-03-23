pyCFR
=====

A python implementation of Counterfactual Regret Minimization for flop-style poker games like Texas Hold'em, Leduc, and Kuhn poker.

Note that this library is intended for *very* simple games. It is written in pure python and is not optimized for speed nor memory usage. Full-scale Texas Hold'em will likely be too slow and too big to handle.

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
gametree = leduc()
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

Tests
-----
Tests for the game tree code are implemented in the `tests` directory.

- test_gametree.py - Tests the game tree functionality against a leduc-like game and verifies some branches are built as expected.

- test_strategy.py - Tests the strategy functionality by loading some pre-computed near-optimal strategies for Leduc poker and a default equal-probability policy.

Note the tests are intended to be run from the main directory, e.g. `python test/test_gametree.py`. They make some assumptions about relative paths when importing modules and loading and saving files.

TODO
----
The following is a list of items that still need to be implemented:

- Best response
- Exploitability (EV of BR)
- CFR
- MC-CFR
- Pretty print game tree
- Simulator from game tree


Contributors
------------

Wesley Tansey

Hand evaluator code courtesy of [Alvin Liang's library](https://github.com/aliang/pokerhand-eval).