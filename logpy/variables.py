class Var(object):
    """ Logic Variable """

    _id = 1
    def __new__(cls, *token):
        if len(token) == 0:
            token = "_%s" % Var._id
            Var._id += 1
        elif len(token) == 1:
            token = token[0]

        obj = object.__new__(cls)
        obj.token = token
        return obj

    def __str__(self):
        return "~" + str(self.token)
    __repr__ = __str__

    def __eq__(self, other):
        return type(self) == type(other) and self.token == other.token

    def __hash__(self):
        return hash((type(self), self.token))

    def assoc(self, d, value):
        d = d.copy()
        d[self] = value
        return d


var = lambda *args: Var(*args)
vars = lambda n: [var() for i in range(n)]
isvar = lambda t: isinstance(t, Var)

