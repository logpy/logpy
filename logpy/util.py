import itertools as it
from toolz.compatibility import range, map, iteritems

def hashable(x):
    try:
        hash(x)
        return True
    except TypeError:
        return False

def transitive_get(key, d):
    """ Transitive dict.get

    >>> from logpy.util import transitive_get
    >>> d = {1: 2, 2: 3, 3: 4}
    >>> d.get(1)
    2
    >>> transitive_get(1, d)
    4
    """
    while hashable(key) and key in d:
        key = d[key]
    return key

def deep_transitive_get(key, d):
    """ Transitive get that propagates within tuples

    >>> from logpy.util import transitive_get, deep_transitive_get
    >>> d = {1: (2, 3), 2: 12, 3: 13}
    >>> transitive_get(1, d)
    (2, 3)
    >>> deep_transitive_get(1, d)
    (12, 13)
    """

    key = transitive_get(key, d)
    if isinstance(key, tuple):
        return tuple(map(lambda k: deep_transitive_get(k, d), key))
    else:
        return key

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
            if key(item) not in seen:
                seen.add(key(item))
                yield item
        except TypeError:   # item probably isn't hashable
            yield item      # Just return it and hope for the best

def interleave(seqs, pass_exceptions=()):
    iters = map(iter, seqs)
    while iters:
        newiters = []
        for itr in iters:
            try:
                yield next(itr)
                newiters.append(itr)
            except (StopIteration,) + tuple(pass_exceptions):
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

    >>> from logpy.util import evalt
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
    return (item for item in seqs[0]
                 if all(item in seq for seq in seqs[1:]))

def groupsizes(total, len):
    """ Groups of length len that add up to total

    >>> from logpy.util import groupsizes
    >>> tuple(groupsizes(4, 2))
    ((1, 3), (2, 2), (3, 1))
    """
    if len == 1:
        yield (total,)
    else:
        for i in range(1, total - len + 1 + 1):
            for perm in groupsizes(total - i, len - 1):
                yield (i,) + perm

def raises(err, lamda):
    try:
        lamda()
        raise Exception("Did not raise %s"%err)
    except err:
        pass

def pprint(g):
    """ Pretty print a tree of goals """
    if callable(g) and hasattr(g, '__name__'):
        return g.__name__
    if isinstance(g, type):
        return g.__name__
    if isinstance(g, tuple):
        return "(" + ', '.join(map(pprint, g)) + ")"
    return str(g)

def index(tup, ind):
    """ Fancy indexing with tuples """
    return tuple(tup[i] for i in ind)
