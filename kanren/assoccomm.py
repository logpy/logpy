""" Associative and Commutative unification

This module provides goals for associative and commutative unification.  It
accomplishes this through naively trying all possibilities.  This was built to
be used in the computer algebra systems SymPy and Theano.

>>> from kanren import run, var, fact
>>> from kanren.assoccomm import eq_assoccomm as eq
>>> from kanren.assoccomm import commutative, associative

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

>>> print(run(0, (x,y), eq(pattern, expr)))
((3, 2),)
"""

from unification.utils import transitive_get as walk
from unification import isvar


from . import core
from .core import (unify, conde, var, eq, fail, lallgreedy, EarlyGoalError,
                   condeseq, goaleval)
from .goals import permuteq
from .facts import Relation
from .util import groupsizes, index
from .term import term, arguments, operator

associative = Relation('associative')
commutative = Relation('commutative')


def assocunify(u, v, s, eq=core.eq, n=None):
    """ Associative Unification

    See Also:
        eq_assoccomm
    """
    uop, uargs = op_args(u)
    vop, vargs = op_args(v)

    if not uop and not vop:
        res = unify(u, v, s)
        if res is not False:
            return (res, )  # TODO: iterate through all possibilities

    if uop and vop:
        s = unify(uop, vop, s)
        if s is False:
            return ().__iter__()
        op = walk(uop, s)

        sm, lg = (uargs, vargs) if len(uargs) <= len(vargs) else (vargs, uargs)
        ops = assocsized(op, lg, len(sm))
        goal = condeseq([(eq, a, b) for a, b, in zip(sm, lg2)] for lg2 in ops)
        return goaleval(goal)(s)

    if uop:
        op, tail = uop, uargs
        b = v
    if vop:
        op, tail = vop, vargs
        b = u

    ns = [n] if n else range(2, len(tail) + 1)
    knowns = (build(op, x) for n in ns for x in assocsized(op, tail, n))

    goal = condeseq([(core.eq, b, k)] for k in knowns)
    return goaleval(goal)(s)


def assocsized(op, tail, n):
    """ All associative combinations of x in n groups """
    gsizess = groupsizes(len(tail), n)
    partitions = (groupsizes_to_partition(*gsizes) for gsizes in gsizess)
    return (makeops(op, partition(tail, part)) for part in partitions)


def makeops(op, lists):
    """ Construct operations from an op and parition lists

    >>> from kanren.assoccomm import makeops
    >>> makeops('add', [(1, 2), (3, 4, 5)])
    (('add', 1, 2), ('add', 3, 4, 5))
    """
    return tuple(l[0] if len(l) == 1 else build(op, l) for l in lists)


def partition(tup, part):
    """ Partition a tuple

    >>> from kanren.assoccomm import partition
    >>> partition("abcde", [[0,1], [4,3,2]])
    [('a', 'b'), ('e', 'd', 'c')]
    """
    return [index(tup, ind) for ind in part]


def groupsizes_to_partition(*gsizes):
    """
    >>> from kanren.assoccomm import groupsizes_to_partition
    >>> groupsizes_to_partition(2, 3)
    [[0, 1], [2, 3, 4]]
    """
    idx = 0
    part = []
    for gs in gsizes:
        l_ = []
        for i in range(gs):
            l_.append(idx)
            idx += 1
        part.append(l_)
    return part


def eq_assoc(u, v, eq=core.eq, n=None):
    """ Goal for associative equality

    >>> from kanren import run, var, fact
    >>> from kanren.assoccomm import eq_assoc as eq

    >>> fact(commutative, 'add')    # declare that 'add' is commutative
    >>> fact(associative, 'add')    # declare that 'add' is associative

    >>> x = var()
    >>> run(0, x, eq(('add', 1, 2, 3), ('add', 1, x)))
    (('add', 2, 3),)
    """
    uop, _ = op_args(u)
    vop, _ = op_args(v)
    if uop and vop:
        return conde([(core.eq, u, v)], [(eq, uop, vop), (associative, uop),
                                         lambda s: assocunify(u, v, s, eq, n)])

    if uop or vop:

        if vop:
            uop, vop = vop, uop
            v, u = u, v
        return conde([(core.eq, u, v)], [(associative, uop),
                                         lambda s: assocunify(u, v, s, eq, n)])

    return (core.eq, u, v)


def eq_comm(u, v, eq=None):
    """ Goal for commutative equality

    >>> from kanren import run, var, fact
    >>> from kanren.assoccomm import eq_comm as eq
    >>> from kanren.assoccomm import commutative, associative

    >>> fact(commutative, 'add')    # declare that 'add' is commutative
    >>> fact(associative, 'add')    # declare that 'add' is associative

    >>> x = var()
    >>> run(0, x, eq(('add', 1, 2, 3), ('add', 2, x, 1)))
    (3,)
    """
    eq = eq or eq_comm
    vtail = var()
    if isvar(u) and isvar(v):
        return (core.eq, u, v)
    uop, uargs = op_args(u)
    vop, vargs = op_args(v)
    if not uop and not vop:
        return (core.eq, u, v)
    if vop and not uop:
        uop, uargs = vop, vargs
        v, u = u, v
    return (conde, ((core.eq, u, v), ),
            ((commutative, uop), (buildo, uop, vtail, v),
             (permuteq, uargs, vtail, eq)))


def buildo(op, args, obj):
    """ obj is composed of op on args

    Example: in add(1,2,3) ``add`` is the op and (1,2,3) are the args

    Checks op_regsitry for functions to define op/arg relationships
    """
    if not isvar(obj):
        oop, oargs = op_args(obj)
        # TODO: Is greedy correct?
        return lallgreedy((eq, op, oop), (eq, args, oargs))
    else:
        try:
            return eq(obj, build(op, args))
        except TypeError:
            raise EarlyGoalError()
    raise EarlyGoalError()


def build(op, args):
    try:
        return term(op, args)
    except NotImplementedError:
        raise EarlyGoalError()


def op_args(x):
    """ Break apart x into an operation and tuple of args """
    if isvar(x):
        return None, None
    try:
        return operator(x), arguments(x)
    except NotImplementedError:
        return None, None


def eq_assoccomm(u, v):
    """ Associative/Commutative eq

    Works like logic.core.eq but supports associative/commutative expr trees

    tree-format:  (op, *args)
    example:      (add, 1, 2, 3)

    State that operations are associative or commutative with relations

    >>> from kanren.assoccomm import eq_assoccomm as eq
    >>> from kanren.assoccomm import commutative, associative
    >>> from kanren import fact, run, var

    >>> fact(commutative, 'add')    # declare that 'add' is commutative
    >>> fact(associative, 'add')    # declare that 'add' is associative

    >>> x = var()
    >>> e1 = ('add', 1, 2, 3)
    >>> e2 = ('add', 1, x)
    >>> run(0, x, eq(e1, e2))
    (('add', 2, 3), ('add', 3, 2))
    """
    uop, uargs = op_args(u)
    vop, vargs = op_args(v)

    if uop and not vop and not isvar(v):
        return fail
    if vop and not uop and not isvar(u):
        return fail
    if uop and vop and uop != vop:
        return fail
    if uop and not (uop, ) in associative.facts:
        return (eq, u, v)
    if vop and not (vop, ) in associative.facts:
        return (eq, u, v)

    if uop and vop:
        u, v = (u, v) if len(uargs) >= len(vargs) else (v, u)
        n = min(map(len, (uargs, vargs)))  # length of shorter tail
    else:
        n = None
    if vop and not uop:
        u, v = v, u
    w = var()
    # TODO: Is greedy correct?
    return (lallgreedy, (eq_assoc, u, w, eq_assoccomm, n),
            (eq_comm, v, w, eq_assoccomm))
