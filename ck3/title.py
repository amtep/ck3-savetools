from enum import IntEnum

class Rank(IntEnum):
    NoRank = 0
    Barony = 1
    County = 2
    Duchy = 3
    Kingdom = 4
    Empire = 5

    def from_letter(c):
        if c == 'b':
            return Rank.Barony
        if c == 'c':
            return Rank.County
        if c == 'd':
            return Rank.Duchy
        if c == 'k':
            return Rank.Kingdom
        if c == 'e':
            return Rank.Empire
        # TODO: look up in landed_titles/dynamic_templates/
        if c == 'x':
            return Rank.Duchy
        raise ValueError("unknown title rank")

class Title:
    def __init__(self, id, state):
        self.id = id
        self.state = state
        self.key = None
        self.rank = None

    def assign(self, key, token):
        if key == 'key':
            self.key = token.value
            self.rank = Rank.from_letter(self.key[0])

    def value(self, key, token):
        pass
