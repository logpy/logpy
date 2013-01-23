""" Associative and Commutative unification

>>> from logpy import run, var, fact
>>> from logpy.assoccomm import eq_assoccomm as eq
>>> from logpy.assoccomm import commutative, associative

>>> # Define some dummy Ops
>>> add = 'add'
>>> mul = 'mul'

>>> # Declare that these ops are commutative using the facts system
>>> fact(commutative, mul)
>>> fact(commutative, add)

>>> # Define some wild variables
>>> x, y = var('x'), var('y')

>>> # Two expressions to match
>>> pattern = (mul, (add, 1, x), y)                # (1 + x) * y
>>> expr    = (mul, 2, (add, 3, 1))                # 2 * (3 + 1)

>>> print run(0, (x,y), eq(pattern, expr))
((3, 2),)
"""

from logpy.core import (isvar, assoc, walk, unify, unique_dict, bindstar,
        Relation, heado, conde, var, eq, fail, goaleval, lall, EarlyGoalError,
        condeseq, seteq, conso)
from logpy import core
from logpy.util import groupsizes

__all__ = ['associative', 'commutative', 'eq_assoccomm']

associative = Relation()
commutative = Relation()

def assocunify(u, v, s, eq=core.eq):
    """ Associative Unification

    See Also:
        eq_assoccomm
    """

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

        parts = (groupsizes_to_partition(*gsizes) for gsizes
                                                  in  groupsizes(len(lg), len(sm)))
        ops = (makeops(op, partition(lg, part)) for part in parts)
        return condeseq([(eq, a, b) for a, b in zip(sm, lg2)] for lg2 in ops)(s)

    return ()

def makeops(op, lists):
    """ Construct operations from an op and parition lists

    >>> makeops('add', [(1, 2), (3, 4, 5)])
    (('add', 1, 2), ('add', 3, 4, 5))
    """
    return tuple(l[0] if len(l) == 1 else (op,) + tuple(l) for l in lists)

def partition(tup, part):
    """ Partition a tuple

    >>> partition("abcde", [[0,1], [4,3,2]])
    [('a', 'b'), ('e', 'd', 'c')]
    """
    return [index(tup, ind) for ind in part]

def index(tup, ind):
    """ Fancy indexing with tuples """
    return tuple(tup[i] for i in ind)

def groupsizes_to_partition(*gsizes):
    """
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

def operation(op):
    """ Either an associative or commutative operation """
    return conde([commutative(op)], [associative(op)])

def eq_assoc(u, v, eq=core.eq):
    """ Goal for associative equality

    >>> from logpy import run, var
    >>> from logpy.assoccomm import eq_assoc as eq

    >>> fact(commutative, 'add')    # declare that 'add' is commutative
    >>> fact(associative, 'add')    # declare that 'add' is associative

    >>> x = var()
    >>> run(0, eq(('add', 1, 2, 3), ('add', 1, x)))
    (('add', 2, 3),)
    """
    op = var()
    return conde([(core.eq, u, v)],
                 [(heado, op, u), (heado, op, v), (associative, op),
                  lambda s: assocunify(u, v, s, eq)])

def eq_comm(u, v, eq=None):
    """ Goal for commutative equality

    >>> from logpy import run, var
    >>> from logpy.assoccomm import eq_comm as eq

    >>> fact(commutative, 'add')    # declare that 'add' is commutative
    >>> fact(associative, 'add')    # declare that 'add' is associative

    >>> x = var()
    >>> run(0, eq(('add', 1, 2, 3), ('add', 2, x, 1)))
    (3,)
    """
    eq = eq or eq_comm
    op = var()
    utail = var()
    vtail = var()
    if isvar(u) and isvar(v):
        return (core.eq, u, v)
        raise EarlyGoalError()
    return (conde, ((core.eq, u, v),),
                   ((conso, op, utail, u),
                    (conso, op, vtail, v),
                    (commutative, op),
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
    w = var()
    return lall((eq_comm, u, w, eq_assoccomm),
                (eq_assoc, w, v, eq_assoccomm))
