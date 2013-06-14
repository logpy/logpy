
from logpy.core import (isvar, var, run, membero, eq, EarlyGoalError, lany)

def gt(x, y):
    if not isvar(x) and not isvar(y):
        return eq(x > y, True)
    else:
        raise EarlyGoalError()

def lt(x, y):
    if not isvar(x) and not isvar(y):
        return eq(x < y, True)
    else:
        raise EarlyGoalError()

def lor(*goalconsts):
    def goal(*args):
        return lany(*[gc(*args) for gc in goalconsts])
    return goal

gte = lor(gt, eq)
lte = lor(lt, eq)

def add(x, y, z):
    """ x + y == z """
    if not isvar(x) and not isvar(y):
        return eq(x+y, z)
    if not isvar(y) and not isvar(z):
        return eq(x, z-y)
    if not isvar(x) and not isvar(z):
        return eq(y, z-x)
    raise EarlyGoalError()

def sub(x, y, z):
    """ x - y == z """
    return add(y, z, x)

def mul(x, y, z):
    """ x * y == z """
    if not isvar(x) and not isvar(y):
        return eq(x*y, z)
    if not isvar(y) and not isvar(z):
        return eq(x, z/y)
    if not isvar(x) and not isvar(z):
        return eq(y, z/x)
    raise EarlyGoalError()

def div(x, y, z):
    """ x / y == z """
    return mul(z, y, x)
