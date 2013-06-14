class Account(object):
    def __init__(self, first, last, id, balance):
        self.first = first
        self.last = last
        self.id = id
        self.balance = balance

    def info(self):
        return (self.first, self.last, self.id, self.balance)

    def __eq__(self, other):
        return self.info() == other.info()

    def __hash__(self):
        return hash((type(self), self.info()))

    def __str__(self):
        return "Account: %s %s, id %d, balance %d" % self.info()

    __repr__ = __str__
