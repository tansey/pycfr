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
holecards = 1
rounds = [RoundInfo(boardcards=0,betsize=1,maxbets=[2,2]),RoundInfo(boardcards=1,betsize=2,maxbets=[2,2])]
ante = 1
blinds = [1,2]
tree = GameTree(players, deck, holecards, rounds, ante, blinds, handeval=leduc_eval)
tree.build()
```

Or use one of the pre-built games:

```python
from pokergames import *
tree = leduc()
```

Tests
-----
Tests for the game tree code are implemented in the `tests` directory.

- test_gametree.py - Tests the game tree functionality against a leduc-like game and verifies some branches are built as expected.

- test_strategy.py - Tests the strategy functionality by loading some pre-computed near-optimal strategies for Leduc poker and a default equal-probability policy.

TODO
----
The following is a list of items that still need to be implemented:

- Expected value of a strategy profile
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