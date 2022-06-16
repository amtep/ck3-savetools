from ck3.title import Title, Rank

class Character:
    def __init__(self, id, state):
        self.id = id
        self.state = state
        self.female = False
        self.death_date = None
        self.birth_date = None
        self.title_ids = []
        self.child_ids = []
        self.real_father_id = None
        self.trait_ids = []
        self.flags = []
        self.primary_spouse_id = None
        self.siblings = []  # derived later

    def assign(self, key, token):
        if key == 'female':
            self.female = token.value == 'yes'
        elif key == 'dead_data/date':
            self.death_date = token.value
        elif key == 'birth':
            self.birth_date = token.value
        elif key == 'family_data/real_father':
            self.real_father_id = token.value
        elif key == "alive_data/variables/data//flag":
            self.flags.append(token.value)
        elif key == 'family_data/primary_spouse':
            self.primary_spouse_id = token.value

    def value(self, key, token):
        if key == 'landed_data/domain':
            self.title_ids.append(token.value)
        elif key == 'family_data/child':
            self.child_ids.append(token.value)
        elif key == 'traits':
            self.trait_ids.append(token.value)
        elif key == 'alive_data/variables/data//flag':
            self.flags.append(token.value)

    def alive(self):
        return self.death_date is None

    def age(self, current):
        if self.birth_date is None:
            raise ValueError("Character %d has no birth date" % self.id)
        return self.birth_date.age(current)

    def titles(self):
        return [ self.state.titles[t_id] for t_id in self.title_ids ]

    def rank(self):
        return max(( t.rank for t in self.titles() ), default=Rank.NoRank)

    def landed(self):
        return any(t.rank == Rank.Barony for t in self.titles())

    def children(self):
        return [ self.state.characters[c_id] for c_id in self.child_ids ]

    def real_children(self):
        if self.female:
            return self.children()
        children = [ c for c in self.children()
                     if c.real_father_id is None or c.real_father_id == self.id ]
        for c in self.state.characters.values():
            if c.real_father_id == self.id and c not in children:
                children.append(c)
        return children

    def real_father(self):
        if self.real_father_id is None:
            return None
        if self.real_father_id not in self.state.characters:
            return None
        return self.state.characters[self.real_father_id]
