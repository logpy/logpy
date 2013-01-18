import itertools as it
from util import transitive_get as walk
from util import deep_transitive_get as walkstar
from util import (assoc, unique, unique_dict, interleave, take, evalt, isempty,
        intersection)

class Var(object):
    """ Logic Variable """

    def __new__(cls, *token):
        if len(token) == 0:
            token = wild()
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

var = lambda *args: Var(*args)
isvar = lambda t: isinstance(t, Var)

class wild(object):
    pass

def reify(e, s):
    if isvar(e):
        return walkstar(e, s)
    elif isinstance(e, tuple):
        return tuple(reify(arg, s) for arg in e)
    else:
        return e

def unify(u, v, s):  # no check at the moment
    """ Find substitution so that u == v while satisfying s

    >>> unify((1, x), (1, 2), {})
    {x: 2}
    """
    u = walk(u, s)
    v = walk(v, s)
    if u == v:
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

def conde(*goalseqs):
    """ Logical cond

    Goal constructor to provides logical AND and OR

    conde((A, B, C), (D, E)) means (A and B and C) or (D and E)
    """
    return condeseq(goalseqs)

def condeseq(goalseqs):
    """ Like conde but supports generic (possibly infinite) iterator of goals"""
    def goal_conde(s):
        return unique_dict(interleave(bindstar((s,), *goals)
                                     for goals in goalseqs))
    return goal_conde

def bind(stream, goal):
    """ Bind a goal to a stream

    inputs:
        stream - sequence of substitutions (dicts)
        goal   - function :: substitution -> stream

    """
    return unique_dict(interleave(it.imap(goaleval(goal), stream)))

def bindstar(stream, *goals):
    """ Bind many goals to a stream

    See Also:
        bind
    """
    for goal in goals:
        # Short circuit in case of empty stream
        a, stream = it.tee(stream, 2)
        if isempty(a):
            return stream
        # Bind stream to new goal
        stream = bind(stream, goal)
    return stream

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


# Goals

class EarlyGoalError():  pass

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

def seteq(a, b, eq=eq):
    """ Set Equality

    For example (1, 2, 3) set equates to (2, 1, 3)

    >>> from logpy import var, run, seteq
    >>> x = var()
    >>> run(0, x, seteq(x, (1, 2)))
    ((1, 2), (2, 1))
    """
    if isinstance(a, tuple) and isinstance(b, tuple):
        if set(a) == set(b):
            return success
        else:
            return fail

    if isvar(a) and isvar(b):
        raise EarlyGoalError()

    if isvar(a) and isinstance(b, tuple):
        c, d = a, b
    if isvar(b) and isinstance(a, tuple):
        c, d = b, a

    return condeseq([eq(c, perm)] for perm in it.permutations(d, len(d)))

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

class Relation(object):
    def __init__(self):
        self.facts = set()
        self.index = dict()

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
        subsets = [self.index[key] for key in enumerate(args)
                                   if  key in self.index]
        if subsets:     # we are able to reduce the pool early
            facts = intersection(*sorted(subsets, key=len))
        else:
            facts = self.facts
        return conde(*[[eq(a, b) for a, b in zip(args, fact)]
                                 for fact in facts])

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

class pair(tuple):
    def __new__(cls, head, tail):
        obj = tuple.__new__(cls)
        obj.head = head
        obj.tail = tail
        return obj

    def __getitem__(self, key):
        if key == 0:
            return self.head
        raise NotImplementedError()

    def __getslice__(self, a, b):
        if a == 1 and b > 100:
            return self.tail
        raise NotImplementedError()

    def __iter__(self):
        yield self.head
        for i in self.tail:
            yield i


def conso(h, t, l):
    if isinstance(l, tuple) and len(l) >= 1:
        return conde([(eq, h, l[0]), (eq, t, l[1:])])
    if isinstance(t, tuple):
        return eq((h,) + t, l)
    return eq(pair(h, t), l)

"""
-This is an attempt to create appendo.  It does not currently work.
-As written in miniKanren, appendo uses LISP machinery not present in Python
-such as quoted expressions and macros for short circuiting.  I have gotten
-around some of these issues but not all.  appendo is a stress test for this
-implementation
"""

def heado(x, coll):
    if isinstance(coll, tuple) and len(coll) >= 1:
        return eq(x, coll[0])
    else:
        return fail

def tailo(x, coll):
    if isinstance(coll, tuple) and len(coll) >= 1:
        return eq(x, coll[1:])
    else:
        return fail

def appendo(l, s, ls):
    """ Byrd thesis pg. 247 """
    a, d, res = [var(wild()) for i in range(3)]
    return conde((eq(l, ()), eq(s, ls)),
                 ((heado, a, l),   (tailo, d, l),
                  (heado, a, ls), (tailo, res, ls),
                  (appendo, d, s, res)))
