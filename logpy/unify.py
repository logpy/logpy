import functools
from util import transitive_get as walk
from util import assoc
from logpy.variables import Var, var, isvar

################
# Reificiation #
################

def reify_generator(t, s):
    return (reify(arg, s) for arg in t)
def reify_tuple(*args):
    return tuple(reify_generator(*args))
def reify_list(*args):
    return list(reify_generator(*args))

def reify_dict(d, s):
    # assert isinstance(d, dict)
    return dict((k, reify(v, s)) for k, v in d.items())

reify_dispatch = {
        tuple: reify_tuple,
        list:  reify_list,
        dict:  reify_dict,
        }

reify_isinstance_list = []

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
    if isvar(e):
        return reify(s[e], s) if e in s else e
    if type(e) in reify_dispatch:
        return reify_dispatch[type(e)](e, s)
    for typ, reify_fn in reify_isinstance_list:
        if isinstance(e, typ):
            return reify_fn(e, s)
    else:
        return e

###############
# Unification #
###############

def unify_seq(u, v, s):
    # assert isinstance(u, tuple) and isinstance(v, tuple)
    if len(u) != len(v):
        return False
    for uu, vv in zip(u, v):  # avoiding recursion
        s = unify(uu, vv, s)
        if s is False:
            return False
    return s

def unify_dict(u, v, s):
    # assert isinstance(u, dict) and isinstance(v, dict)
    if len(u) != len(v):
        return False
    for key, uval in u.iteritems():
        if key not in v:
            return False
        s = unify(uval, v[key], s)
        if s is False:
            return False
    return s

unify_dispatch = {
        (tuple, tuple): unify_seq,
        (list, list):   unify_seq,
        (dict, dict):   unify_dict,
        }

unify_isinstance_list = []
seq_registry = []

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
    for (typu, typv), unify_fn in unify_isinstance_list:
        if isinstance(u, typu) and isinstance(v, typv):
            return unify_fn(u, v, s)
    for typ, fn in seq_registry:
        action = False
        if isinstance(u, typ):
            u = fn(u); action=True
        if isinstance(v, typ):
            v = fn(v); action=True
        if action:
            return unify_seq(u, v, s)

    else:
        return False
