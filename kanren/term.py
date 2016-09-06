from unification import unify, reify
from unification.core import _unify, _reify

from .dispatch import dispatch


@dispatch((tuple, list))
def arguments(seq):
    return seq[1:]


@dispatch((tuple, list))
def operator(seq):
    return seq[0]


@dispatch(object, (tuple, list))
def term(op, args):
    return (op, ) + tuple(args)


def unifiable_with_term(cls):
    _reify.add((cls, dict), reify_term)
    _unify.add((cls, cls, dict), unify_term)
    return cls


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
    if s is not False:
        s = unify(u_args, v_args, s)
    return s
