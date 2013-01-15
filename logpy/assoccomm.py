from logpy.core import isvar, assoc, walk, unify
from sympy.utilities.iterables import kbins

def unify_assoccomm(u, v, s, ordering=None):
    u = walk(u, s)
    v = walk(v, s)
    if u == v:
        yield s
    if isvar(u):                # TODO: yield all possibilities
        yield assoc(s, u, v)
    if isvar(v):                # TODO: yield all possibilities
        yield assoc(s, v, u)

    if isinstance(u, tuple) and isinstance(v, tuple):
        uop, u = u[0], u[1:]
        vop, v = v[0], v[1:]

        s = unify(uop, vop, s)
        uop = walk(uop, s)
        if s is False:
            raise StopIteration()

        sm, lg = (u, v) if len(u) <= len(v) else (v, u)
        for part in kbins(range(len(lg)), len(sm), ordering):
            lg2 = makeops(uop, partition(lg, part))
            result = unify(sm, lg2, s)
            if result is not False:
                yield result

def unify_assoc(u, v, s):
    return unify_assoccomm(u, v, s, None)
def unify_comm(u, v, s):
    return unify_assoccomm(u, v, s, 11)

def makeops(op, lists):
    return tuple(l[0] if len(l) == 1 else (op,) + tuple(l) for l in lists)

def partition(tup, part):
    return [index(tup, ind) for ind in part]

def index(tup, ind):
    return tuple(tup[i] for i in ind)
