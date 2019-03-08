from __future__ import absolute_import

from collections import OrderedDict

from unification import var, isvar

from kanren.goals import (tailo, heado, appendo, seteq, conso, typo, nullo,
                          itero, isinstanceo, permuteq, membero, condp,
                          condpseq)
from kanren.core import (run, eq, goaleval, lall, lallgreedy, conde)
from kanren.cons import is_null, is_cons, car, cons


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


def test_nullo_itero():
    assert isvar(run(0, y, nullo([]))[0])
    assert isvar(run(0, y, nullo(None))[0])
    assert run(0, y, nullo(y))[0] is None
    assert run(0, y, (conso, var(), y, [1]), nullo(y))[0] == []
    assert run(0, y, (conso, var(), y, (1,)), nullo(y))[0] == ()

    assert run(1, y, conso(1, x, y), itero(y))[0] == [1]
    assert run(1, y, conso(1, x, y), conso(2, z, x), itero(y))[0] == [1, 2]

    # Make sure that the remaining results end in logic variables
    res_2 = run(2, y, conso(1, x, y), conso(2, z, x), itero(y))[1]
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


def test_condp():
    """Test `condp` using the example from “A Surprisingly Competitive
    Conditional Operator.”

    BOSKIN, BENJAMIN STRAHAN, WEIXI MA, DAVID THRANE CHRISTIANSEN, and DANIEL
    P. FRIEDMAN. n.d. “A Surprisingly Competitive Conditional Operator.”
    """
    def _ls_keys(ls):
        if isvar(ls):
            return ('use-maybe',)
        elif is_null(ls):
            return ('BASE',)
        elif is_cons(ls):
            return ('KEEP', 'SWAP')
        else:
            return ()

    def _o_keys(o):
        if isvar(o):
            return ('BASE', 'KEEP', 'SWAP')
        elif is_null(o):
            return ('BASE',)
        elif is_cons(o):
            if isvar(car(o)) or 'novel' == car(o):
                return ('KEEP', 'SWAP')
            else:
                return ('KEEP',)
        else:
            return ()

    def swap_somep(ls, o):
        a, d, res = var(), var(), var()
        res = (condp,
               # suggestion function and variable collections
               ((_ls_keys, ls),
                (_o_keys, o)),
               # branch goals
               [('BASE', ((nullo, ls), (nullo, o))),
                ('KEEP', ((eq, cons(a, d), ls),
                          (eq, cons(a, res), o),
                          (swap_somep, d, res))),
                ('SWAP', ((eq, cons(a, d), ls),
                          (eq, cons('novel', res), o),
                          (swap_somep, d, res)))])
        return res

    def swap_someo(ls, o):
        """The original `conde` version.
        """
        a, d, res = var(), var(), var()
        return (conde,
                [(nullo, ls),
                 (nullo, o)],
                [(eq, cons(a, d), ls),
                 (eq, cons(a, res), o),
                 (swap_someo, d, res)],
                [(eq, cons(a, d), ls),
                 (eq, cons('novel', res), o),
                 (swap_someo, d, res)])

    q, r = var('q'), var('r')

    condp_res = run(0, [q, r], (swap_somep, q, ['novel', r]))

    assert len(condp_res) == 4
    assert condp_res[0][0][0] == 'novel'
    assert isvar(condp_res[0][0][1])
    assert isvar(condp_res[0][1])

    assert isvar(condp_res[1][0][0])
    assert isvar(condp_res[1][0][1])
    assert isvar(condp_res[1][1])

    assert condp_res[2][0][0] == 'novel'
    assert isvar(condp_res[2][0][1])
    assert condp_res[2][1] == 'novel'

    assert isvar(condp_res[3][0][0])
    assert isvar(condp_res[3][0][1])
    assert condp_res[3][1] == 'novel'


def test_condpseq():

    def base_sug(a_branches):
        if a_branches['BRANCH1'] == 1:
            return ('BRANCH3',)
        else:
            return ('BRANCH2', 'BRANCH3',)

    def test_rel(a):
        return (condpseq,
                OrderedDict([
                    ('BRANCH1',
                     (None, (eq, a, 1))),
                    ('BRANCH2',
                     ((base_sug, a), (eq, a, 2))),
                    ('BRANCH3',
                     (None, (eq, a, 3)))
                ]))

    q = var('q')

    res = run(0, [q], test_rel(q))

    assert res == ([1], [3])
