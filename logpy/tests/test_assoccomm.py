from logpy.core import var, run, eq, goaleval, EarlyGoalError
from logpy.facts import fact
from logpy.assoccomm import (associative, commutative, conde,
        groupsizes_to_partition, assocunify, eq_comm, eq_assoc,
        eq_assoccomm, assocsized, buildo, op_args)
from logpy.util import raises
from logpy.dispatch import dispatch

a = 'assoc_op'
c = 'comm_op'
x = var()
fact(associative, a)
fact(commutative, c)

def results(g, s={}):
    return tuple(goaleval(g)(s))

def test_eq_comm():
    assert results(eq_comm(1, 1))
    assert results(eq_comm((c, 1, 2, 3), (c, 1, 2, 3)))
    assert results(eq_comm((c, 3, 2, 1), (c, 1, 2, 3)))
    assert not results(eq_comm((a, 3, 2, 1), (a, 1, 2, 3))) # not commutative
    assert not results(eq_comm((3, c, 2, 1), (c, 1, 2, 3)))
    assert not results(eq_comm((c, 1, 2, 1), (c, 1, 2, 3)))
    assert not results(eq_comm((a, 1, 2, 3), (c, 1, 2, 3)))
    assert len(results(eq_comm((c, 3, 2, 1), x))) >= 6




def test_eq_assoc():
    assert results(eq_assoc(1, 1))
    assert results(eq_assoc((a, 1, 2, 3), (a, 1, 2, 3)))
    assert not results(eq_assoc((a, 3, 2, 1), (a, 1, 2, 3)))
    assert results(eq_assoc((a, (a, 1, 2), 3), (a, 1, 2, 3)))
    assert results(eq_assoc((a, 1, 2, 3), (a, (a, 1, 2), 3)))
    o = 'op'
    assert not results(eq_assoc((o, 1, 2, 3), (o, (o, 1, 2), 3)))

    # See TODO in assocunify
    gen = results(eq_assoc((a, 1, 2, 3), x, n=2))
    assert set(g[x] for g in gen).issuperset(set([(a,(a,1,2),3), (a,1,(a,2,3))]))

def test_eq_assoccomm():
    x, y = var(), var()
    eqac = eq_assoccomm
    ac = 'commassoc_op'
    fact(commutative, ac)
    fact(associative, ac)
    assert results(eqac(1, 1))
    assert results(eqac((1,), (1,)))
    assert results(eqac((ac, (ac, 1, x), y), (ac, 2, (ac, 3, 1))))
    assert results((eqac, 1, 1))
    assert results(eqac((a, (a, 1, 2), 3), (a, 1, 2, 3)))
    assert results(eqac((ac, (ac, 1, 2), 3), (ac, 1, 2, 3)))
    assert results(eqac((ac, 3, (ac, 1, 2)), (ac, 1, 2, 3)))
    assert run(0, x, eqac((ac, 3, (ac, 1, 2)), (ac, 1, x, 3))) == (2,)

def test_expr():
    add = 'add'
    mul = 'mul'
    fact(commutative, Add)
    fact(associative, Add)
    fact(commutative, Mul)
    fact(associative, Mul)

    x, y = var('x'), var('y')

    pattern = (mul, (add, 1, x), y)                # (1 + x) * y
    expr    = (mul, 2, (add, 3, 1))                # 2 * (3 + 1)
    assert run(0, (x,y), eq_assoccomm(pattern, expr)) == ((3, 2),)

def test_deep_commutativity():
    x, y = var('x'), var('y')

    e1 = (c, (c, 1, x), y)
    e2 = (c, 2, (c, 3, 1))
    assert run(0, (x,y), eq_comm(e1, e2)) == ((3, 2),)

def test_groupsizes_to_parition():
    assert groupsizes_to_partition(2, 3) == [[0, 1], [2, 3, 4]]

def test_assocunify():
    assert tuple(assocunify(1, 1, {}))
    assert tuple(assocunify((a, 1, 1), (a, 1, 1), {}))
    assert tuple(assocunify((a, 1, 2, 3), (a, 1, (a, 2, 3)), {}))
    assert tuple(assocunify((a, 1, (a, 2, 3)), (a, 1, 2, 3), {}))
    assert tuple(assocunify((a, 1, (a, 2, 3), 4), (a, 1, 2, 3, 4), {}))
    assert tuple(assocunify((a, 1, x, 4), (a, 1, 2, 3, 4), {})) == \
                ({x: (a, 2, 3)},)

    gen = assocunify((a, 1, 2, 3), x, {}, n=2)
    assert set(g[x] for g in gen) == set([(a,(a,1,2),3), (a,1,(a,2,3))])

    gen = assocunify((a, 1, 2, 3), x, {})
    assert set(g[x] for g in gen) == set([(a,1,2,3), (a,(a,1,2),3), (a,1,(a,2,3))])

def test_assocsized():
    add = 'add'
    assert set(assocsized(add, (1, 2, 3), 2)) == \
            set((((add, 1, 2), 3), (1, (add, 2, 3))))
    assert set(assocsized(add, (1, 2, 3), 1)) == \
            set((((add, 1, 2, 3),),))

def test_objects():
    from logpy import variables, reify, assoccomm

    fact(commutative, Add)
    fact(associative, Add)
    assert tuple(goaleval(eq_assoccomm(add(1, 2, 3), add(3, 1, 2)))({}))
    assert tuple(goaleval(eq_assoccomm(add(1, 2, 3), add(3, 1, 2)))({}))

    x = var('x')

    print(tuple(goaleval(eq_assoccomm(add(1, 2, 3), add(1, 2, x)))({})))
    assert reify(x, tuple(goaleval(eq_assoccomm(add(1, 2, 3),
                                                add(1, 2, x)))({}))[0]) == 3

    assert reify(x, next(goaleval(eq_assoccomm(add(1, 2, 3),
                                               add(x, 2, 1)))({}))) == 3

    v = add(1,2,3)
    with variables(v):
        x = add(5, 6)
        print(reify(v, next(goaleval(eq_assoccomm(v, x))({}))))
        assert reify(v, next(goaleval(eq_assoccomm(v, x))({}))) == x

"""
Failing test.  This would work if we flattened first
def test_deep_associativity():
    expr1 = (a, 1, 2, (a, x, 5, 6))
    expr2 = (a, (a, 1, 2), 3, 4, 5, 6)
    result = ({x: (a, 3, 4)})
    print(tuple(unify_assoc(expr1, expr2, {})))
    assert tuple(unify_assoc(expr1, expr2, {})) == result
"""

def test_buildo():
    x = var('x')
    assert results(buildo('add', (1,2,3), x), {}) == ({x: ('add', 1, 2, 3)},)
    assert results(buildo(x, (1,2,3), ('add', 1,2,3)), {}) == ({x: 'add'},)
    assert results(buildo('add', x, ('add', 1,2,3)), {}) == ({x: (1,2,3)},)

class Node(object):
    def __init__(self, op, args):
        self.op = op
        self.args = args
    def __eq__(self, other):
        return (type(self) == type(other)
                and self.op == other.op
                and self.args == other.args)
    def __hash__(self):
        return hash((type(self), self.op, self.args))
    def __str__(self):
        return '%s(%s)' % (self.op.name, ', '.join(map(str, self.args)))
    __repr__ = __str__

class Operator(object):
    def __init__(self, name):
        self.name = name
Add = Operator('add')
Mul = Operator('mul')

add = lambda *args: Node(Add, args)
mul = lambda *args: Node(Mul, args)

@dispatch(Operator, (tuple, list))
def term(op, args):
    return Node(op, args)

@dispatch(Node)
def arguments(n):
    return n.args

@dispatch(Node)
def operator(n):
    return n.op


def test_op_args():
    print(op_args(add(1,2,3)))
    assert op_args(add(1,2,3)) == (Add, (1,2,3))
    assert op_args('foo') == (None, None)

def test_buildo_object():
    x = var('x')
    assert results(buildo(Add, (1,2,3), x), {}) == \
            ({x: add(1, 2, 3)},)
    print(results(buildo(x, (1,2,3), add(1,2,3)), {}))
    assert results(buildo(x, (1,2,3), add(1,2,3)), {}) == \
            ({x: Add},)
    assert results(buildo(Add, x, add(1,2,3)), {}) == \
            ({x: (1,2,3)},)


def test_eq_comm_object():
    x = var('x')
    fact(commutative, Add)
    fact(associative, Add)

    assert run(0, x, eq_comm(add(1, 2, 3), add(3, 1, x))) == (2,)

    print(set(run(0, x, eq_comm(add(1, 2), x))))
    assert set(run(0, x, eq_comm(add(1, 2), x))) == set((add(1, 2), add(2, 1)))

    print(set(run(0, x, eq_assoccomm(add(1, 2, 3), add(1, x)))))
    assert set(run(0, x, eq_assoccomm(add(1, 2, 3), add(1, x)))) == \
            set((add(2, 3), add(3, 2)))
