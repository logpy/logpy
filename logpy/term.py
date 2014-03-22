from multipledispatch import dispatch
from logpy.unification import unify, reify, _reify, _unify


def termify(cls):
    """ Register class to operate as a term

    This uses the type and __dict__ or __slots__ attributes to define the
    nature of the term

    See Also:
        operator
        arguments
        term

    >>> from logpy import termify, run, var, eq
    >>> class A(object):
    ...     def __init__(self, a, b):
    ...         self.a = a
    ...         self.b = b
    >>> termify(A)
    <class 'logpy.term.A'>

    >>> x = var('x')
    >>> a = A(1, 2)
    >>> b = A(1, x)

    >>> run(1, x, eq(a, b))
    (2,)
    """
    if hasattr(cls, '__slots__'):
        operator.add((cls,), operator_slot)
        arguments.add((cls,), arguments_slot)
    else:
        operator.add((cls,), operator_dict)
        arguments.add((cls,), arguments_dict)

    _reify.add((cls, dict), reify_term)
    _unify.add((cls, cls, dict), unify_term)

    return cls

# Arguments

@dispatch((tuple, list))
def arguments(seq):
    return seq[1:]


def arguments_dict(obj):
    return obj.__dict__


def arguments_slot(obj):
    return dict((attr, getattr(obj, attr)) for attr in obj.__slots__
                                            if hasattr(obj, attr))
# Operator

@dispatch((tuple, list))
def operator(seq):
    return seq[0]


operator_slot = operator_dict = type


# Term

@dispatch(object, (tuple, list))
def term(op, args):
    return (op,) + tuple(args)

@dispatch(object, dict)
def term(op, args):
    if hasattr(op, '__slots__'):
        return term_slot(op, args)
    else:
        return term_dict(op, args)


def term_slot(op, args):
    obj = object.__new__(op)
    for attr, val in args.items():
        setattr(obj, attr, val)
    return obj


def term_dict(op, args):
    obj = object.__new__(op)
    obj.__dict__.update(args)
    return obj


def reify_term(obj, s):
    op, args = operator(obj), arguments(obj)
    op = reify(op, s)
    args = reify(args, s)
    new = term(op, args)
    return new


def unify_term(u, v, s):
    u_op, u_args = operator(u), arguments(u)
    v_op, v_args = operator(v), arguments(v)
    s = unify(u_op, v_op, s)
    s = unify(u_args, v_args, s)
    return s
