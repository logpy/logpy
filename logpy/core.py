import itertools as it

class var(object):
    def __new__(cls, token):
        return (var, token)

isvar = lambda t: isinstance(t, tuple) and t[0] is var

def transitive_get(key, d):
    while key in d:
        key = d[key]
    return key

def deep_transitive_get(key, d):
    key = transitive_get(key, d)
    if isvar(key):
        return key
    if isinstance(key, tuple):
        return tuple(map(lambda k: deep_transitive_get(k, d), key))
    return key


walk = transitive_get
walk_star = deep_transitive_get
""" Get the transitive value of v in s """

def assoc(dict, key, value):
    d = dict.copy()
    d[key] = value
    return d

def unify(u, v, s):  # no check at the moment
    u = walk(u, s)
    v = walk(v, s)
    if u is v:
        return s
    if isvar(u):
        return assoc(s, u, v)
    if isvar(v):
        return assoc(s, v, u)
    if isinstance(u, tuple) and isinstance(v, tuple):
        if len(u) != len(v):
            return False
        for uu, vv in zip(u, v):  # avoiding recursion
            s = unify(uu, vv, s)
            if s is False:
                return False
        return s
    return False

def eq(u, v):
    def goal_eq(s):
        result = unify(u, v, s)
        if result is not False:
            yield result
    return goal_eq

def unique(seq):
    seen = set()
    for item in seq:
        try:  # TODO, deal with dicts and hashability
            if item not in seen:
                seen.add(item)
                yield item
        except TypeError:
            yield item

# TODO: replace chain with interleave

def conde(*goals):
    def goal_conde(s):
        return unique(it.chain(*[goal(s) for goal in goals]))
    return goal_conde

def bind(stream, goal):
    """ Filter a stream by a goal """
    return unique(it.chain(*it.imap(goal, stream))) # TODO: interleave

def bindstar(stream, *goals):
    if not goals:
        return stream
    else:
        return bindstar(bind(stream, goals[0]), *goals[1:])

def rrun(n, x, *goals):
    seq = (walk_star(x, s) for s in bindstar(({},), *goals))
    if isinstance(n, int) and n > 0:
        return tuple(it.islice(seq, 0, n))
    if n is None:
        return seq
