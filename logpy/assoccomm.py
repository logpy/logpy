from logpy.core import (isvar, success, fail, assoc, goaleval, EarlyGoalError,
        walk, unify, isvar)
from sympy.utilities.iterables import kbins

def assoc_unify(u, v, s):
    u = walk(u, s)
    v = walk(v, s)
    if u == v:
        yield s
    if isvar(u):
        yield assoc(s, u, v)
    if isvar(v):
        yield assoc(s, v, u)

    if isinstance(u, tuple) and isinstance(v, tuple):
        uop, u = u[0], u[1:]
        vop, v = v[0], v[1:]

        s = unify(uop, vop, s)
        uop = walk(uop, s)
        if s is False:
            raise StopIteration()

        sm, lg = (u, v) if len(u) <= len(v) else (v, u)
        print sm, lg
        for part in kbins(range(len(lg)), len(sm)):
            print "    ", part
            lg2 = makeops(uop, partition(lg, part))
            print "    ", sm, lg2
            result = unify(sm, lg2, s)
            if result is not False:
                yield result

def makeops(op, lists):
    return tuple(l[0] if len(l) == 1 else (op,) + tuple(l) for l in lists)

def partition(tup, part):
    return [index(tup, ind) for ind in part]

def index(tup, ind):
    return tuple(tup[i] for i in ind)
