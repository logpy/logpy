from logpy.core import (isvar, assoc, walk, unify, unique_dict, bindstar,
        Relation, heado, conde, var, eq, fail, goaleval, lall, EarlyGoalError,
        condeseq, seteq, conso)
from logpy import core
from logpy.util import groupsizes

__all__ = ['associative', 'commutative', 'eq_assoccomm', 'opo']

associative = Relation()
commutative = Relation()

def assocunify(u, v, s, eq=core.eq):
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
    return tuple(l[0] if len(l) == 1 else (op,) + tuple(l) for l in lists)

def partition(tup, part):
    return [index(tup, ind) for ind in part]

def index(tup, ind):
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

def eq_assoc2(u, v, eq=core.eq):
    """ Goal for associative equality

    >>> from logpy import run, var
    >>> from logpy.assoccomm import eq_assoc as eq
    >>> x = var()
    >>> run(0, eq((add, 1, 2, 3), ('add', 1, x)))
    (('add', 2, 3),)
    """
    op = var()
    return conde([(core.eq, u, v)],
                 [(heado, op, u), (heado, op, v), (associative, op),
                  lambda s: assocunify(u, v, s, eq)])

def eq_comm2(u, v, eq=None):
    """ Goal for commutative equality

    >>> from logpy import run, var
    >>> from logpy.assoccomm import eq_comm as eq
    >>> x = var()
    >>> run(0, eq((add, 1, 2, 3), ('add', x, 1)))
    (('add', 2, 3), ('add', 3, 2))
    """
    eq = eq or eq_comm2
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

def eq_assoccomm2(u, v):
    """ Associative/Commutative eq

    Works like logic.core.eq but supports associative/commutative expr trees

    tree-format:  (op, *args)
    example:      (add, 1, 2, 3)

    State that operations are associative or commutative with relations

    >>> from logpy.assoccomm import eq_assoccomm as eq
    >>> from logpy.assoccomm import commutative, associative
    >>> from logpy import fact, run, var

    >>> fact(commutative, 'add')    # declare that 'add' is commutative

    >>> x = var
    >>> e1 = ('add', 1, 2, 3)
    >>> e2 = ('add', 1, x)
    >>> run(0, x, eq(e1, e2))
    (('add', 2, 3), ('add', 3, 2))
    """
    w = var()
    return lall((eq_comm2, u, w, eq_assoccomm2),
                (eq_assoc2, w, v, eq_assoccomm2))
