from logpy import var
from logpy.arith import lt, gt, lte, gte, add, sub, mul, mod

x = var('x')
y = var('y')
def results(g):
    return list(g({}))

def test_lt():
    assert results(lt(1, 2))
    assert not results(lt(2, 1))
    assert not results(lt(2, 2))

def test_gt():
    assert results(gt(2, 1))
    assert not results(gt(1, 2))
    assert not results(gt(2, 2))

def test_lte():
    assert results(lte(2, 2))

def test_gte():
    assert results(gte(2, 2))

def test_add():
    assert results(add(1, 2, 3))
    assert not results(add(1, 2, 4))
    assert results(add(1, 2, 3))

    assert results(add(1, 2, x)) == [{x: 3}]
    assert results(add(1, x, 3)) == [{x: 2}]
    assert results(add(x, 2, 3)) == [{x: 1}]

def test_sub():
    assert results(sub(3, 2, 1))
    assert not results(sub(4, 2, 1))

    assert results(sub(3, 2, x)) == [{x: 1}]
    assert results(sub(3, x, 1)) == [{x: 2}]
    assert results(sub(x, 2, 1)) == [{x: 3}]

def test_mul():
    assert results(mul(2, 3, 6))
    assert not results(mul(2, 3, 7))

    assert results(mul(2, 3, x)) == [{x: 6}]
    assert results(mul(2, x, 6)) == [{x: 3}]
    assert results(mul(x, 3, 6)) == [{x: 2}]

    assert mul.__name__ == 'mul'

def test_mod():
    assert results(mod(5, 3, 2))

def test_complex():
    from logpy import run, membero
    numbers = tuple(range(10))
    results = set(run(0, x, (sub, y, x, 1),
                            (membero, y, numbers),
                            (mod, y, 2, 0),
                            (membero, x, numbers)))
    expected = set((1, 3, 5, 7))
    print(results)
    assert results == expected
