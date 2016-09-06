import operator

from unification import isvar

from .core import (eq, EarlyGoalError, lany)


def gt(x, y):
    """ x > y """
    if not isvar(x) and not isvar(y):
        return eq(x > y, True)
    else:
        raise EarlyGoalError()


def lt(x, y):
    """ x > y """
    if not isvar(x) and not isvar(y):
        return eq(x < y, True)
    else:
        raise EarlyGoalError()


def lor(*goalconsts):
    """ Logical or for goal constructors

    >>> from kanren.arith import lor, eq, gt
    >>> gte = lor(eq, gt)  # greater than or equal to is `eq or gt`
    """

    def goal(*args):
        return lany(*[gc(*args) for gc in goalconsts])

    return goal


gte = lor(gt, eq)
lte = lor(lt, eq)


def binop(op, revop=None):
    """ Transform binary operator into goal

    >>> from kanren.arith import binop
    >>> import operator
    >>> add = binop(operator.add, operator.sub)

    >>> from kanren import var, run
    >>> x = var('x')
    >>> next(add(1, 2, x)({}))
    {~x: 3}
    """

    def goal(x, y, z):
        if not isvar(x) and not isvar(y):
            return eq(op(x, y), z)
        if not isvar(y) and not isvar(z) and revop:
            return eq(x, revop(z, y))
        if not isvar(x) and not isvar(z) and revop:
            return eq(y, revop(z, x))
        raise EarlyGoalError()

    goal.__name__ = op.__name__
    return goal


add = binop(operator.add, operator.sub)
add.__doc__ = """ x + y == z """
mul = binop(operator.mul, operator.truediv)
mul.__doc__ = """ x * y == z """
mod = binop(operator.mod)
mod.__doc__ = """ x % y == z """


def sub(x, y, z):
    """ x - y == z """
    return add(y, z, x)


def div(x, y, z):
    """ x / y == z """
    return mul(z, y, x)
