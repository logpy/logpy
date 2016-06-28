from unification import unify, var

from logpy.goals import (tailo, heado, appendo, seteq, conso, typo,
                         isinstanceo, permuteq, LCons, membero)
from logpy.core import run, eq, goaleval

x, y, z, w = var('x'), var('y'), var('z'), var('w')


def results(g, s={}):
    return tuple(goaleval(g)(s))


def test_heado():
    assert results(heado(x, (1, 2, 3))) == ({x: 1}, )
    assert results(heado(1, (x, 2, 3))) == ({x: 1}, )
    assert results(heado(x, ())) == ()

    assert run(0, x, (heado, x, z), (conso, 1, y, z)) == (1, )


def test_tailo():
    assert results((tailo, x, (1, 2, 3))) == ({x: (2, 3)}, )
    assert results((tailo, x, (1, ))) == ({x: ()}, )
    assert results((tailo, x, ())) == ()

    assert run(0, y, (tailo, y, z), (conso, x, (1, 2), z)) == ((1, 2), )


def test_conso():
    assert not results(conso(x, y, ()))
    assert results(conso(1, (2, 3), (1, 2, 3)))
    assert results(conso(x, (2, 3), (1, 2, 3))) == ({x: 1}, )
    assert results(conso(1, (2, 3), x)) == ({x: (1, 2, 3)}, )
    assert results(conso(x, y, (1, 2, 3))) == ({x: 1, y: (2, 3)}, )
    assert results(conso(x, (2, 3), y)) == ({y: (x, 2, 3)}, )

    # Verify that the first goal that's found does not contain unbound logic
    # variables.
    assert run(1, y, conso(1, x, y))[0] == (1, )
    # But (potentially infinitely many goals _are_ generated).
    assert isinstance(run(2, y, conso(1, x, y))[1], LCons)

    assert run(1, y, conso(1, x, y), conso(2, z, x))[0] == (1, 2)
    # assert tuple(conde((conso(x, y, z), (membero, x, z)))({}))


def test_lcons():
    assert unify(LCons(1, ()), (x, )) == {x: 1}
    assert unify(LCons(1, (x, )), (x, y)) == {x: 1, y: 1}
    assert unify((x, y), LCons(1, (x, ))) == {x: 1, y: 1}
    assert unify(LCons(x, y), ()) == False
    assert list(LCons(1, LCons(2, x))) == [1, 2]


def test_membero():
    x = var('x')
    assert set(run(5, x, membero(x, (1, 2, 3)), membero(x, (2, 3, 4)))) \
           == {2, 3}

    assert run(5, x, membero(2, (1, x, 3))) == (2, )
    assert run(0, x, (membero, 1, (1, 2, 3))) == (x, )
    assert run(0, x, (membero, 1, (2, 3))) == ()


def test_membero_can_be_reused():
    g = membero(x, (0, 1, 2))
    assert list(goaleval(g)({})) == [{x: 0}, {x: 1}, {x: 2}]
    assert list(goaleval(g)({})) == [{x: 0}, {x: 1}, {x: 2}]


def test_uneval_membero():
    assert set(run(100, x,
                   (membero, y, ((1, 2, 3), (4, 5, 6))),
                   (membero, x, y))) == \
           {1, 2, 3, 4, 5, 6}


def test_seteq():
    abc = tuple('abc')
    bca = tuple('bca')
    assert results(seteq(abc, bca))
    assert len(results(seteq(abc, x))) == 6
    assert len(results(seteq(x, abc))) == 6
    assert bca in run(0, x, seteq(abc, x))
    assert results(seteq((1, 2, 3), (3, x, 1))) == ({x: 2}, )

    assert run(0, (x, y), seteq((1, 2, x), (2, 3, y)))[0] == (3, 1)
    assert not run(0, (x, y), seteq((4, 5, x), (2, 3, y)))


def test_permuteq():
    assert results(permuteq((1, 2), (2, 1)))
    assert results(permuteq((1, 2, 2), (2, 1, 2)))
    assert not results(permuteq((1, 2), (2, 1, 2)))
    assert not results(permuteq((1, 2, 3), (2, 1, 2)))
    assert not results(permuteq((1, 2, 1), (2, 1, 2)))

    assert set(run(0, x, permuteq(x, (1, 2, 2)))) == set(((1, 2, 2), (2, 1, 2),
                                                          (2, 2, 1)))


def test_typo():
    assert results(typo(3, int))
    assert not results(typo(3.3, int))
    assert run(0, x, membero(x, (1, 'cat', 2.2, 'hat')), (typo, x, str)) ==\
            ('cat', 'hat')


def test_isinstanceo():
    assert results(isinstanceo((3, int), True))
    assert not results(isinstanceo((3, float), True))
    assert results(isinstanceo((3, float), False))


def test_conso_early():
    assert (run(0, x, (conso, x, y, z), (eq, z, (1, 2, 3))) == (1, ))


def test_appendo():
    assert results(appendo((), (1, 2), (1, 2))) == ({}, )
    assert results(appendo((), (1, 2), (1))) == ()
    assert results(appendo((1, 2), (3, 4), (1, 2, 3, 4)))
    assert run(5, x, appendo((1, 2, 3), x, (1, 2, 3, 4, 5))) == ((4, 5), )
    assert run(5, x, appendo(x, (4, 5), (1, 2, 3, 4, 5))) == ((1, 2, 3), )
    assert run(5, x, appendo((1, 2, 3), (4, 5), x)) == ((1, 2, 3, 4, 5), )


def test_appendo2():
    for t in [tuple(range(i)) for i in range(5)]:
        for xi, yi in run(0, (x, y), appendo(x, y, t)):
            assert xi + yi == t
        results = run(0, (x, y, z), (appendo, x, y, w), (appendo, w, z, t))
        for xi, yi, zi in results:
            assert xi + yi + zi == t
