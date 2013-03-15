""" Associative and Commutative unification

This module provides goals for associative and commutative unification.  It
accomplishes this through naively trying all possibilities.  This was built to
be used in the computer algebra systems SymPy and Theano.

>>> from logpy import run, var, fact
>>> from logpy.assoccomm import eq_assoccomm as eq
>>> from logpy.assoccomm import commutative, associative

>>> # Define some dummy Ops
>>> add = 'add'
>>> mul = 'mul'

>>> # Declare that these ops are commutative using the facts system
>>> fact(commutative, mul)
>>> fact(commutative, add)
>>> fact(associative, mul)
>>> fact(associative, add)

>>> # Define some wild variables
>>> x, y = var('x'), var('y')

>>> # Two expressions to match
>>> pattern = (mul, (add, 1, x), y)                # (1 + x) * y
>>> expr    = (mul, 2, (add, 3, 1))                # 2 * (3 + 1)

>>> print run(0, (x,y), eq(pattern, expr))
((3, 2),)
"""

from logpy.core import (isvar, assoc, walk, unify,
        conde, var, eq, fail, goaleval, lall, EarlyGoalError,
        condeseq, goaleval)
from logpy.goals import heado, seteq, conso, tailo
from logpy.facts import Relation
from logpy import core
from logpy.util import groupsizes, index

__all__ = ['associative', 'commutative', 'eq_assoccomm']

associative = Relation('associative')
commutative = Relation('commutative')

def assocunify(u, v, s, eq=core.eq, n=None):
    """ Associative Unification

    See Also:
        eq_assoccomm
    """

    if not isinstance(u, tuple) and not isinstance(v, tuple):
        res = unify(u, v, s)
        if res is not False:
            return (res,)  # TODO: iterate through all possibilities

    if isinstance(u, tuple) and isinstance(v, tuple):
        uop, u = u[0], u[1:]
        vop, v = v[0], v[1:]
        s = unify(uop, vop, s)
        if s is False:
            raise StopIteration()
        op = walk(uop, s)

        sm, lg = (u, v) if len(u) <= len(v) else (v, u)
        ops = assocsized(op, lg, len(sm))
        goal = condeseq([(eq, a, b) for a, b, in zip(sm, lg2)] for lg2 in ops)
        return goaleval(goal)(s)

    if isinstance(u, tuple):
        a, b = u, v
    if isinstance(v, tuple):
        a, b = v, u

    op, tail = a[0], a[1:]

    ns = [n] if n else range(2, len(a))
    knowns = (((op,) + x) for n in ns for x in assocsized(op, tail, n))

    goal = condeseq([(core.eq, b, k)] for k in knowns)
    return goaleval(goal)(s)

def assocsized(op, tail, n):
    """ All associative combinations of x in n groups """
    gsizess = groupsizes(len(tail), n)
    partitions = (groupsizes_to_partition(*gsizes) for gsizes in gsizess)
    return (makeops(op, partition(tail, part)) for part in partitions)

def makeops(op, lists):
    """ Construct operations from an op and parition lists

    >>> from logpy.assoccomm import makeops
    >>> makeops('add', [(1, 2), (3, 4, 5)])
    (('add', 1, 2), ('add', 3, 4, 5))
    """
    return tuple(l[0] if len(l) == 1 else (op,) + tuple(l) for l in lists)

def partition(tup, part):
    """ Partition a tuple

    >>> from logpy.assoccomm import partition
    >>> partition("abcde", [[0,1], [4,3,2]])
    [('a', 'b'), ('e', 'd', 'c')]
    """
    return [index(tup, ind) for ind in part]

def groupsizes_to_partition(*gsizes):
    """
    >>> from logpy.assoccomm import groupsizes_to_partition
    >>> groupsizes_to_partition(2, 3)
    [[0, 1], [2, 3, 4]]
    """
    idx = 0
    part = []
    for gs in gsizes:
        l = []
        for i in range(gs):
            l.append(idx)
            idx += 1
        part.append(l)
    return part

def eq_assoc(u, v, eq=core.eq, n=None):
    """ Goal for associative equality

    >>> from logpy import run, var, fact
    >>> from logpy.assoccomm import eq_assoc as eq

    >>> fact(commutative, 'add')    # declare that 'add' is commutative
    >>> fact(associative, 'add')    # declare that 'add' is associative

    >>> x = var()
    >>> run(0, x, eq(('add', 1, 2, 3), ('add', 1, x)))
    (('add', 2, 3),)
    """
    op = var()
    if isinstance(u, tuple) and isinstance(v, tuple):
        return conde([(core.eq, u, v)],
                     [(heado, op, u), (heado, op, v), (associative, op),
                      lambda s: assocunify(u, v, s, eq, n)])

    if isinstance(u, tuple) or isinstance(v, tuple):
        if isinstance(v, tuple):
            v, u = u, v
        return conde([(core.eq, u, v)],
                     [(heado, op, u), (associative, op),
                      lambda s: assocunify(u, v, s, eq, n)])

    return (core.eq, u, v)

def eq_comm(u, v, eq=None):
    """ Goal for commutative equality

    >>> from logpy import run, var, fact
    >>> from logpy.assoccomm import eq_comm as eq
    >>> from logpy.assoccomm import commutative, associative

    >>> fact(commutative, 'add')    # declare that 'add' is commutative
    >>> fact(associative, 'add')    # declare that 'add' is associative

    >>> x = var()
    >>> run(0, x, eq(('add', 1, 2, 3), ('add', 2, x, 1)))
    (3,)
    """
    eq = eq or eq_comm
    op = var()
    utail = var()
    vtail = var()
    if isvar(u) and isvar(v):
        return (core.eq, u, v)
        raise EarlyGoalError()
    if isinstance(v, tuple) and not isinstance(u, tuple):
        u, v = v, u
    return (conde, ((core.eq, u, v),),
                   ((heado, op, u),
                    (commutative, op),
                    (tailo, utail, u),
                    (conso, op, vtail, v),
                    (seteq, utail, vtail, eq)))

def eq_assoccomm(u, v):
    """ Associative/Commutative eq

    Works like logic.core.eq but supports associative/commutative expr trees

    tree-format:  (op, *args)
    example:      (add, 1, 2, 3)

    State that operations are associative or commutative with relations

    >>> from logpy.assoccomm import eq_assoccomm as eq
    >>> from logpy.assoccomm import commutative, associative
    >>> from logpy import fact, run, var

    >>> fact(commutative, 'add')    # declare that 'add' is commutative
    >>> fact(associative, 'add')    # declare that 'add' is associative

    >>> x = var()
    >>> e1 = ('add', 1, 2, 3)
    >>> e2 = ('add', 1, x)
    >>> run(0, x, eq(e1, e2))
    (('add', 2, 3), ('add', 3, 2))
    """
    if isinstance(u, tuple) and not isinstance(v, tuple) and not isvar(v):
        return fail
    if isinstance(v, tuple) and not isinstance(u, tuple) and not isvar(u):
        return fail
    if isinstance(u, tuple) and isinstance(v, tuple) and not u[0] == v[0]:
        return fail
    if isinstance(u, tuple) and not (u[0],) in associative.facts:
        return (eq, u, v)
    if isinstance(v, tuple) and not (v[0],) in associative.facts:
        return (eq, u, v)

    if isinstance(u, tuple) and isinstance(v, tuple):
        u, v = (u, v) if len(u) >= len(v) else (v, u)
        n = len(v)-1  # length of shorter tail
    else:
        n = None
    if isinstance(v, tuple) and not isinstance(u, tuple):
        u, v = v, u
    w = var()
    return lall((eq_assoc, u, w, eq_assoccomm, n),
                (eq_comm, v, w, eq_assoccomm))

