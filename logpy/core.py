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
    """ A dummy variable, often used inside Vars """
    _id = 1

    def __init__(self):
        self.id = wild._id
        wild._id += 1

    def __str__(self):
        return "_%d"%self.id
    __repr__ = __str__

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

def conde(*goalseqs, **kwargs):
    """ Logical cond

    Goal constructor to provides logical AND and OR

    conde((A, B, C), (D, E)) means (A and B and C) or (D and E)
    """
    return (lany, ) + tuple((lallearly,) + tuple(gs) for gs in goalseqs)

def condeseq(goalseqs, **kwargs):
    """ Like conde but supports generic (possibly infinite) iterator of goals"""
    bindfn = kwargs.get('bindfn', binddefault)
    def goal_conde(s):
        return unique_dict(interleave(bindfn((s,), *goals)
                                     for goals in goalseqs))
    return goal_conde

def lall(*goals):
    """ Logical all

    >>> from logpy import lall, membero
    >>> g = lall(membero(x, (1,2,3), membero(x, (2,3,4))))
    >>> tuple(g({}))
    ({x: 2}, {x: 3})
    """
    if not goals:
        return success
    if len(goals) == 1:
        return goals[0]
    def allgoal(s):
        g = goaleval(reify(goals[0], s))
        return unique_dict(interleave(
            goaleval(reify((lall,) + tuple(goals[1:]), ss))(ss)
            for ss in g(s)))
    return allgoal

def lany(*goals):
    """ Logical any

    >>> from logpy import lall, membero
    >>> g = lany(membero(x, (1,2,3), membero(x, (2,3,4))))
    >>> tuple(g({}))
    ({x: 1}, {x: 2}, {x: 3}, {x: 4})
    """
    if len(goals) == 1:
        return goals[0]

    def anygoal(s):
        gs = []
        for goal in goals:
            try:
                gs.append(goaleval(reify(goal, s)))
            except EarlyGoalError:
                pass
        return interleave((g(s) for g in gs), [EarlyGoalError])
    return anygoal
    return lambda s: interleave(
            (goaleval(reify(goal, s))(s) for goal in goals), (EarlyGoalError,))

def lallearly(*goals):
    """ Logical all with goal reordering to avoid EarlyGoalErrors """
    return (lall,) + tuple(earlyorder(*goals))

def earlyorder(*goals):
    """ Reorder goals to avoid EarlyGoalErrors

    All goals are evaluated.  Those that raise EarlyGoalErrors are placed at
    the end in a lallearly
    """
    good, bad = [], []
    for goal in goals:
        try:
            goaleval(goal)
            good.append(goal)
        except EarlyGoalError:
            bad.append(goal)
    if not good:
        raise EarlyGoalError()
    else:
        if not bad:
            return tuple(good)
        else:
            return tuple(good) + ((lallearly,) + tuple(bad),)

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
binddefault = bindstar

def run(n, x, *goals, **kwargs):
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
    bindfn = kwargs.get('bindfn', binddefault)
    return take(n, unique(walkstar(x, s) for s in goaleval(lallearly(*goals))({})))

    # bindfn(({},), *goals)))


# Goals

class EarlyGoalError(Exception):  pass

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
    try:
        return (lany,) + tuple((eq, x, item) for item in coll)
    except TypeError:
        raise EarlyGoalError()

def seteq(a, b, eq=eq):
    """ Set Equality

    For example (1, 2, 3) set equates to (2, 1, 3)

    >>> from logpy import var, run, seteq
    >>> x = var()
    >>> run(0, x, seteq(x, (1, 2)))
    ((1, 2), (2, 1))

    >>> run(0, x, seteq((2, 1, x), (3, 1, 2)))
    (3,)
    """
    if isinstance(a, tuple) and isinstance(b, tuple):
        if set(a) == set(b):
            return success
        elif len(a) != len(b):
            return fail
        else:
            c, d = a, b
            return (condeseq, (((eq, cc, dd) for cc, dd in zip(c, perm))
                                     for perm in it.permutations(d, len(d))))

    if isvar(a) and isvar(b):
        raise EarlyGoalError()

    if isvar(a) and isinstance(b, tuple):
        c, d = a, b
    if isvar(b) and isinstance(a, tuple):
        c, d = b, a

    return (condeseq, ([eq(c, perm)] for perm in it.permutations(d, len(d))))

def goaleval(goal):
    """ Evaluate an possibly unevaluated goal

    See also:
        goal_tuple_eval
    """
    if callable(goal):          # goal is already a function like eq(x, 1)
        return goal
    if isinstance(goal, tuple): # goal is not yet evaluated like (eq, x, 1)
        egoal = goalexpand(goal)
        return egoal[0](*egoal[1:])
    raise TypeError("Expected either function or tuple")

def goalexpand(goalt):
    """ Expand a goal tuple """
    tmp = goalt
    while isinstance(tmp, tuple) and len(tmp) >= 1 and not callable(tmp):
        goalt = tmp
        tmp = goalt[0](*goalt[1:])
    return goalt



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
    def g(s):
        tup = reify(goalt, s)
        while isinstance(tup, tuple) and len(tup) >= 1 and callable(tup[0]):
            tup = evalt(tup)
        return tup(s)
    return g

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
        return (conde,) + tuple([[eq(a, b) for a, b in zip(args, fact)]
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

def conso(h, t, l):
    """ Logical cons -- l[0], l[1:] == h, t """
    if isinstance(l, tuple):
        if len(l) == 0:
            return fail
        else:
            return (conde, [(eq, h, l[0]), (eq, t, l[1:])])
    elif isinstance(t, tuple):
        return eq((h,) + t, l)
    else:
        raise EarlyGoalError()

"""
-This is an attempt to create appendo.  It does not currently work.
-As written in miniKanren, appendo uses LISP machinery not present in Python
-such as quoted expressions and macros for short circuiting.  I have gotten
-around some of these issues but not all.  appendo is a stress test for this
-implementation
"""

def heado(x, coll):
    """ x is the head of coll

    See also:
        heado
        conso
    """
    if not isinstance(coll, tuple):
        raise EarlyGoalError()
    if isinstance(coll, tuple) and len(coll) >= 1:
        return eq(x, coll[0])
    else:
        return fail

def tailo(x, coll):
    """ x is the tail of coll

    See also:
        heado
        conso
    """
    if not isinstance(coll, tuple):
        raise EarlyGoalError()
    if isinstance(coll, tuple) and len(coll) >= 1:
        return eq(x, coll[1:])
    else:
        return fail

def appendo(l, s, ls):
    """ Byrd thesis pg. 247 """
    a, d, res = [var() for i in range(3)]
    return (lany, (lall, (eq, l, ()), (eq, s, ls)),
                  (lallearly, (conso, a, d, l), (conso, a, res, ls), (appendo, d, s, res)))
