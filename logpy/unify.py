import functools
from util import transitive_get as walk
from util import assoc
from logpy.variables import Var, var, isvar

#########################################
# Functions for Expression Manipulation #
#########################################

def reify_var(v, s):
    # assert isvar(v)
    return reify(s[v], s) if v in s else v

def reify_generator(t, s):
    return (reify(arg, s) for arg in t)
def reify_tuple(*args):
    return tuple(reify_generator(*args))
def reify_list(*args):
    return list(reify_generator(*args))

def reify_dict(d, s):
    # assert isinstance(d, dict)
    return dict((k, reify(v, s)) for k, v in d.items())

def reify_object(o, s):
    obj = object.__new__(type(o))
    d = reify_dict(o.__dict__, s)
    obj.__dict__.update(d)
    return obj

def reify_slice(*args):
    assert len(args) == 3
    return slice(reify_generator(*args))

reify_dispatch = {
        Var:   reify_var,
        tuple: reify_tuple,
        list:  reify_list,
        dict:  reify_dict,
        slice: reify_slice,
        }

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

def unify_slice(u, v, s):
    return unify_seq((u.start, u.stop, u.step), (v.start, v.stop, v.step), s)

def unify_object(u, v, s):
    if type(u) != type(v):
        return False
    return unify_dict(u.__dict__, v.__dict__, s)

def unify_object_attrs(u, v, s, attrs):
    """Unify an object based on attribute comparison

    This function is meant to be partially specialized:

        unify_Foo = functools.partial(unify_object_attrs,
            attrs=['attr_i_care_about', 'attr_i_care_about2'])

    """
    gu = lambda a: getattr(u, a)
    gv = lambda a: getattr(v, a)
    return unify_seq(map(gu, attrs), map(gv, attrs), s)

def register_unify_object(cls):
    unify_dispatch[(cls, cls)] = unify_object

def register_unify_object_attrs(cls, attrs):
    unify_dispatch[(cls, cls)] = functools.partial(unify_object_attrs,
            attrs=attrs)

unify_dispatch = {
        (tuple, tuple): unify_seq,
        (list, list):   unify_seq,
        (dict, dict):   unify_dict,
        (slice, slice): unify_slice,
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
