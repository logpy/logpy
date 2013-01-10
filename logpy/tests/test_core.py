from core import (walk, walk_star, isvar, var, unify, unique, eq, conde, bind,
        bindstar, rrun, membero)

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
    assert walk_star(x, s) == (5, 6)

def test_isvar():
    assert not isvar(3)
    assert isvar((var, 3))

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

def test_eq():
    x = var('x')
    assert tuple(eq(x, 2)({})) == ({x: 2},)
    assert tuple(eq(x, 2)({x: 3})) == ()

def test_conde():
    x = var('x')
    assert tuple(conde(eq(x, 2), eq(x, 3))({})) == ({x: 2}, {x: 3})

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

def test_run():
    x,y,z = map(var, 'xyz')
    assert rrun(1, x,  eq(x, 1)) == (1,)
    assert rrun(2, x,  eq(x, 1)) == (1,)
    assert rrun(1, x,  eq(x, (y, z)),
                       eq(y, 3),
                       eq(z, 4)) == ((3, 4),)
    assert set(rrun(2, x, conde(eq(x, 1), eq(x, 2)))) == set((1, 2))

def test_membero():
    x = var('x')
    assert set(rrun(5, x, membero(x, (1,2,3)),
                          membero(x, (2,3,4)))) == set((2,3))
    assert rrun(5, x, membero(2, (1, x, 3))) == (2,)
