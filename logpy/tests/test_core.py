from logpy.core import (walk, walkstar, isvar, var, run,
        membero, evalt, fail, success, eq, conde,
        condeseq, goaleval, lany, lall, lanyseq,
        goalexpand, earlyorder, EarlyGoalError, lallearly, earlysafe)
import itertools
from logpy.util import raises

w, x, y, z = 'wxyz'

def test_walk():
    s = {1: 2, 2: 3}
    assert walk(2, s) == 3
    assert walk(1, s) == 3
    assert walk(4, s) == 4

def test_deep_walk():
    """ Page 30 of Byrd thesis """
    s = {z: 6, y: 5, x: (y, z)}
    assert walk(x, s) == (y, z)
    assert walkstar(x, s) == (5, 6)

def test_eq():
    x = var('x')
    assert tuple(eq(x, 2)({})) == ({x: 2},)
    assert tuple(eq(x, 2)({x: 3})) == ()

def test_lany():
    x = var('x')
    assert len(tuple(lany(eq(x, 2), eq(x, 3))({}))) == 2
    assert len(tuple(lany((eq, x, 2), (eq, x, 3))({}))) == 2

def test_lall():
    x = var('x')
    assert results(lall((eq, x, 2))) == ({x: 2},)
    assert results(lall((eq, x, 2), (eq, x, 3))) == ()

def test_earlysafe():
    x, y = var('x'), var('y')
    assert earlysafe((eq, 2, 2))
    assert earlysafe((eq, 2, 3))
    assert earlysafe((membero, x, (1,2,3)))
    assert not earlysafe((membero, x, y))

def test_earlyorder():
    x, y = var(), var()
    assert earlyorder((eq, 2, x)) == ((eq, 2, x),)
    assert earlyorder((eq, 2, x), (eq, 3, x)) == ((eq, 2, x), (eq, 3, x))
    assert earlyorder((membero, x, y), (eq, y, (1,2,3)))[0] == (eq, y, (1,2,3))

def test_conde():
    x = var('x')
    assert results(conde([eq(x, 2)], [eq(x, 3)])) == ({x: 2}, {x: 3})
    assert results(conde([eq(x, 2), eq(x, 3)])) == ()

"""
def test_condeseq():
    x = var('x')
    assert tuple(condeseq(([eq(x, 2)], [eq(x, 3)]))({})) == ({x: 2}, {x: 3})
    assert tuple(condeseq([[eq(x, 2), eq(x, 3)]])({})) == ()

    goals = ([eq(x, i)] for i in itertools.count()) # infinite number of goals
    assert next(condeseq(goals)({})) == {x: 0}
"""

def test_short_circuit():
    def badgoal(s):
        raise NotImplementedError()

    x = var('x')
    tuple(run(5, x, fail, badgoal)) # Does not raise exception

def test_run():
    x,y,z = map(var, 'xyz')
    assert run(1, x,  eq(x, 1)) == (1,)
    assert run(2, x,  eq(x, 1)) == (1,)
    assert run(0, x,  eq(x, 1)) == (1,)
    assert run(1, x,  eq(x, (y, z)),
                       eq(y, 3),
                       eq(z, 4)) == ((3, 4),)
    assert set(run(2, x, conde([eq(x, 1)], [eq(x, 2)]))) == set((1, 2))

def test_run_output_reify():
    x = var()
    assert run(0, (1, 2, x), eq(x, 3)) == ((1, 2, 3),)

def test_membero():
    x = var('x')
    assert set(run(5, x, membero(x, (1,2,3)),
                         membero(x, (2,3,4)))) == set((2,3))

    assert run(5, x, membero(2, (1, x, 3))) == (2,)

def test_lanyseq():
    x = var('x')
    g = lanyseq(((eq, x, i) for i in range(3)))
    assert list(goaleval(g)({})) == [{x: 0}, {x: 1}, {x: 2}]
    assert list(goaleval(g)({})) == [{x: 0}, {x: 1}, {x: 2}]

def test_membero_can_be_reused():
    x = var('x')
    g = membero(x, (0, 1, 2))
    assert list(goaleval(g)({})) == [{x: 0}, {x: 1}, {x: 2}]
    assert list(goaleval(g)({})) == [{x: 0}, {x: 1}, {x: 2}]

def test_evalt():
    add = lambda x, y: x + y
    assert evalt((add, 2, 3)) == 5
    assert evalt(add(2, 3)) == 5
    assert evalt((1,2)) == (1,2)

def test_uneval_membero():
    x, y = var('x'), var('y')
    assert set(run(100, x, (membero, y, ((1,2,3),(4,5,6))), (membero, x, y))) == \
           set((1,2,3,4,5,6))

def test_goaleval():
    x, y = var('x'), var('y')
    g = eq(x, 2)
    assert goaleval(g) == g
    assert callable(goaleval((eq, x, 2)))
    raises(EarlyGoalError, lambda: goaleval((membero, x, y)))
    assert callable(goaleval((lall, (eq, x, 2))))

def test_goalexpand():
    def growing_goal(*args):
        if len(args) < 10:
            return (growing_goal, 1) + tuple(args)
        else:
            return lambda s: (1,)

    g = (growing_goal, 2)
    assert goalexpand(g) == (growing_goal, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2)

def test_early():
    x, y = var(), var()
    assert run(0, x, lallearly((eq, y, (1, 2)), (membero, x, y)))
    assert run(0, x, lallearly((membero, x, y), (eq, y, (1, 2))))

def test_lany_is_early_safe():
    x = var()
    y = var()
    assert run(0, x, lany((membero, x, y), (eq, x, 2))) == (2,)

def results(g, s={}):
    return tuple(goaleval(g)(s))

def test_dict():
    x = var()
    assert run(0, x, eq({1: x}, {1: 2})) == (2,)
