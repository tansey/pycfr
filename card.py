import re

class Card:
    SUIT_TO_STRING = {
        1: "s",
        2: "h",
        3: "d",
        4: "c"
    }
    
    RANK_TO_STRING = {
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "T",
        11: "J",
        12: "Q",
        13: "K",
        14: "A"
    }
    
    STRING_TO_SUIT = dict([(v, k) for k, v in SUIT_TO_STRING.iteritems()])
    STRING_TO_RANK = dict([(v, k) for k, v in RANK_TO_STRING.iteritems()])
    
    REPR_RE = re.compile(r'\((.*?)\)')
    
    def __init__(self, rank, suit):
        """Create a card. Rank is 2-14, representing 2-A,
        while suit is 1-4 representing spades, hearts, diamonds, clubs"""
        self.rank = rank
        self.suit = suit
    
    def __repr__(self):
        return "<Card(%s%s)>" % (self.RANK_TO_STRING[self.rank], self.SUIT_TO_STRING[self.suit])
    
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.rank == other.rank and self.suit == other.suit)
    
    def __hash__(self):
        return hash((self.rank, self.suit))
    
    @classmethod
    def from_repr(cls, repr):
        """Return a card instance from repr.
        This is really dirty--it just matches between the parens.
        It's meant for debugging."""
        between_parens = re.search(cls.REPR_RE, repr).group(1)
        rank = cls.STRING_TO_RANK[between_parens[0].upper()]
        suit = cls.STRING_TO_SUIT[between_parens[1].lower()]
        return Card(rank, suit)
        