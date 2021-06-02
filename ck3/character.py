from ck3.title import Title, Rank

class Character:
    def __init__(self, id, state):
        self.id = id
        self.state = state
        self.death_date = None
        self.birth_date = None
        self.title_ids = []

    def assign(self, key, token):
        if key == 'dead_data/date':
            self.death_date = token.value
        elif key == 'birth':
            self.birth_date = token.value

    def value(self, key, token):
        if key == 'landed_data/domain':
            self.title_ids.append(token.value)

    def alive(self):
        return self.death_date is None

    def age(self, current):
        return self.birth_date.age(current)

    def titles(self):
        return [ self.state.titles[t_id] for t_id in self.title_ids ]

    def rank(self):
        return max(( t.rank for t in self.titles() ), default=Rank.NoRank)

    def landed(self):
        return any(t.rank == Rank.Barony for t in self.titles())
