from __future__ import absolute_import

from itertools import count

import pytest
from pytest import raises
from unification import var

from ..goals import membero
from ..core import (run, fail, eq, conde, goaleval, lany, lallgreedy,
                    lanyseq, earlyorder, EarlyGoalError, lall, earlysafe,
                    lallfirst, condeseq)
from ..util import evalt

w, x, y, z = 'wxyz'


def test_eq():
    x = var('x')
    assert tuple(eq(x, 2)({})) == ({x: 2}, )
    assert tuple(eq(x, 2)({x: 3})) == ()


def test_lany():
    x = var('x')
    assert len(tuple(lany(eq(x, 2), eq(x, 3))({}))) == 2
    assert len(tuple(lany((eq, x, 2), (eq, x, 3))({}))) == 2


# Test that all three implementations of lallgreedy behave identically for
# correctly ordered goals.
@pytest.mark.parametrize('lall_impl', [lallgreedy, lall, lallfirst])
def test_lall(lall_impl):
    x, y = var('x'), var('y')
    assert results(lall_impl((eq, x, 2))) == ({x: 2}, )
    assert results(lall_impl((eq, x, 2), (eq, x, 3))) == ()
    assert results(lall_impl()) == ({}, )

    assert run(0, x, lall_impl((eq, y, (1, 2)), (membero, x, y)))
    assert run(0, x, lall_impl()) == (x, )
    with pytest.raises(EarlyGoalError):
        run(0, x, lall_impl(membero(x, y)))


@pytest.mark.parametrize('lall_impl', [lall, lallfirst])
def test_safe_reordering_lall(lall_impl):
    x, y = var('x'), var('y')
    assert run(0, x, lall_impl((membero, x, y), (eq, y, (1, 2)))) == (1, 2)


def test_earlysafe():
    x, y = var('x'), var('y')
    assert earlysafe((eq, 2, 2))
    assert earlysafe((eq, 2, 3))
    assert earlysafe((membero, x, (1, 2, 3)))
    assert not earlysafe((membero, x, y))


def test_earlyorder():
    x, y = var(), var()
    assert earlyorder((eq, 2, x)) == ((eq, 2, x), )
    assert earlyorder((eq, 2, x), (eq, 3, x)) == ((eq, 2, x), (eq, 3, x))
    assert earlyorder(
        (membero, x, y), (eq, y, (1, 2, 3)))[0] == (eq, y, (1, 2, 3))


def test_conde():
    x = var('x')
    assert results(conde([eq(x, 2)], [eq(x, 3)])) == ({x: 2}, {x: 3})
    assert results(conde([eq(x, 2), eq(x, 3)])) == ()


def test_condeseq():
    x = var('x')
    assert set(run(0, x, condeseq(([eq(x, 2)], [eq(x, 3)])))) == {2, 3}
    assert set(run(0, x, condeseq([[eq(x, 2), eq(x, 3)]]))) == set()

    goals = ([eq(x, i)] for i in count())  # infinite number of goals
    assert run(1, x, condeseq(goals)) == (0, )
    assert run(1, x, condeseq(goals)) == (1, )


def test_short_circuit():
    def badgoal(s):
        raise NotImplementedError()

    x = var('x')
    tuple(run(5, x, fail, badgoal))  # Does not raise exception


def test_run():
    x, y, z = map(var, 'xyz')
    assert run(1, x, eq(x, 1)) == (1, )
    assert run(2, x, eq(x, 1)) == (1, )
    assert run(0, x, eq(x, 1)) == (1, )
    assert run(1, x, eq(x, (y, z)), eq(y, 3), eq(z, 4)) == ((3, 4), )
    assert set(run(2, x, conde([eq(x, 1)], [eq(x, 2)]))) == set((1, 2))


def test_run_output_reify():
    x = var()
    assert run(0, (1, 2, x), eq(x, 3)) == ((1, 2, 3), )


def test_lanyseq():
    x = var('x')
    g = lanyseq(((eq, x, i) for i in range(3)))
    assert list(goaleval(g)({})) == [{x: 0}, {x: 1}, {x: 2}]
    assert list(goaleval(g)({})) == [{x: 0}, {x: 1}, {x: 2}]

    # Test lanyseq with an infinite number of goals.
    assert set(run(3, x, lanyseq(((eq, x, i) for i in count())))) == {0, 1, 2}
    assert set(run(3, x, (lanyseq, ((eq, x, i) for i in count())))) == \
           {0, 1, 2}


def test_evalt():
    add = lambda x, y: x + y
    assert evalt((add, 2, 3)) == 5
    assert evalt(add(2, 3)) == 5
    assert evalt((1, 2)) == (1, 2)


def test_goaleval():
    x, y = var('x'), var('y')
    g = eq(x, 2)
    assert goaleval(g) == g
    assert callable(goaleval((eq, x, 2)))
    with raises(EarlyGoalError):
        goaleval((membero, x, y))
    assert callable(goaleval((lallgreedy, (eq, x, 2))))


def test_lany_is_early_safe():
    x = var()
    y = var()
    assert run(0, x, lany((membero, x, y), (eq, x, 2))) == (2, )


def results(g, s={}):
    return tuple(goaleval(g)(s))


def test_dict():
    x = var()
    assert run(0, x, eq({1: x}, {1: 2})) == (2, )
