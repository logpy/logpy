import itertools as it
from collections import Hashable

from toolz.compatibility import range, map


def hashable(x):
    try:
        hash(x)
        return True
    except TypeError:
        return False


def dicthash(d):
    return hash(frozenset(d.items()))


def multihash(x):
    try:
        return hash(x)
    except TypeError:
        if isinstance(x, (list, tuple, set, frozenset)):
            return hash(tuple(map(multihash, x)))
        if type(x) is dict:
            return hash(frozenset(map(multihash, x.items())))
        if type(x) is slice:
            return hash((x.start, x.stop, x.step))
        raise TypeError('Hashing not covered for ' + str(x))


def unique(seq, key=lambda x: x):
    seen = set()
    for item in seq:
        try:
            k = key(item)
        except TypeError:
            # Just yield it and hope for the best, since we can't efficiently
            # check if we've seen it before.
            yield item
            continue
        if not isinstance(k, Hashable):
            # Just yield it and hope for the best, since we can't efficiently
            # check if we've seen it before.
            yield item
        elif k not in seen:
            seen.add(key(item))
            yield item


def interleave(seqs, pass_exceptions=()):
    iters = map(iter, seqs)
    while iters:
        newiters = []
        for itr in iters:
            try:
                yield next(itr)
                newiters.append(itr)
            except (StopIteration, ) + tuple(pass_exceptions):
                pass
        iters = newiters


def take(n, seq):
    if n is None:
        return seq
    if n == 0:
        return tuple(seq)
    return tuple(it.islice(seq, 0, n))


def evalt(t):
    """ Evaluate tuple if unevaluated

    >>> from kanren.util import evalt
    >>> add = lambda x, y: x + y
    >>> evalt((add, 2, 3))
    5
    >>> evalt(add(2, 3))
    5
    """

    if isinstance(t, tuple) and len(t) >= 1 and callable(t[0]):
        return t[0](*t[1:])
    else:
        return t


def intersection(*seqs):
    return (item for item in seqs[0] if all(item in seq for seq in seqs[1:]))


def groupsizes(total, len):
    """ Groups of length len that add up to total

    >>> from kanren.util import groupsizes
    >>> tuple(groupsizes(4, 2))
    ((1, 3), (2, 2), (3, 1))
    """
    if len == 1:
        yield (total, )
    else:
        for i in range(1, total - len + 1 + 1):
            for perm in groupsizes(total - i, len - 1):
                yield (i, ) + perm


def pprint(g):
    """ Pretty print a tree of goals """
    if callable(g) and hasattr(g, '__name__'):
        return g.__name__
    if isinstance(g, type):  # pragma: no cover
        return g.__name__
    if isinstance(g, tuple):
        return "(" + ', '.join(map(pprint, g)) + ")"
    return str(g)


def index(tup, ind):
    """ Fancy indexing with tuples """
    return tuple(tup[i] for i in ind)
