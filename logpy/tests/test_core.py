from logpy.core import (walk, walkstar, isvar, var, unify, unique, eq, conde,
        bind, bindstar, run, membero, evalt, isempty, fail, success,
        Relation, fact, facts, take, reify, goal_tuple_eval, tailo, heado,
        appendo, unique_dict, interleave, intersection)
import itertools
from unittest import expectedFailure as FAIL

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

def test_reify():
    x, y, z = var(), var(), var()
    s = {x: 1, y: 2, z: (x, y)}
    assert reify(x, s) == 1
    assert reify(10, s) == 10
    assert reify((1, y), s) == (1, 2)
    assert reify((1, (x, (y, 2))), s) == (1, (1, (2, 2)))
    assert reify(z, s) == (1, 2)

def test_isvar():
    assert not isvar(3)
    assert isvar(var(3))

def test_var():
    assert var(1) == var(1)

def test_unify():
    assert unify(1, 1, {}) == {}
    assert unify(1, 2, {}) == False
    assert unify(var(1), 2, {}) == {var(1): 2}
    assert unify(2, var(1), {}) == {var(1): 2}
    assert unify((1, 2), (1, 2), {}) == {}
    assert unify((1, 2), (1, 2, 3), {}) == False
    assert unify((1, var(1)), (1, 2), {}) == {var(1): 2}
    assert unify((1, var(1)), (1, 2), {var(1): 3}) == False

def test_unique():
    assert tuple(unique((1,2,3))) == (1,2,3)
    assert tuple(unique((1,2,1,3))) == (1,2,3)

def test_unique_dict():
    assert tuple(unique_dict(({1: 2}, {2: 3}))) == ({1: 2}, {2: 3})
    assert tuple(unique_dict(({1: 2}, {1: 2}))) == ({1: 2},)

def test_intersection():
    a,b,c = (1,2,3,4), (2,3,4,5), (3,4,5,6)

    print tuple(intersection(a,b,c))
    assert tuple(intersection(a,b,c)) == (3,4)

def test_eq():
    x = var('x')
    assert tuple(eq(x, 2)({})) == ({x: 2},)
    assert tuple(eq(x, 2)({x: 3})) == ()

def test_conde():
    x = var('x')
    assert tuple(conde([eq(x, 2)], [eq(x, 3)])({})) == ({x: 2}, {x: 3})
    assert tuple(conde([eq(x, 2), eq(x, 3)])({})) == ()

def test_bind():
    x = var('x')
    stream = tuple({x: i} for i in range(5))
    success = lambda s: (s,)
    assert tuple(bind(stream, success)) == stream
    assert tuple(bind(stream, eq(x, 3))) == ({x: 3},)

def test_bindstar():
    x = var('x')
    stream = tuple({x: i} for i in range(5))
    success = lambda s: (s,)
    assert tuple(bindstar(stream, success)) == stream
    assert tuple(bindstar(stream, eq(x, 3))) == ({x: 3},)
    assert tuple(bindstar(stream, success, eq(x, 3))) == ({x: 3},)
    assert tuple(bindstar(stream, eq(x, 2), eq(x, 3))) == ()

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

def test_take():
    assert take(2, range(5)) == (0, 1)
    assert take(0, range(5)) == (0, 1, 2, 3, 4)
    assert take(None, range(5)) == range(5)

def test_membero():
    x = var('x')
    assert set(run(5, x, membero(x, (1,2,3)),
                         membero(x, (2,3,4)))) == set((2,3))
    assert run(5, x, membero(2, (1, x, 3))) == (2,)

def test_evalt():
    add = lambda x, y: x + y
    assert evalt((add, 2, 3)) == 5
    assert evalt(add(2, 3)) == 5
    assert evalt((1,2)) == (1,2)

def test_bindstar_evalt():
    x = var('x')
    stream = bindstar(({},), success, (eq, x, 1))
    assert tuple(stream) == ({x: 1},)

def test_isempty():
    assert isempty(())
    assert not isempty((1,2))
    it = (x for x in (1,2))
    a, it = itertools.tee(it, 2)
    assert not isempty(a)
    assert next(it) == 1

def test_relation():
    parent = Relation()
    fact(parent, "Homer", "Bart")
    fact(parent, "Homer", "Lisa")
    fact(parent, "Marge", "Bart")
    fact(parent, "Marge", "Lisa")
    fact(parent, "Abe", "Homer")
    fact(parent, "Jackie", "Marge")

    x = var('x')
    assert set(run(5, x, parent("Homer", x))) == set(("Bart", "Lisa"))
    assert set(run(5, x, parent(x, "Bart")))  == set(("Homer", "Marge"))

    def grandparent(x, z):
        y = var()
        return conde((parent(x, y), parent(y, z)))

    assert set(run(5, x, grandparent(x, "Bart") )) == set(("Abe", "Jackie"))

def test_var_inputs():
    assert var(1) == var(1)
    assert var() != var()

def test_fact():
    rel = Relation()
    fact(rel, 1, 2)
    assert (1, 2) in rel.facts
    assert (10, 10) not in rel.facts

    facts(rel, (2, 3), (3, 4))
    assert (2, 3) in rel.facts
    assert (3, 4) in rel.facts

def test_uneval_membero():
    x, y = var('x'), var('y')
    assert set(run(100, x, membero(y, ((1,2,3),(4,5,6))), (membero, x, y))) == \
           set((1,2,3,4,5,6))

def test_goal_tuple_eval():
    x, y = var(), var()
    s = {y: (1, 2)}
    results = tuple(goal_tuple_eval((membero, x, y))(s))
    assert all(res[x] in (1, 2) for res in results)

def test_interleave():
    assert ''.join(interleave(('ABC', '123'))) == 'A1B2C3'
    assert ''.join(interleave(('ABC', '1'))) == 'A1BC'

def test_heado():
    x = var('x')
    assert tuple(heado(x, (1,2,3))({})) == ({x: 1},)
    assert tuple(heado(1, (x,2,3))({})) == ({x: 1},)

def test_tailo():
    x = var('x')
    assert tuple(tailo(x, (1,2,3))({})) == ({x: (2,3)},)

def test_appendo():
    x = var('x')
    assert tuple(appendo((), (1,2), (1,2))({})) == ({},)
    assert tuple(appendo((), (1,2), (1))({})) == ()
    assert tuple(appendo((1,2), (3,4), (1,2,3,4))({}))
    assert run(5, x, appendo((1,2,3), x, (1,2,3,4,5))) == ((4,5),)

def failing_test_appendo():
    pass
    #assert run(5, x, appendo((1,2,3), (4,5), x)) == ((1,2,3,4,5),)
    #assert run(5, x, appendo(x, (4,5), (1,2,3,4,5))) == ((1,2,3),)
