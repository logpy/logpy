import collections
import operator
from itertools import permutations

from unification import var, isvar, unify
# TODO: we should be able to register new reification processes without
# importing private methods.
from unification.core import _reify
from unification.more import unifiable, reify_object

from .core import (eq, EarlyGoalError, conde, condeseq, lany, lallgreedy, lall,
                   fail, success)
from .util import unique


def heado(head, coll):
    """ head is the head of coll

    See also:
        tailo
        conso
    """
    if isinstance(coll, (tuple, list)):
        return (fail if len(coll) == 0 else (eq, head, coll[0]))
    else:
        tail = var()
        return (eq, LCons(head, tail), coll)


def tailo(tail, coll):
    """ tail is the tail of coll

    See also:
        heado
        conso
    """
    if isinstance(coll, (tuple, list)):
        return (fail if len(coll) == 0 else (eq, tail, coll[1:]))
    else:
        head = var()
        return (eq, LCons(head, tail), coll)


def conso(h, t, l):
    """ Logical cons -- l[0], l[1:] == h, t """
    if isinstance(l, (tuple, list)):
        if len(l) == 0:
            return fail
        else:
            return (conde, [(eq, h, l[0]), (eq, t, l[1:])])
    elif isinstance(t, (tuple, list)):
        return eq((h, ) + tuple(t), l)
    else:
        return (
            lall,

            # The definition of conso. This means that l can be unified with
            # an LCons object (head + tail).
            (eq, LCons(h, t), l),

            # A "type declaration" for the tail. This means that the first goal
            # found will simplify to a list with no extra unbound variables.
            (lany, (eq, t, ()), (eq, t, LCons(var(), var())))
        )


def permuteq(a, b, eq2=eq):
    """ Equality under permutation

    For example (1, 2, 2) equates to (2, 1, 2) under permutation
    >>> from kanren import var, run, permuteq
    >>> x = var()
    >>> run(0, x, permuteq(x, (1, 2)))
    ((1, 2), (2, 1))

    >>> run(0, x, permuteq((2, 1, x), (2, 1, 2)))
    (2,)
    """
    if isinstance(a, tuple) and isinstance(b, tuple):
        if len(a) != len(b):
            return fail
        elif collections.Counter(a) == collections.Counter(b):
            return success
        else:
            c, d = list(a), list(b)
            for x in list(c):
                # TODO: This is quadratic in the number items in the sequence.
                # Need something like a multiset. Maybe use
                # collections.Counter?
                try:
                    d.remove(x)
                    c.remove(x)
                except ValueError:
                    pass
            c, d = tuple(c), tuple(d)
            if len(c) == 1:
                return (eq2, c[0], d[0])
            return condeseq(
                ((eq2, x, d[0]), (permuteq, c[0:i] + c[i + 1:], d[1:], eq2))
                for i, x in enumerate(c)
            )

    if isvar(a) and isvar(b):
        raise EarlyGoalError()

    if isvar(a) or isvar(b):
        if isinstance(b, tuple):
            c, d = a, b
        elif isinstance(a, tuple):
            c, d = b, a

        return (condeseq, ([eq(c, perm)]
                           for perm in unique(permutations(d, len(d)))))


def seteq(a, b, eq2=eq):
    """ Set Equality

    For example (1, 2, 3) set equates to (2, 1, 3)

    >>> from kanren import var, run, seteq
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
    else:  # not isvar(b)
        return permuteq(a, ts(b), eq2)


def goalify(func, name=None):
    """ Convert Python function into kanren goal

    >>> from kanren import run, goalify, var, membero
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
                if any(map(isvar, inputs)):
                    raise EarlyGoalError()
                return (eq, func(*inputs), out)
            else:
                return (eq, func(inputs), out)

    name = name or (func.__name__ + 'o')
    funco.__name__ = name

    return funco


def membero(x, coll):
    """ Goal such that x is an item of coll """
    if not isvar(coll):
        return (lany, ) + tuple((eq, x, item) for item in coll)
    raise EarlyGoalError()


typo = goalify(type, name='typo')
isinstanceo = goalify(isinstance, name='isinstanceo')
not_equalo = goalify(operator.ne, name='not_equalo')


def appendo(l, s, ls):
    """
    Goal that ls = l + s.

    See Byrd thesis pg. 247
    https://scholarworks.iu.edu/dspace/bitstream/handle/2022/8777/Byrd_indiana_0093A_10344.pdf
    """
    if all(map(isvar, (l, s, ls))):
        raise EarlyGoalError()
    a, d, res = [var() for i in range(3)]
    return (lany, (lallgreedy, (eq, l, ()), (eq, s, ls)),
            (lall, (conso, a, d, l), (conso, a, res, ls),
             (appendo, d, s, res)))


@unifiable
class LCons(object):
    __slots__ = 'head', 'tail'

    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def __repr__(self):
        return 'LCons(%r, %r)' % (self.head, self.tail)

    def __iter__(self):
        yield self.head
        if isinstance(self.tail, collections.Iterable):
            for x in self.tail:
                yield x

    def __eq__(self, other):
        return (
            isinstance(other, LCons) and
            self.head == other.head and
            self.tail == other.tail)

    def as_tuple(self):
        tail = self.tail
        if isinstance(tail, LCons):
            tail = self.tail.as_tuple()
        elif isvar(tail):
            raise EarlyGoalError()
        return (self.head, ) + tail


@unify.register(LCons, (list, tuple), dict)
def _lcons_unify(lcons, t, s):
    if len(t) == 0:
        return False
    return unify((lcons.head, lcons.tail), (t[0], t[1:]), s)


@unify.register((list, tuple), LCons, dict)
def _lcons_runify(t, lcons, s):
    return _lcons_unify(lcons, t, s)


@_reify.register(LCons, dict)
def reify_lcons(lcons, s):
    ret = reify_object(lcons, s)
    try:
        # Simplify to a tuple once we've reified, if possible.
        ret = ret.as_tuple()
    except (TypeError, EarlyGoalError):
        pass
    return ret
