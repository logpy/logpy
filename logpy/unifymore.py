from logpy.unify import (unify_seq, unify_dict, reify_dict, reify_tuple,
        unify_dispatch)
from functools import partial
# Reify

def reify_object(o, s):
    obj = object.__new__(type(o))
    d = reify_dict(o.__dict__, s)
    obj.__dict__.update(d)
    return obj

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

def register_unify_object(cls):
    unify_dispatch[(cls, cls)] = unify_object

def register_unify_object_attrs(cls, attrs):
    unify_dispatch[(cls, cls)] = partial(unify_object_attrs, attrs=attrs)
