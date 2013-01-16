from logpy.core import (isvar, assoc, walk, unify, unique_dict, bindstar,
        Relation, heado, conde, var, eq, fail)
from sympy.utilities.iterables import kbins

__all__ = ['associative', 'commutative', 'eq_assoccomm', 'opo']

associative = Relation()
commutative = Relation()

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
            # TODO: we use logpy code within python within logpy
            # There must be a more elegant way
            for res in conde((eq_assoccomm, a, b) for a, b in zip(sm, lg2))(s):
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

def operation(op):
    """ Either an associative or commutative operation """
    return conde([commutative(op)], [associative(op)])

# Goals
def opo(x, op):
    """ Operation of a tuple

    op((add, 1, 2), x) --> {x: add}
    """
    h = var()
    return conde(((heado, h, x), (operation, h), (eq, h, op)))

def eq_assoccomm(u, v):
    """ Associative/Commutative eq

    Works like logic.core.eq but supports associative/commutative expr trees

    tree-format:  (op, *args)
    example:      (add, 1, 2, 3)

    State that operations are associative or commutative with relations

    >>> from logpy.assoccomm import eq_assoccomm as eq
    >>> from logpy.assoccomm import commutative, associative
    >>> from logpy import fact, run, var

    >>> fact(commutative, 'add')    # declare that 'add' is commutative

    >>> x = var
    >>> e1 = ('add', 1, 2, 3)
    >>> e2 = ('add', 1, x)
    >>> run(0, x, eq(e1, e2))
    (('add', 2, 3), ('add', 3, 2))
    """
    op = var()
    return conde(((eq, u, v),),
                 ((opo, u, op), (opo, v, op),
                    (conde,
                        ((commutative, op), (eq_comm, u, v)),
                        ((associative, op), (eq_assoc, u, v)))))

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
