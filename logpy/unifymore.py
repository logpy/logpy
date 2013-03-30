from logpy.unify import (unify_seq, unify_dict, reify_dict, reify_tuple,
        unify_dispatch, reify_dispatch)
from functools import partial
# Reify

def reify_object(o, s):
    obj = object.__new__(type(o))
    d = reify_dict(o.__dict__, s)
    if d == o.__dict__:
        return o
    obj.__dict__.update(d)
    return obj

def reify_object_attrs(o, s, attrs):
    """ Reify an object based on attribute comparison

    This function is meant to be partially specialized:

        reify_Foo = functools.partial(reify_object_attrs,
            attrs=['attr_i_care_about', 'attr_i_care_about2'])

    """
    obj = object.__new__(type(o))
    d = dict(zip(attrs, map(o.__dict__.get, attrs)))  # dict with attrs
    d2 = reify_dict(d, s)                              # reified attr dict
    if d2 == d:
        return o
    obj.__dict__.update(o.__dict__)                   # old dict
    obj.__dict__.update(d2)                            # update w/ reified vals
    return obj

def register_reify_object_attrs(cls, attrs):
    reify_dispatch[cls] = partial(reify_object_attrs, attrs=attrs)

def reify_slice(o, s):
    return slice(*reify_tuple((o.start, o.stop, o.step), s))

more_reify_dispatch = {
        slice: reify_slice,
        }

# Unify

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

more_unify_dispatch = {
        (slice, slice): unify_slice,
        }

def register_unify_object(cls):
    unify_dispatch[(cls, cls)] = unify_object

def register_unify_object_attrs(cls, attrs):
    unify_dispatch[(cls, cls)] = partial(unify_object_attrs, attrs=attrs)

def register_object_attrs(cls, attrs):
    register_unify_object_attrs(cls, attrs)
    register_reify_object_attrs(cls, attrs)
