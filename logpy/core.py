import itertools as it

class var(object):
    """ Logic Variable """

    def __new__(cls, *token):
        if len(token) == 0:
            token = wild()
        elif len(token) == 1:
            token = token[0]
        return (var, token)

isvar = lambda t: isinstance(t, tuple) and len(t) >= 1 and t[0] is var

class wild(object):
    pass

def transitive_get(key, d):
    """ Transitive dict.get

    >>> d = {1: 2, 2: 3, 3: 4}
    >>> d.get(1)
    2
    >>> transitive_get(1, d)
    4
    """
    while key in d:
        key = d[key]
    return key

def deep_transitive_get(key, d):
    """ Transitive get that propagates within tuples

    >>> d = {1: (2, 3), 2: 12, 3: 13}
    >>> transitive_get(1, d)
    (2, 3)
    >>> deep_transitive_get(1, d)
    (12, 13)
    """

    key = transitive_get(key, d)
    if isvar(key):
        return key
    if isinstance(key, tuple):
        return tuple(map(lambda k: deep_transitive_get(k, d), key))
    return key

walk = transitive_get
walkstar = deep_transitive_get

def reify(e, s):
    if isvar(e):
        return walkstar(e, s)
    if isinstance(e, tuple):
        return tuple(reify(arg, s) for arg in e)
    return e

def assoc(dict, key, value):
    d = dict.copy()
    d[key] = value
    return d

def unify(u, v, s):  # no check at the moment
    """ Find substitution so that u == v while satisfying s

    >>> unify((1, x), (1, 2), {})
    {x: 2}
    """
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

def unique_dict(seq):
    seen = set()
    for d in seq:
        h = hash(frozenset(d.items()))
        if h not in seen:
            seen.add(h)
            yield d

def unique(seq):
    seen = set()
    for item in seq:
        if item not in seen:
            seen.add(item)
            yield item

# TODO: replace chain with interleave

def conde(*goalseqs):
    """ Logical cond

    Goal constructor to provides logical AND and OR

    conde((A, B, C), (D, E)) means (A and B and C) or (D and E)
    """
    def goal_conde(s):
        return unique_dict(it.chain(*[bindstar((s,), *goals) for goals in goalseqs]))
    return goal_conde

def bind(stream, goal):
    """ Bind a goal to a stream

    inputs:
        stream - sequence of substitutions (dicts)
        goal   - function :: substitution -> stream

    """
    return unique_dict(it.chain(*it.imap(goal, stream))) # TODO: interleave

def bindstar(stream, *goals):
    """ Bind many goals to a stream

    See Also:
        bind
    """
    if not goals:
        return stream
    a, b, stream = it.tee(stream, 3)
    if isempty(a):
        return stream
    else:
        return bindstar(bind(stream, goaleval(goals[0])), *goals[1:])

def run(n, x, *goals):
    """ Run a logic program.  Obtain n solutions to satisfy goals.

    n     - number of desired solutions.  See ``take``
            0 for all
            None for a lazy sequence
    x     - Output variable
    goals - a sequence of goals.  All must be true

    >>> from logpy import run, var, eq
    >>> run(1, x, eq(x, 1))
    (1,)
    """
    return take(n, unique(walkstar(x, s) for s in bindstar(({},), *goals)))

def take(n, seq):
    if n is None:
        return seq
    if n == 0:
        return tuple(seq)
    return tuple(it.islice(seq, 0, n))


# Goals
def fail(s):
    return ()
def success(s):
    return (s,)

def eq(u, v):
    """ Goal such that u == v

    See also:
        unify
    """
    def goal_eq(s):
        result = unify(u, v, s)
        if result is not False:
            yield result
    return goal_eq

def membero(x, coll):
    """ Goal such that x is an item of coll """
    return conde(*[[eq(x, item)] for item in coll])

def goaleval(goal):
    """ Evaluate an possibly unevaluated goal

    See also:
        goal_tuple_eval
    """
    if callable(goal):          # goal is already a function like eq(x, 1)
        return goal
    if isinstance(goal, tuple): # goal is not yet evaluated like (eq, x, 1)
        return goal_tuple_eval(goal)
    raise TypeError("Expected either function or tuple")

def goal_tuple_eval(goalt):
    """ Evaluate an unevaluated goal tuple

    Converts a goal-tuple like (eq, x, 1) into a goal like eq(x, 1) so that the
    tuple first reifies against the input substitution.  This enables the use
    of unevaluated goals.

    >>> x, y = var(), var()
    >>> g = goal_tuple_eval((membero, x, y))

    This would fail if done as ``membero(x, y)`` because y is a var, not a
    collection.  goal_tuple_eval wait to evaluate membero until the last
    moment.  It uses the substitution given to the goal to first reify the
    goal tuple, replacing all variables with the current values in the
    substitution.

    See also:
        goaleval - safe to use on eq(x, 1) or (eq, x, 1)
    """
    return lambda s: evalt(reify(goalt, s))(s)

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
    def __init__(self):
        self.facts = set()

    def add_fact(self, *inputs):
        """ Add a fact to the knowledgebase.

        See Also:
            fact
            facts
        """
        self.facts.add(tuple(inputs))

    def __call__(self, *args):
        return conde(*[[eq(a, b) for a, b in zip(args, fact)]
                                 for fact in self.facts])

def fact(rel, *args):
    """ Declare a fact

    >>> from logpy import fact, Relation, var
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

    >>> from logpy import fact, Relation, var
    >>> parent = Relation()
    >>> facts(parent,  ("Homer", "Bart"),
    ...                ("Homer", "Lisa"))
    >>> x = var()
    >>> run(1, x, parent(x, "Bart"))
    ('Homer',)
    """
    for l in lists:
        fact(rel, *l)

"""
-This is an attempt to create appendo.  It does not currently work.
-As written in miniKanren, appendo uses LISP machinery not present in Python
-such as quoted expressions and macros for short circuiting.  I have gotten
-around some of these issues but not all.  appendo is a stress test for this
-implementation
"""

def heado(x, coll):
    if coll:
        return eq(x, coll[0])
    else:
        return fail

def tailo(x, coll):
    if coll:
        return eq(x, coll[1:])
    else:
        return fail

def appendo(l, s, out):
    """ Byrd thesis pg. 247 """
    a, d, res = [var(wild()) for i in range(3)]
    return conde((eq(l, ()), eq(s, out)),
                 ((heado, a, l),   (tailo, d, l),
                  (heado, a, out), (tailo, res, out),
                  (appendo, d, s, res)))
