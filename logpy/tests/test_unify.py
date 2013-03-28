from logpy.unify import (unify, unify_dict, unify_seq, reify_dict, reify,
        unify_object, reify_object)
from logpy.variables import var

def test_reify():
    x, y, z = var(), var(), var()
    s = {x: 1, y: 2, z: (x, y)}
    assert reify(x, s) == 1
    assert reify(10, s) == 10
    assert reify((1, y), s) == (1, 2)
    assert reify((1, (x, (y, 2))), s) == (1, (1, (2, 2)))
    assert reify(z, s) == (1, 2)

def test_reify_dict():
    x, y = var(), var()
    s = {x: 2, y: 4}
    e = {1: x, 3: {5: y}}
    assert reify_dict(e, s) == {1: 2, 3: {5: 4}}

def test_reify_complex():
    x, y = var(), var()
    s = {x: 2, y: 4}
    e = {1: x, 3: (y, 5)}

    assert reify(e, s) == {1: 2, 3: (4, 5)}

def test_unify():
    assert unify(1, 1, {}) == {}
    assert unify(1, 2, {}) == False
    assert unify(var(1), 2, {}) == {var(1): 2}
    assert unify(2, var(1), {}) == {var(1): 2}

def test_unify_seq():
    assert unify_seq((1, 2), (1, 2), {}) == {}
    assert unify_seq([1, 2], [1, 2], {}) == {}
    assert unify_seq((1, 2), (1, 2, 3), {}) == False
    assert unify_seq((1, var(1)), (1, 2), {}) == {var(1): 2}
    assert unify_seq((1, var(1)), (1, 2), {var(1): 3}) == False

def test_unify_dict():
    assert unify_dict({1: 2}, {1: 2}, {}) == {}
    assert unify_dict({1: 2}, {1: 3}, {}) == False
    assert unify_dict({2: 2}, {1: 2}, {}) == False
    assert unify_dict({1: var(5)}, {1: 2}, {}) == {var(5): 2}

def test_unify_complex():
    assert unify((1, {2: 3}), (1, {2: 3}), {}) == {}
    assert unify((1, {2: 3}), (1, {2: 4}), {}) == False
    assert unify((1, {2: var(5)}), (1, {2: 4}), {}) == {var(5): 4}

    assert unify({1: (2, 3)}, {1: (2, var(5))}, {}) == {var(5): 3}
    assert unify({1: [2, 3]}, {1: [2, var(5)]}, {}) == {var(5): 3}

class Foo(object):
        def __init__(self, a, b):
            self.a = a
            self.b = b
        def __eq__(self, other):
            return (self.a, self.b) == (other.a, other.b)
class Bar(object):
        def __init__(self, c):
            self.c = c
        def __eq__(self, other):
            return self.c == other.c

def test_unify_object():
    assert unify_object(Foo(1, 2), Foo(1, 2), {}) == {}
    assert unify_object(Foo(1, 2), Foo(1, 3), {}) == False
    assert unify_object(Foo(1, 2), Foo(1, var(3)), {}) == {var(3): 2}


def test_reify_object():
    obj = reify_object(Foo(1, var(3)), {var(3): 4})
    assert obj.a == 1
    assert obj.b == 4

def test_objects_full():
    from logpy.unify import unify_dispatch, reify_dispatch
    unify_dispatch[(Foo, Foo)] = unify_object
    unify_dispatch[(Bar, Bar)] = unify_object
    reify_dispatch[Foo] = reify_object
    reify_dispatch[Bar] = reify_object

    assert unify_object(Foo(1, Bar(2)), Foo(1, Bar(var(3))), {}) == {var(3): 2}
    assert reify(Foo(var('a'), Bar(Foo(var('b'), 3))),
                 {var('a'): 1, var('b'): 2}) == Foo(1, Bar(Foo(2, 3)))


    del reify_dispatch[Bar]
    del reify_dispatch[Foo]
    del unify_dispatch[(Foo, Foo)]
    del unify_dispatch[(Bar, Bar)]

def test_list_1():
    from logpy import run, eq
    x = var('x')
    y = var('y')
    rval = run(0, (x, y), (eq, Foo(1, [2]), Foo(x, [y])))
    assert rval == ((1, 2),)

def test_list_2():
    from logpy import run, eq
    x = var('x')
    y = var('y')
    rval = run(0, (x, y), (eq, Foo(1, [2]), Foo(x, y)))
    assert rval == ((1, [2]),)
