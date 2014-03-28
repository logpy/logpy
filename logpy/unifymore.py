from logpy.unification import unify, reify
from functools import partial
from .dispatch import dispatch

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
    >>> print(f)
    Foo(1, ~x)
    >>> print(reify_object(f, {x: 2}))
    Foo(1, 2)
    """

    obj = object.__new__(type(o))
    d = reify(o.__dict__, s)
    if d == o.__dict__:
        return o
    obj.__dict__.update(d)
    return obj


def reify_object_slots(o, s):
    """
    >>> from logpy.unifymore import reify_object_slots
    >>> from logpy import var
    >>> class Foo(object):
    ...     __slots__ = 'a', 'b'
    ...     def __init__(self, a, b):
    ...         self.a = a
    ...         self.b = b
    ...     def __str__(self):
    ...         return "Foo(%s, %s)"%(str(self.a), str(self.b))
    >>> x = var('x')
    >>> print(reify_object_slots(Foo(x, 2), {x: 1}))
    Foo(1, 2)
    """
    attrs = [getattr(o, attr) for attr in o.__slots__]
    new_attrs = reify(attrs, s)
    if attrs == new_attrs:
        return o
    else:
        newobj = object.__new__(type(o))
        for slot, attr in zip(o.__slots__, new_attrs):
            setattr(newobj, slot, attr)
        return newobj


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
    >>> print(f)
    Foo(~x, ~y)
    >>> print(reify_object_attrs(f, {x: 1, y: 2}, ['a', 'b']))
    Foo(1, 2)
    >>> print(reify_object_attrs(f, {x: 1, y: 2}, ['a']))
    Foo(1, ~y)

    This function is meant to be partially specialized

    >>> from functools import partial
    >>> reify_Foo_a = partial(reify_object_attrs, attrs=['a'])

    attrs contains the list of attributes which participate in reificiation
    """
    obj = object.__new__(type(o))
    d = dict(zip(attrs, [getattr(o, attr) for attr in attrs]))
    d2 = reify(d, s)                             # reified attr dict
    if d2 == d:
        return o

    obj.__dict__.update(o.__dict__)                   # old dict
    obj.__dict__.update(d2)                           # update w/ reified vals
    return obj

#########
# Unify #
#########

@dispatch(slice, slice, dict)
def _unify(u, v, s):
    """ Unify a Python ``slice`` object """
    return unify((u.start, u.stop, u.step), (v.start, v.stop, v.step), s)


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
    return unify(u.__dict__, v.__dict__, s)




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
    >>> print(unify_object_attrs(f, g, {}, ['a', 'b']))  #doctest: +SKIP
    {~x: 1, ~y: 2}
    >>> print(unify_object_attrs(f, g, {}, ['a']))
    {~x: 1}

    This function is meant to be partially specialized

    >>> from functools import partial
    >>> unify_Foo_a = partial(unify_object_attrs, attrs=['a'])

    attrs contains the list of attributes which participate in reificiation
    """
    return unify([getattr(u, a) for a in attrs],
                 [getattr(v, a) for a in attrs],
                 s)


# Registration

def register_reify_object_attrs(cls, attrs):
    _reify.add((cls,), partial(reify_object_attrs, attrs=attrs))


def register_unify_object(cls):
    _unify.add((cls, cls, dict), unify_object)


def register_unify_object_attrs(cls, attrs):
    _unify.add((cls, cls, dict), partial(unify_object_attrs, attrs=attrs))


def register_object_attrs(cls, attrs):
    register_unify_object_attrs(cls, attrs)
    register_reify_object_attrs(cls, attrs)


def unifiable(cls):
    """ Register standard unify and reify operations on class

    This uses the type and __dict__ or __slots__ attributes to define the
    nature of the term

    See Also:

    >>> from logpy import run, var, eq
    >>> from logpy.unifymore import unifiable
    >>> class A(object):
    ...     def __init__(self, a, b):
    ...         self.a = a
    ...         self.b = b
    >>> unifiable(A)
    <class 'logpy.unifymore.A'>

    >>> x = var('x')
    >>> a = A(1, 2)
    >>> b = A(1, x)

    >>> run(1, x, eq(a, b))
    (2,)
    """
    if hasattr(cls, '__slots__'):
        _reify.add((cls, dict), reify_object_slots)
        _unify.add((cls, cls, dict), unify_object_slots)
    else:
        _reify.add((cls, dict), reify_object)
        _unify.add((cls, cls, dict), unify_object)

    return cls
