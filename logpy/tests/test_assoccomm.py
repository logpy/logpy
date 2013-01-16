from logpy.core import var, run, fact, eq
from logpy.assoccomm import (unify_assoc, unify_comm, eq_assoc, eq_comm,
        operation, associative, commutative, eq_assoccomm, conde)

a = 'assoc_op'
c = 'comm_op'
x = var()
fact(associative, a)
fact(commutative, c)

def test_assoc():
    assert tuple(unify_assoc((a, 1, 2, 3), (a, 1, 2, 3), {}))
    assert tuple(unify_assoc((a, 1, 2, 3), (a, (a, 1, 2), 3), {}))
    assert tuple(unify_assoc((a, 1, 2, 3), (a, 1,x,3), {})) == ({x: 2},)
    assert tuple(unify_assoc((a, 1, 2, 3), (a, 1, x), {})) == \
                                 ({x: (a, 2, 3)},)
    assert tuple(unify_assoc((a, 1, 2, 3), (a, x, 3), {})) == \
                                 ({x: (a, 1, 2)},)
    assert tuple(unify_assoc((a, x, 3), (a, 1, 2, 3), {})) == \
                                 ({x: (a, 1, 2)},)

def test_eq_assoccomm():
    A, B = ((a, 1, 2), 3), ((a, 1, 2), 3)
    assert tuple(eq_assoccomm((a,1,2), (a,1,2))({}))
    assert tuple(eq_assoccomm(3, 3)({}))
    assert tuple(eq_assoccomm((1,2), (1,2))({}))
    assert tuple(conde(((eq_assoccomm, (a,1,2), (a,1,2)),
                        (eq_assoccomm, 3, 3)))({}))
    assert tuple(conde((eq_assoccomm, a, b) for a, b in zip(A, B))({}))

def test_comm():
    assert tuple(unify_comm((c, 1, 2, 3), (c, 1, 2, 3), {}))
    assert tuple(unify_comm((c, 3, 2, 1), (c, 1, 2, 3), {}))
    assert tuple(unify_comm((c, 1, 2, 3), (c, 1, x), {})) == \
                        tuple(({x: (c, 2, 3)}, {x: (c, 3, 2)}))
    assert tuple(unify_comm((c, (c, 3, 1), 2), (c, 1, 2, 3), {}))

def test_eq_assoc():
    assert run(0, x, eq_assoc((c, 1, 2, 3), (c, x, 3))) == ((c, 1, 2),)

def test_eq_comm():
    assert set(run(0, x, eq_comm((c, 1, 2, 3), (c, x, 3)))) == \
            set(((c, 1, 2), (c, 2, 1)))

def test_deep_commutativity():
    x, y = var('x'), var('y')

    e1 = (c, (c, 1, x), y)
    e2 = (c, 2, (c, 3, 1))
    assert run(0, (x,y), eq_comm(e1, e2)) == ((3, 2),)


"""
Failing test.  This would work if we flattened first
def test_deep_associativity():
    expr1 = (a, 1, 2, (a, x, 5, 6))
    expr2 = (a, (a, 1, 2), 3, 4, 5, 6)
    result = ({x: (a, 3, 4)})
    print tuple(unify_assoc(expr1, expr2, {}))
    assert tuple(unify_assoc(expr1, expr2, {})) == result
"""
