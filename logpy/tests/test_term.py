from logpy.term import term, operator, arguments, unifiable_with_term
from logpy import var, unify, reify
from logpy.dispatch import dispatch

def test_arguments():
    assert arguments(('add', 1, 2, 3)) == (1, 2, 3)


def test_operator():
    assert operator(('add', 1, 2, 3)) == 'add'


def test_term():
    assert term('add', (1, 2, 3)) == ('add', 1, 2, 3)


class Op(object):
    def __init__(self, name):
        self.name = name

@unifiable_with_term
class MyTerm(object):
    def __init__(self, op, arguments):
        self.op = op
        self.arguments = arguments
    def __eq__(self, other):
        return self.op == other.op and self.arguments == other.arguments

@dispatch(MyTerm)
def arguments(t):
    return t.arguments

@dispatch(MyTerm)
def operator(t):
    return t.op

@dispatch(Op, (list, tuple))
def term(op, args):
    return MyTerm(op, args)

def test_unifiable_with_term():
    add = Op('add')
    t = MyTerm(add, (1, 2))
    assert arguments(t) == (1, 2)
    assert operator(t) == add
    assert term(operator(t), arguments(t)) == t

    x = var('x')
    assert unify(MyTerm(add, (1, x)), MyTerm(add, (1, 2)), {}) == {x: 2}

