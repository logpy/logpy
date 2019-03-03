from __future__ import absolute_import

from unification import var, isvar

from kanren.goals import (tailo, heado, appendo, seteq, conso, typo,
                          listo, isinstanceo, permuteq, membero)
from kanren.core import run, eq, goaleval, lall, lallgreedy, EarlyGoalError

x, y, z, w = var('x'), var('y'), var('z'), var('w')


def results(g, s={}):
    return tuple(goaleval(g)(s))


def test_heado():
    assert (x, 1) in results(heado(x, (1, 2, 3)))[0].items()
    assert (x, 1) in results(heado(1, (x, 2, 3)))[0].items()
    assert results(heado(x, ())) == ()

    assert run(0, x, (heado, x, z), (conso, 1, y, z)) == (1, )


def test_tailo():
    assert (x, (2, 3)) in results((tailo, x, (1, 2, 3)))[0].items()
    assert (x, ()) in results((tailo, x, (1, )))[0].items()
    assert results((tailo, x, ())) == ()

    assert run(0, y, (tailo, y, z), (conso, x, (1, 2), z)) == ((1, 2), )


def test_conso():
    assert not results(conso(x, y, ()))
    assert results(conso(1, (2, 3), (1, 2, 3)))
    assert results(conso(x, (2, 3), (1, 2, 3))) == ({x: 1}, )
    assert results(conso(1, (2, 3), x)) == ({x: (1, 2, 3)}, )
    assert results(conso(x, y, (1, 2, 3))) == ({x: 1, y: (2, 3)}, )
    assert results(conso(x, (2, 3), y)) == ({y: (x, 2, 3)}, )

    # Confirm that custom types are preserved.
    class mytuple(tuple):
        def __add__(self, other):
            return type(self)(super(mytuple, self).__add__(other))

    assert type(results(conso(x, mytuple((2, 3)), y))[0][y]) == mytuple


def test_listo():
    assert run(1, y, conso(1, x, y), listo(y))[0] == [1]
    assert run(1, y, conso(1, x, y), conso(2, z, x), listo(y))[0] == [1, 2]

    # Make sure that the remaining results end in logic variables
    res_2 = run(2, y, conso(1, x, y), conso(2, z, x), listo(y))[1]
    assert res_2[:2] == [1, 2]
    assert isvar(res_2[-1])


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


def test_goal_ordering():
    # Regression test for https://github.com/logpy/logpy/issues/58

    def lefto(q, p, lst):
        if isvar(lst):
            raise EarlyGoalError()
        return membero((q, p), zip(lst, lst[1:]))

    vals = var()

    # Verify the solution can be computed when we specify the execution
    # ordering.
    rules_greedy = (
        lallgreedy,
        (eq, (var(), var()), vals),
        (lefto, 'green', 'white', vals),
    )

    solution, = run(1, vals, rules_greedy)
    assert solution == ('green', 'white')

    # Verify that attempting to compute the "safe" order does not itself cause
    # the evaluation to fail.
    rules_greedy = (
        lall,
        (eq, (var(), var()), vals),
        (lefto, 'green', 'white', vals),
    )

    solution, = run(1, vals, rules_greedy)
    assert solution == ('green', 'white')
