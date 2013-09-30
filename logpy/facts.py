from toolz import intersection, get, merge
from core import conde, reify, isvar

class Relation(object):
    _id = 0
    def __init__(self, name=None):
        self.facts = set()
        self.index = dict()
        if not name:
            name = "_%d"%Relation._id
            Relation._id += 1
        self.name = name

    def add_fact(self, *inputs):
        """ Add a fact to the knowledgebase.

        See Also:
            fact
            facts
        """
        fact = tuple(inputs)

        self.facts.add(fact)

        for key in enumerate(inputs):
            if key not in self.index:
                self.index[key] = set()
            self.index[key].add(fact)

    def __call__(self, *args):
        def f(s):
            args2 = reify(args, s)
            subsets = [self.index[key] for key in enumerate(args)
                                       if  key in self.index]
            if subsets:     # we are able to reduce the pool early
                facts = intersection(*sorted(subsets, key=len))
            else:
                facts = self.facts
            varinds = [i for i, arg in enumerate(args2) if isvar(arg)]
            valinds = [i for i, arg in enumerate(args2) if not isvar(arg)]
            vars = get(varinds, args2)
            vals = get(valinds, args2)
            assert not any(var in s for var in vars)

            return (merge(dict(zip(vars, get(varinds, fact))), s)
                              for fact in self.facts
                              if vals == get(valinds, fact))
        return f

    def __str__(self):
        return "Rel: " + self.name
    __repr__ = __str__


def fact(rel, *args):
    """ Declare a fact

    >>> from logpy import fact, Relation, var, run
    >>> parent = Relation()
    >>> fact(parent, "Homer", "Bart")
    >>> fact(parent, "Homer", "Lisa")

    >>> x = var()
    >>> run(1, x, parent(x, "Bart"))
    ('Homer',)
    """
    rel.add_fact(*args)

def facts(rel, *lists):
    """ Declare several facts

    >>> from logpy import fact, Relation, var, run
    >>> parent = Relation()
    >>> facts(parent,  ("Homer", "Bart"),
    ...                ("Homer", "Lisa"))

    >>> x = var()
    >>> run(1, x, parent(x, "Bart"))
    ('Homer',)
    """
    for l in lists:
        fact(rel, *l)

