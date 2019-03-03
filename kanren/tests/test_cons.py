from itertools import chain
from functools import reduce
from collections import Iterable, OrderedDict

from kanren.cons import cons, ConsPair, car, cdr, is_cons


def assert_all_equal(*tests):

    def _equal(x, y):
        assert x, y
        return y

    reduce(_equal, tests)


def test_cons():
    assert_all_equal(cons('a', None), cons('a', []), ['a'])
    assert cons('a', ()) == ('a',)
    assert cons('a', []) == ['a']
    assert cons(None, 'a').car is None
    assert cons(None, 'a').cdr == 'a'
    assert cons((), 'a') == ConsPair((), 'a')
    assert cons([], 'a') == ConsPair([], 'a')
    assert cons('a', None) == ['a']
    assert cons('a', ['b', 'c']) == ['a', 'b', 'c']
    assert cons('a', ('b', 'c')) == ('a', 'b', 'c')
    assert type(cons(('a', 1), {'b': 2})) == ConsPair
    assert cons(('a', 1), OrderedDict({'b': 2})) == OrderedDict([('a', 1),
                                                                 ('b', 2)])

    assert cons(['a', 'b'], 'c') == ConsPair(['a', 'b'], 'c')

    assert cons(('a', 'b'), 'c') == ConsPair(('a', 'b'), 'c')
    assert cons(['a', 'b'], ['c', 'd']) == [['a', 'b'], 'c', 'd']
    assert cons(('a', 'b'), ['c', 'd']) == [('a', 'b'), 'c', 'd']
    assert cons(['a', 'b'], ('c', 'd')) == (['a', 'b'], 'c', 'd')
    assert type(cons(1, iter([3, 4]))) == chain
    assert list(cons([1, 2], iter([3, 4]))) == [[1, 2], 3, 4]
    assert list(cons(1, iter([2, 3]))) == [1, 2, 3]
    assert cons('a', cons('b', 'c')) == cons(['a', 'b'], 'c')
    assert cons(cons('a', 'b'), cons('c', 'd')) == cons([cons('a', 'b'), 'c'],
                                                        'd')


def test_car_cdr():
    assert car(cons('a', 'b')) == 'a'
    z = car(cons(iter([]), 1))
    expected = iter([])
    assert type(z) == type(expected)
    assert list(z) == list(expected)

    z = cdr(cons(1, iter([])))
    expected = iter([])
    assert isinstance(z, Iterable)
    assert list(z) == list(expected)

    assert car(iter([1])) == 1
    assert list(cdr(iter([1]))) == []
    assert list(cons(car(iter([1])), cdr(iter([1])))) == [1]
    assert list(cdr(iter([1, 2, 3]))) == [2, 3]

    assert car(cons(['a', 'b'], 'a')) == ['a', 'b']
    assert car(cons(('a', 'b'), 'a')) == ('a', 'b')
    assert cdr(cons('a', 'b')) == 'b'
    assert cdr(cons('a', ())) == ()
    assert cdr(cons('a', [])) == []
    assert cdr(cons('a', ('b',))) == ('b',)
    assert cdr(cons('a', ['b'])) == ['b']
    assert car(OrderedDict([(1, 2), (3, 4)])) == (1, 2)
    assert cdr(OrderedDict([(1, 2), (3, 4)])) == [(3, 4)]
    assert cdr(OrderedDict({(1): 2})) == []


def test_is_cons():
    assert is_cons(cons(1, 'hi'))
    assert is_cons((1, 2))
    assert is_cons([1, 2])
    assert is_cons(OrderedDict({(1): 2}))
    assert is_cons(iter([1]))
    assert not is_cons({})
    assert not is_cons(set())
    assert not is_cons(set([1, 2]))
    assert not is_cons('hi')
    assert not is_cons('hi')
    assert not is_cons(1)
    assert not is_cons(iter([]))
    assert not is_cons(OrderedDict({}))
    assert not is_cons(())
    assert not is_cons([])
