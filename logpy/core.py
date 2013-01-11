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
walk_star = deep_transitive_get

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
    """ Logical cond

    Goal constructor to provides logical AND and OR

    conde((A, B, C), (D, E)) means (A and B and C) or (D and E)
    """
    def goal_conde(s):
        return unique(it.chain(*[bindstar((s,), *goals) for goals in goalseqs]))
    return goal_conde

def bind(stream, goal):
    """ Bind a goal to a stream

    inputs:
        stream - sequence of substitutions (dicts)
        goal   - function :: substitution -> stream

    """
    return unique(it.chain(*it.imap(goal, stream))) # TODO: interleave

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
        return bindstar(bind(stream, evalt(goals[0])), *goals[1:])

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
    return take(n, (walk_star(x, s) for s in bindstar(({},), *goals)))

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
    def member_goal(s):
        x2 = walk(x, s)
        coll2 = walk(coll, s)
        return conde(*[[eq(x2, item)] for item in coll2])(s)
    return member_goal

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

'''
This is an attempt to create appendo.  It does not currently work.
As written in miniKanren, appendo uses LISP machinery not present in Python
such as quoted expressions and macros for short circuiting.  I have gotten
around some of these issues but not all.  appendo is a stress test for this
implementation

quoting:
    By convention we replace fn(arg1, arg2) with (fn, arg1, arg2) as the
    unevaluated form.  The function evalt evaluates such tuples.

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

def appendo(l, s, out):
    """ Byrd thesis pg. 267 """
    print l, s, out
    a, d, res = [var(wild()) for i in range(3)]
    return conde((eq(l, ()), eq(s, out)),
                 ((heado, a, l),   (tailo, d, l),
                  (heado, a, out), (tailo, res, out),
                  (appendo, d, s, res)))
'''
