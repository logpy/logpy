import itertools as it

def transitive_get(key, d):
    """ Transitive dict.get

    >>> d = {1: 2, 2: 3, 3: 4}
    >>> d.get(1)
    2
    >>> transitive_get(1, d)
    4
    """
    while key in d:
        key = d[key]
    return key

def deep_transitive_get(key, d):
    """ Transitive get that propagates within tuples

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

def assoc(dict, key, value):
    d = dict.copy()
    d[key] = value
    return d

def dicthash(d):
    return hash(frozenset(d.items()))

def unique_dict(seq):
    seen = set()
    for d in seq:
        h = dicthash(d)
        if h not in seen:
            seen.add(h)
            yield d

def unique(seq):
    seen = set()
    for item in seq:
        if item not in seen:
            seen.add(item)
            yield item

def interleave(seqs, pass_exceptions=()):
    iters = it.imap(iter, seqs)
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

def isempty(it):
    """ Is an iterable empty

    destructive.  Use with tee

    >>> from itertools import tee
    >>> it = range(3)
    >>> tmp, it = tee(it, 2)
    >>> isempty(tmp)
    False
    """
    try:
        next(iter(it))
        return False
    except StopIteration:
        return True

def intersection(*seqs):
    for item in seqs[0]:
        found = True
        for seq in seqs[1:]:
            if item not in seq:
                found = False
                break
        if found:
            yield item

def groupsizes(total, len):
    """ Groups of length len that add up to total

    >>> from logpy.util import groupsizes
    >>> tuple(groupsizes(4, 2))
    ((1, 3), (2, 2), (3, 1))
    """
    if len == 1:
        yield (total,)
    else:
        for i in xrange(1, total - len + 1 + 1):
            for perm in groupsizes(total - i, len - 1):
                yield (i,) + perm

def raises(err, lamda):
    try:
        lamda()
        raise Exception("Did not raise %s"%err)
    except err:
        pass
