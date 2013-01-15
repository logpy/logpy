from logpy.core import var, run
from logpy.assoccomm import unify_assoc, unify_comm, eq_assoc, eq_comm

add = 'add'
mul = 'mul'
x = var()

def test_assoc():
    assert tuple(unify_assoc((add, 1, 2, 3), (add, 1, 2, 3), {}))
    assert tuple(unify_assoc((add, 1, 2, 3), (add, (add, 1, 2), 3), {}))
    assert tuple(unify_assoc((add, 1, 2, 3), (add, 1,x,3), {})) == ({x: 2},)
    assert tuple(unify_assoc((add, 1, 2, 3), (add, 1, x), {})) == \
                                 ({x: (add, 2, 3)},)
    assert tuple(unify_assoc((add, 1, 2, 3), (add, x, 3), {})) == \
                                 ({x: (add, 1, 2)},)
    assert tuple(unify_assoc((add, x, 3), (add, 1, 2, 3), {})) == \
                                 ({x: (add, 1, 2)},)

def test_comm():
    assert tuple(unify_comm((add, 1, 2, 3), (add, 1, 2, 3), {}))
    assert tuple(unify_comm((add, 3, 2, 1), (add, 1, 2, 3), {}))
    assert tuple(unify_comm((add, 1, 2, 3), (add, 1, x), {})) == \
                        tuple(({x: (add, 2, 3)}, {x: (add, 3, 2)}))
    assert tuple(unify_comm((add, (add, 3, 1), 2), (add, 1, 2, 3), {}))

def test_eq_assoc():
    assert run(0, x, eq_assoc((add, 1, 2, 3), (add, x, 3))) == ((add, 1, 2),)

def test_eq_comm():
    assert set(run(0, x, eq_comm((add, 1, 2, 3), (add, x, 3)))) == \
            set(((add, 1, 2), (add, 2, 1)))

def test_deep_commutativity():
    x, y = var('x'), var('y')

    e1 = (mul, (add, 1, x), y)
    e2 = (mul, 2, (add, 3, 1))
    assert run(0, (x,y), eq_comm(e1, e2)) == ((3, 2),)


"""
Failing Test
def test_deep_associativity():
    add = 'add'
    x = var()
    expr1 = (add, 1, 2, (add, x, 5, 6))
    expr2 = (add, (add, 1, 2), 3, 4, 5, 6)
    result = ({x: (add, 3, 4)})
    print tuple(unify_assoc(expr1, expr2, {}))
    assert tuple(unify_assoc(expr1, expr2, {})) == result
"""
