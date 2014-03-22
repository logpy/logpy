from logpy.unifymore import (unify_object, reify_object,
        unify_slice, reify_object_attrs, unify_object_attrs, logify)
from logpy import var, run, eq
from logpy.unification import unify, reify
from logpy import variables
from logpy.unification import (unify_dispatch, reify, _reify,
        unify_isinstance_list, reify_isinstance_list, seq_registry)

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

def test_run_objects_with_context_manager():
    f = Foo(1, 1234)
    g = Foo(1, 2)
    unify_dispatch[(Foo, Foo)] = unify_object
    _reify.add((Foo, dict), reify_object)
    with variables(1234):
        assert unify_object(f, g, {})
        assert run(1, 1234, (eq, f, g)) == (2,)
        assert run(1, Foo(1234, 1234), (eq, f, g)) == (Foo(2, 2),)

    del unify_dispatch[(Foo, Foo)]

def test_unify_object():
    assert unify_object(Foo(1, 2), Foo(1, 2), {}) == {}
    assert unify_object(Foo(1, 2), Foo(1, 3), {}) == False
    assert unify_object(Foo(1, 2), Foo(1, var(3)), {}) == {var(3): 2}


def test_reify_object():
    obj = reify_object(Foo(1, var(3)), {var(3): 4})
    assert obj.a == 1
    assert obj.b == 4

    f = Foo(1, 2)
    assert reify_object(f, {}) is f

def test_objects_full():
    unify_dispatch[(Foo, Foo)] = unify_object
    unify_dispatch[(Bar, Bar)] = unify_object
    _reify.add((Foo, dict), reify_object)
    _reify.add((Bar, dict), reify_object)

    assert unify_object(Foo(1, Bar(2)), Foo(1, Bar(var(3))), {}) == {var(3): 2}
    assert reify(Foo(var('a'), Bar(Foo(var('b'), 3))),
                 {var('a'): 1, var('b'): 2}) == Foo(1, Bar(Foo(2, 3)))


    del unify_dispatch[(Foo, Foo)]
    del unify_dispatch[(Bar, Bar)]

class Foo2(Foo):
    def _as_logpy(self):
        return (type(self), self.a, self.b)

    @staticmethod
    def _from_logpy((typ, a, b)):
        return typ(a, b)

def test_objects_as_logpy():
    x = var()
    assert unify(Foo2(1, x), Foo2(1, 2), {}) == {x: 2}
    assert reify(Foo2(1, x), {x: 2}) == Foo2(1, 2)

def test_list_1():
    from logpy.unification import unify_dispatch
    unify_dispatch[(Foo, Foo)] = unify_object
    _reify.add((Foo, dict), reify_object)

    x = var('x')
    y = var('y')
    rval = run(0, (x, y), (eq, Foo(1, [2]), Foo(x, [y])))
    assert rval == ((1, 2),)

    rval = run(0, (x, y), (eq, Foo(1, [2]), Foo(x, y)))
    assert rval == ((1, [2]),)

    del unify_dispatch[(Foo, Foo)]

def test_unify_slice():
    x = var('x')
    y = var('y')

    assert unify_slice(slice(1), slice(1), {}) == {}
    assert unify(slice(1, 2, 3), x, {}) == {x: slice(1, 2, 3)}
    assert unify_slice(slice(1, 2, None), slice(x, y), {}) == {x: 1, y: 2}

def test_reify_slice():
    x = var('x')
    assert reify(slice(1, var(2), 3), {var(2): 10}) == slice(1, 10, 3)

def test_unify_object_attrs():
    x, y = var('x'), var('y')
    f, g = Foo(1, 2), Foo(x, y)
    assert unify_object_attrs(f, g, {}, ['a']) == {x: 1}
    assert unify_object_attrs(f, g, {}, ['b']) == {y: 2}
    assert unify_object_attrs(f, g, {}, []) == {}

def test_reify_object_attrs():
    x, y = var('x'), var('y')
    f, g = Foo(1, 2), Foo(x, y)
    s = {x: 1, y: 2}
    assert reify_object_attrs(g, s, ['a', 'b']) == f
    assert reify_object_attrs(g, s, ['a']) ==  Foo(1, y)
    assert reify_object_attrs(g, s, ['b']) ==  Foo(x, 2)
    assert reify_object_attrs(g, s, []) is g

def test_unify_isinstance_list():
    class Foo2(Foo): pass
    x = var('x')
    y = var('y')
    f, g = Foo2(1, 2), Foo2(x, y)

    unify_isinstance_list.append(((Foo, Foo), unify_object))
    reify_isinstance_list.append((Foo, reify_object))

    assert unify(f, g, {})
    assert reify(g, {x: 1, y: 2}) == f

    unify_isinstance_list.pop()
    reify_isinstance_list.pop()

def test_seq_registry():
    seq_registry.append((Foo, lambda x: (type(x), x.a, x.b)))

    x = var('x')
    y = var('y')
    f, g = Foo(1, 2), Foo(x, y)

    assert unify(f, g, {}) == {x: 1, y: 2}

    seq_registry.pop()

class A(object):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class B(A):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c
        self.data = {'a': a, 'b': b, 'c': c}

logify(A)

def test_logify():
    x = var('x')
    f = A(1, 2)
    g = A(1, x)
    assert unify(f, g, {}) == {x: 2}
    assert reify(g, {x: 2}) == f

class Aslot(object):
    __slots__ = ['a', 'b']
    def __eq__(self, other):
        return (self.a, self.b) == (other.a, other.b)

logify(Aslot)

def test_logify_slots():
    x = var('x')
    f = Aslot()
    f.a = 1
    f.b = 2
    g = Aslot()
    g.a = 1
    g.b = x
    assert unify(f, g, {}) == {x: 2}
    assert reify(g, {x: 2}) == f
