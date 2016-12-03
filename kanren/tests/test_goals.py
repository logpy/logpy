from __future__ import absolute_import

from unification import unify, var

from ..goals import (tailo, heado, appendo, seteq, conso, typo,
                          isinstanceo, permuteq, LCons, membero)
from ..core import run, eq, goaleval, lall

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


def test_goal_ordering():
    def lefto(q, p, list):
            # give me q such that q is left of p in list
            # zip(list, list[1:]) gives a list of 2-tuples of neighboring combinations
            # which can then be pattern-matched against the query
            return membero((q,p), zip(list, list[1:]))

    def nexto(q, p, list):
            # give me q such that q is next to p in list
            # match lefto(q, p) OR lefto(p, q)
            # requirement of vector args instead of tuples doesn't seem to be documented
            return conde([lefto(q, p, list)], [lefto(p, q, list)])

    houses = var()

    zebraRules = lall(
            # there are 5 houses
            (eq,            (var(), var(), var(), var(), var()), houses),
            # the Englishman's house is red
            (membero,       ('Englishman', var(), var(), var(), 'red'), houses),
            # the Swede has a dog
            (membero,       ('Swede', var(), var(), 'dog', var()), houses),
            # the Dane drinks tea
            (membero,       ('Dane', var(), 'tea', var(), var()), houses),
            # the Green house is left of the White house
            (lefto,         (var(), var(), var(), var(), 'green'),
                                    (var(), var(), var(), var(), 'white'), houses),
            # coffee is the drink of the green house
            (membero,       (var(), var(), 'coffee', var(), 'green'), houses),
            # the Pall Mall smoker has birds
            (membero,       (var(), 'Pall Mall', var(), 'birds', var()), houses),
            # the yellow house smokes Dunhills
            (membero,       (var(), 'Dunhill', var(), var(), 'yellow'), houses),
            # the middle house drinks milk
            (eq,            (var(), var(), (var(), var(), 'milk', var(), var()), var(), var()), houses),
            # the Norwegian is the first house
            (eq,            (('Norwegian', var(), var(), var(), var()), var(), var(), var(), var()), houses),
            # the Blend smoker is in the house next to the house with cats
            (nexto,         (var(), 'Blend', var(), var(), var()),
                                    (var(), var(), var(), 'cats', var()), houses),
            # the Dunhill smoker is next to the house where they have a horse
            (nexto,         (var(), 'Dunhill', var(), var(), var()),
                                    (var(), var(), var(), 'horse', var()), houses),
            # the Blue Master smoker drinks beer
            (membero,       (var(), 'Blue Master', 'beer', var(), var()), houses),
            # the German smokes Prince
            (membero,       ('German', 'Prince', var(), var(), var()), houses),
            # the Norwegian is next to the blue house
            (nexto,         ('Norwegian', var(), var(), var(), var()),
                                    (var(), var(), var(), var(), 'blue'), houses),
            # the house next to the Blend smoker drinks water
            (nexto,         (var(), 'Blend', var(), var(), var()),
                                    (var(), var(), 'water', var(), var()), houses),
            # one of the houses has a zebra--but whose?
            (membero,       (var(), var(), var(), 'zebra', var()), houses)
    )

    solutions = run(0, houses, zebraRules)
    zebraOwner = [house for house in solutions[0] if 'zebra' in house][0][0]
