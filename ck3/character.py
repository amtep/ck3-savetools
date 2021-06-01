class Character:
    def __init__(self, id):
        self.id = id
        self.death_date = None
        self.birth_date = None

    def assign(self, key, token):
        if key == 'dead_data/date':
            self.death_date = token.value
        elif key == 'birth':
            self.birth_date = token.value

    def value(self, key, token):
        pass

    def alive(self):
        return self.death_date is None

    def age(self, current):
        return self.birth_date.age(current)
