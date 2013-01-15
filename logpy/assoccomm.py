from logpy.core import isvar, assoc, walk, unify, unique_dict, bindstar
from sympy.utilities.iterables import kbins

def unify_assoccomm(u, v, s, ordering=None):
    u = walk(u, s)
    v = walk(v, s)
    res = unify(u, v, s)
    if res is not False:
        yield res

    if isinstance(u, tuple) and isinstance(v, tuple):
        uop, u = u[0], u[1:]
        vop, v = v[0], v[1:]

        s = unify(uop, vop, s)
        if s is False:
            raise StopIteration()

        op = walk(uop, s)

        sm, lg = (u, v) if len(u) <= len(v) else (v, u)
        for part in kbins(range(len(lg)), len(sm), ordering):
            lg2 = makeops(op, partition(lg, part))
            # TODO: the use of bindstar here should be replaced.  This uses
            # logpy within python code within logpy.  There must be a more
            # elegant way
            goals = [eq_assoccomm(a, b, ordering) for a, b in zip(sm, lg2)]
            for res in bindstar((s,), *goals):
                yield res

def makeops(op, lists):
    return tuple(l[0] if len(l) == 1 else (op,) + tuple(l) for l in lists)

def partition(tup, part):
    return [index(tup, ind) for ind in part]

def index(tup, ind):
    return tuple(tup[i] for i in ind)


def unify_assoc(u, v, s):
    return unique_dict(unify_assoccomm(u, v, s, None))
def unify_comm(u, v, s):
    return unique_dict(unify_assoccomm(u, v, s, 11))

# Goals
def eq_assoccomm(u, v, ordering):
    return lambda s: unify_assoccomm(u, v, s, ordering)

def eq_assoc(u, v):
    """ Goal for associative equality

    >>> from logpy import run, var
    >>> from logpy.assoccomm import eq_assoc as eq
    >>> x = var()
    >>> run(0, eq((add, 1, 2, 3), ('add', 1, x)))
    (('add', 2, 3),)
    """
    return lambda s: unify_assoc(u, v, s)

def eq_comm(u, v):
    """ Goal for commutative equality

    >>> from logpy import run, var
    >>> from logpy.assoccomm import eq_comm as eq
    >>> x = var()
    >>> run(0, eq((add, 1, 2, 3), ('add', x, 1)))
    (('add', 2, 3), ('add', 3, 2))
    """
    return lambda s: unify_comm(u, v, s)
