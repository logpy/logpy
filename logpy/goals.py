from core import (var, isvar, eq, EarlyGoalError, conde, condeseq, lany, lall,
        lallearly, fail, success)
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
    if isinstance(a, tuple) and isinstance(b, tuple):
        if set(a) == set(b):
            return success
        elif len(a) != len(b):
            return fail
        else:
            c, d = a, b
            if len(c) == 1:
                return (eq2, c[0], d[0])
            return (conde,) + tuple(
                    ((eq2, c[i], d[0]), (seteq, c[0:i] + c[i+1:], d[1:], eq2))
                        for i in range(len(c)))

    if isvar(a) and isvar(b):
        raise EarlyGoalError()

    if isvar(a) and isinstance(b, tuple):
        c, d = a, b
    if isvar(b) and isinstance(a, tuple):
        c, d = b, a

    return (condeseq, ([eq(c, perm)] for perm in it.permutations(d, len(d))))


def goalify(func):
    """ Convert Python function into LogPy goal

    >>> from logpy import run, goalify, var, membero
    >>> typo = goalify(type)
    >>> x = var('x')
    >>> run(0, x, membero(x, (1, 'cat', 'hat', 2)), (typo, x, str))
    ('cat', 'hat')
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
