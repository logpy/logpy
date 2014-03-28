from .core import (var, isvar, eq, EarlyGoalError, conde, condeseq, lany, lall,
        lallearly, fail, success)
from .util import unique
import itertools as it

def heado(x, coll):
    """ x is the head of coll

    See also:
        heado
        conso
    """
    if not isinstance(coll, tuple):
        raise EarlyGoalError()
    if isinstance(coll, tuple) and len(coll) >= 1:
        return (eq, x, coll[0])
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
        return (eq, x, coll[1:])
    else:
        return fail

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

def permuteq(a, b, eq2=eq):
    """ Equality under permutation

    For example (1, 2, 2) equates to (2, 1, 2) under permutation
    >>> from logpy import var, run, permuteq
    >>> x = var()
    >>> run(0, x, permuteq(x, (1, 2)))
    ((1, 2), (2, 1))

    >>> run(0, x, permuteq((2, 1, x), (2, 1, 2)))
    (2,)
    """
    if isinstance(a, tuple) and isinstance(b, tuple):
        if len(a) != len(b):
            return fail
        elif set(a) == set(b) and len(set(a)) == len(a):
            return success
        else:
            c, d = a, b
            try:
                c, d = tuple(sorted(c)), tuple(sorted(d))
            except:
                pass
            if len(c) == 1:
                return (eq2, c[0], d[0])
            return condeseq((
                   ((eq2, c[i], d[0]), (permuteq, c[0:i] + c[i+1:], d[1:], eq2))
                        for i in range(len(c))))

    if isvar(a) and isvar(b):
        raise EarlyGoalError()

    if isvar(a) or isvar(b):
        if isinstance(b, tuple):
            c, d = a, b
        elif isinstance(a, tuple):
            c, d = b, a

        return (condeseq, ([eq(c, perm)]
                           for perm in unique(it.permutations(d, len(d)))))

def seteq(a, b, eq2=eq):
    """ Set Equality

    For example (1, 2, 3) set equates to (2, 1, 3)

    >>> from logpy import var, run, seteq
    >>> x = var()
    >>> run(0, x, seteq(x, (1, 2)))
    ((1, 2), (2, 1))

    >>> run(0, x, seteq((2, 1, x), (3, 1, 2)))
    (3,)
    """
    ts = lambda x: tuple(set(x))
    if not isvar(a) and not isvar(b):
        return permuteq(ts(a), ts(b), eq2)
    elif not isvar(a):
        return permuteq(ts(a), b, eq2)
    elif not isvar(b):
        return permuteq(a, ts(b), eq2)
    else:
        return permuteq(a, b, eq2)

    raise Exception()


def goalify(func):
    """ Convert Python function into LogPy goal

    >>> from logpy import run, goalify, var, membero
    >>> typo = goalify(type)
    >>> x = var('x')
    >>> run(0, x, membero(x, (1, 'cat', 'hat', 2)), (typo, x, str))
    ('cat', 'hat')

    Goals go both ways.  Here are all of the types in the collection

    >>> typ = var('typ')
    >>> results = run(0, typ, membero(x, (1, 'cat', 'hat', 2)), (typo, x, typ))
    >>> print([result.__name__ for result in results])
    ['int', 'str']
    """
    def funco(inputs, out):
        if isvar(inputs):
            raise EarlyGoalError()
        else:
            if isinstance(inputs, (tuple, list)):
                return (eq, func(*inputs), out)
            else:
                return (eq, func(inputs), out)
    return funco

typo = goalify(type)
isinstanceo = goalify(isinstance)


"""
-This is an attempt to create appendo.  It does not currently work.
-As written in miniKanren, appendo uses LISP machinery not present in Python
-such as quoted expressions and macros for short circuiting.  I have gotten
-around some of these issues but not all.  appendo is a stress test for this
-implementation
"""

def appendo(l, s, ls):
    """ Byrd thesis pg. 247 """
    a, d, res = [var() for i in range(3)]
    return (lany, (lall, (eq, l, ()), (eq, s, ls)),
                  (lallearly, (conso, a, d, l), (conso, a, res, ls), (appendo, d, s, res)))
