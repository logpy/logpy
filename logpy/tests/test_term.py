from logpy.term import termify, term, operator, arguments
from logpy import var, unify, reify

@termify
class A(object):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def test_termify():
    x = var('x')
    f = A(1, 2)
    g = A(1, x)
    assert unify(f, g, {}) == {x: 2}
    assert reify(g, {x: 2}) == f


def test_arguments():
    assert arguments(A(1, 2)) == {'a': 1, 'b': 2}


def test_operator():
    assert operator(A(1, 2)) == A


def test_term():
    assert term(A, {'a': 1, 'b': 2}) == A(1, 2)


def test_inheritance():
    class B(A):
        pass

    x = var('x')
    f = B(1, 2)
    g = B(1, x)
    assert unify(f, g, {}) == {x: 2}
    assert reify(g, {x: 2}) == f


@termify
class Aslot(object):
    __slots__ = ['a', 'b']
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __eq__(self, other):
        return (self.a, self.b) == (other.a, other.b)


def test_arguments_slot():
    assert arguments(Aslot(1, 2)) == {'a': 1, 'b': 2}


def test_operator_slot():
    assert operator(Aslot(1, 2)) == Aslot


def test_term_slot():
    assert term(Aslot, {'a': 1, 'b': 2}) == Aslot(1, 2)


def test_termify_slots():
    x = var('x')
    f = Aslot(1, 2)
    g = Aslot(1, x)
    assert unify(f, g, {}) == {x: 2}
    assert reify(g, {x: 2}) == f
