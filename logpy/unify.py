from util import transitive_get as walk
from util import assoc
from logpy.variables import Var, var, isvar

#########################################
# Functions for Expression Manipulation #
#########################################

def reify_var(v, s):
    assert isvar(v)
    return reify(s[v], s) if v in s else v

def reify_tuple(t, s):
    assert isinstance(t, tuple)
    return tuple(reify(arg, s) for arg in t)

def reify_dict(d, s):
    assert isinstance(d, dict)
    return dict((k, reify(v, s)) for k, v in d.items())

def reify_object(o, s):
    obj = object.__new__(type(o))
    d = reify_dict(o.__dict__, s)
    obj.__dict__.update(d)
    return obj

reify_dispatch = {Var: reify_var,
                  tuple: reify_tuple,
                  dict:  reify_dict}

def reify(e, s):
    """ Replace variables of expression with substitution

    >>> from logpy.unify import reify, var
    >>> x, y = var(), var()
    >>> e = (1, x, (3, y))
    >>> s = {x: 2, y: 4}
    >>> reify(e, s)
    (1, 2, (3, 4))

    >>> e = {1: x, 3: (y, 5)}
    >>> reify(e, s)
    {1: 2, 3: (4, 5)}

    """
    if type(e) in reify_dispatch:
        return reify_dispatch[type(e)](e, s)
    else:
        return e


def unify_tuple(u, v, s):
    assert isinstance(u, tuple) and isinstance(v, tuple)
    if len(u) != len(v):
        return False
    for uu, vv in zip(u, v):  # avoiding recursion
        s = unify(uu, vv, s)
        if s is False:
            return False
    return s

def unify_dict(u, v, s):
    assert isinstance(u, dict) and isinstance(v, dict)
    if len(u) != len(v):
        return False
    for key, uval in u.iteritems():
        if key not in v:
            return False
        s = unify(uval, v[key], s)
        if s is False:
            return False
    return s

def unify_object(u, v, s):
    if type(u) != type(v):
        return False
    return unify_dict(u.__dict__, v.__dict__, s)

unify_dispatch = {
        (tuple, tuple): unify_tuple,
        (dict, dict):   unify_dict
        }

def unify(u, v, s):  # no check at the moment
    """ Find substitution so that u == v while satisfying s

    >>> from logpy.unify import unify, var
    >>> x = var('x')
    >>> unify((1, x), (1, 2), {})
    {~x: 2}
    """
    u = walk(u, s)
    v = walk(v, s)
    if u == v:
        return s
    if isvar(u):
        return assoc(s, u, v)
    if isvar(v):
        return assoc(s, v, u)
    types = (type(u), type(v))
    if types in unify_dispatch:
        return unify_dispatch[types](u, v, s)
    else:
        return False
