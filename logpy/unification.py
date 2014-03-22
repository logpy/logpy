from functools import partial
from util import transitive_get as walk
from util import assoc
from variable import Var, var, isvar
import itertools as it
from multipledispatch import dispatch
from collections import Iterator

################
# Reificiation #
################

@dispatch(Iterator, dict)
def _reify(t, s):
    return it.imap(partial(reify, s=s), t)
    # return (reify(arg, s) for arg in t)

@dispatch(tuple, dict)
def _reify(t, s):
    return tuple(reify(iter(t), s))

@dispatch(list, dict)
def _reify(t, s):
    return list(reify(iter(t), s))

@dispatch(dict, dict)
def _reify(d, s):
    # assert isinstance(d, dict)
    return dict((k, reify(v, s)) for k, v in d.items())

@dispatch(object, dict)
def _reify(o, s):
    return o

reify_isinstance_list = []

def reify(e, s):
    """ Replace variables of expression with substitution

    >>> from logpy.unification import reify, var
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
    if hasattr(e, '_from_logpy') and not isinstance(e, type):
        return e._from_logpy(reify(e._as_logpy(), s))
    return _reify(e, s)

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

    >>> from logpy.unification import unify, var
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
    if (hasattr(u, '_as_logpy') and not isinstance(u, type) and
        hasattr(v, '_as_logpy') and not isinstance(v, type)):
        return unify_seq(u._as_logpy(), v._as_logpy(), s)
    for (typu, typv), unify_fn in unify_isinstance_list:
        if isinstance(u, typu) and isinstance(v, typv):
            return unify_fn(u, v, s)
    for typ, fn in seq_registry:
        if isinstance(u, typ) and isinstance(v, typ):
            return unify_seq(fn(u), fn(v), s)

    else:
        return False
