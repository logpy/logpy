from logpy.unification import (unify_seq, unify_dict,
        unify_dispatch, reify)
from functools import partial
from multipledispatch import dispatch

#########
# Reify #
#########

@dispatch(slice, dict)
def _reify(o, s):
    """ Reify a Python ``slice`` object """
    return slice(*reify((o.start, o.stop, o.step), s))

def reify_object(o, s):
    """ Reify a Python object with a substitution

    >>> from logpy.unifymore import reify_object
    >>> from logpy import var
    >>> class Foo(object):
    ...     def __init__(self, a, b):
    ...         self.a = a
    ...         self.b = b
    ...     def __str__(self):
    ...         return "Foo(%s, %s)"%(str(self.a), str(self.b))

    >>> x = var('x')
    >>> f = Foo(1, x)
    >>> print f
    Foo(1, ~x)
    >>> print reify_object(f, {x: 2})
    Foo(1, 2)
    """

    obj = object.__new__(type(o))
    d = reify(o.__dict__, s)
    if d == o.__dict__:
        return o
    obj.__dict__.update(d)
    return obj

def reify_object_attrs(o, s, attrs):
    """ Reify only certain attributes of a Python object

    >>> from logpy.unifymore import reify_object_attrs
    >>> from logpy import var
    >>> class Foo(object):
    ...     def __init__(self, a, b):
    ...         self.a = a
    ...         self.b = b
    ...     def __str__(self):
    ...         return "Foo(%s, %s)"%(str(self.a), str(self.b))

    >>> x = var('x')
    >>> y = var('y')
    >>> f = Foo(x, y)
    >>> print f
    Foo(~x, ~y)
    >>> print reify_object_attrs(f, {x: 1, y: 2}, ['a', 'b'])
    Foo(1, 2)
    >>> print reify_object_attrs(f, {x: 1, y: 2}, ['a'])
    Foo(1, ~y)

    This function is meant to be partially specialized

    >>> from functools import partial
    >>> reify_Foo_a = partial(reify_object_attrs, attrs=['a'])

    attrs contains the list of attributes which participate in reificiation
    """
    obj = object.__new__(type(o))
    d = dict(zip(attrs, map(o.__dict__.get, attrs)))  # dict with attrs
    d2 = reify(d, s)                             # reified attr dict
    if d2 == d:
        return o
    obj.__dict__.update(o.__dict__)                   # old dict
    obj.__dict__.update(d2)                           # update w/ reified vals
    return obj

#########
# Unify #
#########

def unify_slice(u, v, s):
    """ Unify a Python ``slice`` object """
    return unify_seq((u.start, u.stop, u.step), (v.start, v.stop, v.step), s)

def unify_object(u, v, s):
    """ Unify two Python objects

    Unifies their type and ``__dict__`` attributes

    >>> from logpy.unifymore import unify_object
    >>> from logpy import var
    >>> class Foo(object):
    ...     def __init__(self, a, b):
    ...         self.a = a
    ...         self.b = b
    ...     def __str__(self):
    ...         return "Foo(%s, %s)"%(str(self.a), str(self.b))

    >>> x = var('x')
    >>> f = Foo(1, x)
    >>> g = Foo(1, 2)
    >>> unify_object(f, g, {})
    {~x: 2}
    """
    if type(u) != type(v):
        return False
    return unify_dict(u.__dict__, v.__dict__, s)

def unify_object_attrs(u, v, s, attrs):
    """ Unify only certain attributes of two Python objects

    >>> from logpy.unifymore import unify_object_attrs
    >>> from logpy import var
    >>> class Foo(object):
    ...     def __init__(self, a, b):
    ...         self.a = a
    ...         self.b = b
    ...     def __str__(self):
    ...         return "Foo(%s, %s)"%(str(self.a), str(self.b))

    >>> x = var('x')
    >>> y = var('y')
    >>> f = Foo(x, y)
    >>> g = Foo(1, 2)
    >>> print unify_object_attrs(f, g, {}, ['a', 'b'])  #doctest: +SKIP
    {~x: 1, ~y: 2}
    >>> print unify_object_attrs(f, g, {}, ['a'])
    {~x: 1}

    This function is meant to be partially specialized

    >>> from functools import partial
    >>> unify_Foo_a = partial(unify_object_attrs, attrs=['a'])

    attrs contains the list of attributes which participate in reificiation
    """
    gu = lambda a: getattr(u, a)
    gv = lambda a: getattr(v, a)
    return unify_seq(map(gu, attrs), map(gv, attrs), s)


# Registration

more_unify_dispatch = {
        (slice, slice): unify_slice,
        }

def register_reify_object_attrs(cls, attrs):
    _reify.add((cls,), partial(reify_object_attrs, attrs=attrs))


def register_unify_object(cls):
    unify_dispatch[(cls, cls)] = unify_object

def register_unify_object_attrs(cls, attrs):
    unify_dispatch[(cls, cls)] = partial(unify_object_attrs, attrs=attrs)

def register_object_attrs(cls, attrs):
    register_unify_object_attrs(cls, attrs)
    register_reify_object_attrs(cls, attrs)

def _as_logpy(self):
    return (type(self), self.__dict__)

def _from_logpy((typ, attrs)):
    obj = object.__new__(typ)
    obj.__dict__.update(attrs)
    return obj

def _as_logpy_slot(self):
    attrs = dict((attr, getattr(self, attr)) for attr in self.__slots__
                                             if hasattr(self, attr))
    return (type(self), attrs)

def _from_logpy_slot((typ, attrs)):
    obj = object.__new__(typ)
    for attr, val in attrs.items():
        setattr(obj, attr, val)
    return obj


def logify(cls):
    """ Alter a class so that it interacts well with LogPy

    The __class__ and __dict__ attributes are used to define the LogPy term

    See Also:
        _as_logpy
        _from_logpy


    >>> from logpy import logify, run, var, eq
    >>> class A(object):
    ...     def __init__(self, a, b):
    ...         self.a = a
    ...         self.b = b
    >>> logify(A)

    >>> x = var('x')
    >>> a = A(1, 2)
    >>> b = A(1, x)

    >>> run(1, x, eq(a, b))
    (2,)
    """
    if hasattr(cls, '__slots__'):
        cls._as_logpy = _as_logpy_slot
        cls._from_logpy = staticmethod(_from_logpy_slot)
    else:
        cls._as_logpy = _as_logpy
        cls._from_logpy = staticmethod(_from_logpy)
