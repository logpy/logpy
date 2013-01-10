import itertools as it

class var(object):
    def __new__(cls, token):
        return (var, token)
class wild(object):
    pass
isvar = lambda t: isinstance(t, tuple) and len(t) >= 1 and t[0] is var

def transitive_get(key, d):
    while key in d:
        key = d[key]
    return key

def deep_transitive_get(key, d):
    key = transitive_get(key, d)
    if isvar(key):
        return key
    if isinstance(key, tuple):
        return tuple(map(lambda k: deep_transitive_get(k, d), key))
    return key


walk = transitive_get
walk_star = deep_transitive_get
""" Get the transitive value of v in s """

def assoc(dict, key, value):
    d = dict.copy()
    d[key] = value
    return d

def unify(u, v, s):  # no check at the moment
    u = walk(u, s)
    v = walk(v, s)
    if u is v:
        return s
    if isvar(u):
        return assoc(s, u, v)
    if isvar(v):
        return assoc(s, v, u)
    if isinstance(u, tuple) and isinstance(v, tuple):
        if len(u) != len(v):
            return False
        for uu, vv in zip(u, v):  # avoiding recursion
            s = unify(uu, vv, s)
            if s is False:
                return False
        return s
    return False

def unique(seq):
    seen = set()
    for item in seq:
        try:  # TODO, deal with dicts and hashability
            if item not in seen:
                seen.add(item)
                yield item
        except TypeError:
            yield item

# TODO: replace chain with interleave

def conde(*goalseqs):
    def goal_conde(s):
        return unique(it.chain(*[bindstar((s,), *goals) for goals in goalseqs]))
    return goal_conde

def bind(stream, goal):
    """ Filter a stream by a goal """
    return unique(it.chain(*it.imap(goal, stream))) # TODO: interleave

def bindstar(stream, *goals):
    if not goals:
        return stream
    a, b, stream = it.tee(stream, 3)
    if isempty(a):
        return stream
    else:
        return bindstar(bind(stream, evalt(goals[0])), *goals[1:])

def run(n, x, *goals):
    seq = (walk_star(x, s) for s in bindstar(({},), *goals))
    if isinstance(n, int) and n > 0:
        return tuple(it.islice(seq, 0, n))
    if n is None:
        return seq

# Goals
def fail(s):
    return ()
def success(s):
    return (s,)

def eq(u, v):
    def goal_eq(s):
        result = unify(u, v, s)
        if result is not False:
            yield result
    return goal_eq

def membero(x, coll):
    return conde(*[[eq(x, item)] for item in coll])

def heado(x, coll):
    def head_goal(s):
        x2 = walk(x, s)
        coll2 = walk(coll, s)
        if coll2:
            return eq(x2, coll2[0])(s)
        else:
            return fail(s)
    return head_goal

def tailo(x, coll):
    def tail_goal(s):
        x2 = walk(x, s)
        coll2 = walk(coll, s)
        if coll2:
            return eq(x2, coll2[1:])(s)
        else:
            return fail(s)
    return tail_goal

#def appendo(l, s, out):
#    """ Byrd thesis pg. 267 """
#    print l, s, out
#    a, d, res = [var(wild()) for i in range(3)]
#    return conde((eq(l, ()), eq(s, out)),
#                 ((heado, a, l),   (tailo, d, l),
#                  (heado, a, out), (tailo, res, out),
#                  (appendo, d, s, res)))

def evalt(t):
    """ Evaluate tuple if unevaluated

    >>> add = lambda x, y: x + y
    >>> evalt((add, 2, 3))
    5
    >>> evalt(add(2, 3))
    5
    """

    if isinstance(t, tuple) and len(t) >= 1 and callable(t[0]):
        return t[0](*t[1:])
    else:
        return t

def isempty(it):
    """ Is an iterable empty

    destructive.  Use with tee

    >>> from itertools import tee
    >>> it = range(3)
    >>> tmp, it = tee(it, 2)
    >>> isempty(tmp)
    False
    """
    try:
        next(iter(it))
        return False
    except StopIteration:
        return True

class Relation(object):
    def __init__(self, *args):
        self.args  = args
        self.facts = set()

    def add_fact(self, *inputs):
        if self.args and not len(inputs) == len(self.args):
            raise ValueError("Expected %d attributes"%len(self.args))
        self.facts.add(tuple(inputs))

    def __call__(self, *args):
        return conde(*[[eq(a, b) for a, b in zip(args, fact)]
                                 for fact in self.facts])
