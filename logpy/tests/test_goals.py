from logpy.goals import (tailo, heado, appendo, seteq, conso, typo,
        isinstanceo, permuteq)
from logpy.core import var, run, eq, EarlyGoalError, goaleval, membero
from logpy.util import raises

def results(g, s={}):
    return tuple(goaleval(g)(s))

def test_heado():
    x, y = var('x'), var('y')
    assert results(heado(x, (1,2,3))) == ({x: 1},)
    assert results(heado(1, (x,2,3))) == ({x: 1},)
    raises(EarlyGoalError, lambda: heado(x, y))

def test_tailo():
    x, y = var('x'), var('y')
    assert results((tailo, x, (1,2,3))) == ({x: (2,3)},)
    raises(EarlyGoalError, lambda: tailo(x, y))

def test_conso():
    x = var()
    y = var()
    assert not results(conso(x, y, ()))
    assert results(conso(1, (2, 3), (1, 2, 3)))
    assert results(conso(x, (2, 3), (1, 2, 3))) == ({x: 1},)
    assert results(conso(1, (2, 3), x)) == ({x: (1, 2, 3)},)
    assert results(conso(x, y, (1, 2, 3))) == ({x: 1, y: (2, 3)},)
    assert results(conso(x, (2, 3), y)) == ({y: (x, 2, 3)},)
    # assert tuple(conde((conso(x, y, z), (membero, x, z)))({}))

def test_seteq():
    x = var('x')
    y = var('y')
    abc = tuple('abc')
    bca = tuple('bca')
    assert results(seteq(abc, bca))
    assert len(results(seteq(abc, x))) == 6
    assert len(results(seteq(x, abc))) == 6
    assert bca in run(0, x, seteq(abc, x))
    assert results(seteq((1, 2, 3), (3, x, 1))) == ({x: 2},)

    assert run(0, (x, y), seteq((1, 2, x), (2, 3, y)))[0] == (3, 1)
    assert not run(0, (x, y), seteq((4, 5, x), (2, 3, y)))

def test_permuteq():
    x = var('x')
    assert results(permuteq((1,2,2), (2,1,2)))
    assert not results(permuteq((1,2), (2,1,2)))
    assert not results(permuteq((1,2,3), (2,1,2)))
    assert not results(permuteq((1,2,1), (2,1,2)))

    assert set(run(0, x, permuteq(x, (1,2,2)))) == set(
            ((1,2,2), (2,1,2), (2,2,1)))

def test_typo():
    x = var('x')
    assert results(typo(3, int))
    assert not results(typo(3.3, int))
    assert run(0, x, membero(x, (1, 'cat', 2.2, 'hat')), (typo, x, str)) ==\
            ('cat', 'hat')

def test_isinstanceo():
    assert results(isinstanceo((3, int), True))
    assert not results(isinstanceo((3, float), True))
    assert results(isinstanceo((3, float), False))


def test_conso_early():
    x, y, z = var(), var(), var()
    assert (run(0, x, (conso, x, y, z), (eq, z, (1, 2, 3)))
            == (1,))

def test_appendo():
    x = var('x')
    assert results(appendo((), (1,2), (1,2))) == ({},)
    assert results(appendo((), (1,2), (1))) == ()
    assert results(appendo((1,2), (3,4), (1,2,3,4)))
    assert run(5, x, appendo((1,2,3), x, (1,2,3,4,5))) == ((4,5),)

"""
Failing test
def test_appendo2():
    print(run(5, x, appendo((1,2,3), (4,5), x)))
    assert run(5, x, appendo(x, (4,5), (1,2,3,4,5))) == ((1,2,3),)
    assert run(5, x, appendo((1,2,3), (4,5), x)) == ((1,2,3,4,5),)
"""
