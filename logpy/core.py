import itertools as it
from functools import partial
from .util import transitive_get as walk
from .util import deep_transitive_get as walkstar
from .util import (dicthash, interleave, take, evalt, index, multihash, unique)
from toolz import assoc, groupby

from .variable import var, isvar
from .unification import reify, unify


#########
# Goals #
#########

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
    if not isvar(x) and not isvar(coll):
        if x in coll:
            return success
        return (lany,) + tuple((eq, x, item) for item in coll)
    if isvar(x) and not isvar(coll):
        return (lany,) + tuple((eq, x, item) for item in coll)
    raise EarlyGoalError()

################################
# Logical combination of goals #
################################

def lall(*goals):
    """ Logical all

    >>> from logpy.core import lall, membero
    >>> x = var('x')
    >>> g = lall(membero(x, (1,2,3)), membero(x, (2,3,4)))
    >>> tuple(g({}))
    ({~x: 2}, {~x: 3})
    """
    if not goals:
        return success
    if len(goals) == 1:
        return goals[0]
    def allgoal(s):
        g = goaleval(reify(goals[0], s))
        return unique(interleave(
                        goaleval(reify((lall,) + tuple(goals[1:]), ss))(ss)
                        for ss in g(s)),
                      key=dicthash)
    return allgoal

def lallfirst(*goals):
    """ Logical all - Run goals one at a time

    >>> from logpy.core import lall, membero
    >>> x = var('x')
    >>> g = lall(membero(x, (1,2,3)), membero(x, (2,3,4)))
    >>> tuple(g({}))
    ({~x: 2}, {~x: 3})
    """
    if not goals:
        return success
    if len(goals) == 1:
        return goals[0]
    def allgoal(s):
        for i, g in enumerate(goals):
            try:
                goal = goaleval(reify(g, s))
            except EarlyGoalError:
                continue
            other_goals = tuple(goals[:i] + goals[i+1:])
            return unique(interleave(goaleval(
                reify((lallfirst,) + other_goals, ss))(ss)
                for ss in goal(s)), key=dicthash)
        else:
            raise EarlyGoalError()
    return allgoal

def lany(*goals):
    """ Logical any

    >>> from logpy.core import lany, membero
    >>> x = var('x')
    >>> g = lany(membero(x, (1,2,3)), membero(x, (2,3,4)))
    >>> tuple(g({}))
    ({~x: 1}, {~x: 2}, {~x: 3}, {~x: 4})
    """
    if len(goals) == 1:
        return goals[0]
    return lanyseq(goals)

def lallearly(*goals):
    """ Logical all with goal reordering to avoid EarlyGoalErrors

    See also:
        EarlyGoalError
        earlyorder
    """
    return (lall,) + tuple(earlyorder(*goals))

def earlysafe(goal):
    """ Call goal be evaluated without raising an EarlyGoalError """
    try:
        goaleval(goal)
        return True
    except EarlyGoalError:
        return False

def earlyorder(*goals):
    """ Reorder goals to avoid EarlyGoalErrors

    All goals are evaluated.  Those that raise EarlyGoalErrors are placed at
    the end in a lallearly

    See also:
        EarlyGoalError
    """
    groups = groupby(earlysafe, goals)
    good = groups.get(True, [])
    bad  = groups.get(False, [])

    if not good:
        raise EarlyGoalError()
    elif not bad:
        return tuple(good)
    else:
        return tuple(good) + ((lallearly,) + tuple(bad),)

def conde(*goalseqs, **kwargs):
    """ Logical cond

    Goal constructor to provides logical AND and OR

    conde((A, B, C), (D, E)) means (A and B and C) or (D and E)

    See Also:
        lall - logical all
        lany - logical any
    """
    return (lany, ) + tuple((lallearly,) + tuple(gs) for gs in goalseqs)


def lanyseq(goals):
    """ Logical any with possibly infinite number of goals

    Note:  If using lanyseq with a generator you must call lanyseq, not include
    it in a tuple
    """
    def anygoal(s):
        anygoal.goals, local_goals = it.tee(anygoal.goals)
        def f(goals):
            for goal in goals:
                try:
                    yield goaleval(reify(goal, s))(s)
                except EarlyGoalError:
                    pass

        return unique(interleave(f(local_goals), [EarlyGoalError]),
                      key=dicthash)
    anygoal.goals = goals

    return anygoal

def condeseq(goalseqs):
    """ Like conde but supports generic (possibly infinite) iterator of goals"""
    return (lanyseq, ((lallearly,) + tuple(gs) for gs in goalseqs))

########################
# User level execution #
########################

def run(n, x, *goals, **kwargs):
    """ Run a logic program.  Obtain n solutions to satisfy goals.

    n     - number of desired solutions.  See ``take``
            0 for all
            None for a lazy sequence
    x     - Output variable
    goals - a sequence of goals.  All must be true

    >>> from logpy import run, var, eq
    >>> x = var()
    >>> run(1, x, eq(x, 1))
    (1,)
    """
    results = map(partial(reify, x), goaleval(lallearly(*goals))({}))
    return take(n, unique(results, key=multihash))

###################
# Goal Evaluation #
###################

class EarlyGoalError(Exception):
    """ A Goal has been constructed prematurely

    Consider the following case

    >>> from logpy import run, eq, membero, var
    >>> x, coll = var(), var()
    >>> run(0, x, (membero, x, coll), (eq, coll, (1, 2, 3))) # doctest: +SKIP

    The first goal, membero, iterates over an infinite sequence of all possible
    collections.  This is unproductive.  Rather than proceed, membero raises an
    EarlyGoalError, stating that this goal has been called early.

    The goal constructor lallearly Logical-All-Early will reorder such goals to
    the end so that the call becomes

    >>> run(0, x, (eq, coll, (1, 2, 3)), (membero, x, coll)) # doctest: +SKIP

    In this case coll is first unified to ``(1, 2, 3)`` then x iterates over
    all elements of coll, 1, then 2, then 3.

    See Also:
        lallearly
        earlyorder
    """

def goalexpand(goalt):
    """ Expand a goal tuple until it can no longer be expanded

    >>> from logpy.core import var, membero, goalexpand
    >>> from logpy.util import pprint
    >>> x = var('x')
    >>> goal = (membero, x, (1, 2, 3))
    >>> print(pprint(goalexpand(goal)))
    (lany, (eq, ~x, 1), (eq, ~x, 2), (eq, ~x, 3))
    """
    tmp = goalt
    while isinstance(tmp, tuple) and len(tmp) >= 1 and not callable(tmp):
        goalt = tmp
        tmp = goalt[0](*goalt[1:])
    return goalt


def goaleval(goal):
    """ Expand and then evaluate a goal

    Idempotent

    See also:
       goalexpand
    """
    if callable(goal):          # goal is already a function like eq(x, 1)
        return goal
    if isinstance(goal, tuple): # goal is not yet evaluated like (eq, x, 1)
        egoal = goalexpand(goal)
        # from logpy.util import pprint
        # print(pprint(egoal))
        return egoal[0](*egoal[1:])
    raise TypeError("Expected either function or tuple")
