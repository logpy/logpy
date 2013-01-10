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
