from logpy.util import (take, unique, interleave, intersection,
        groupsizes, raises, groupby, merge, dicthash, hashable, multihash)
import itertools

def test_hashable():
    assert hashable(2)
    assert hashable((2,3))
    assert not hashable({1: 2})
    assert not hashable((1, {2: 3}))

def test_unique():
    assert tuple(unique((1,2,3))) == (1,2,3)
    assert tuple(unique((1,2,1,3))) == (1,2,3)

def test_unique_dict():
    assert tuple(unique(({1: 2}, {2: 3}), key=dicthash)) == ({1: 2}, {2: 3})
    assert tuple(unique(({1: 2}, {1: 2}), key=dicthash)) == ({1: 2},)

def test_unique_not_hashable():
    assert tuple(unique(([1], [1])))

def test_multihash():
    inputs = 2, (1, 2), [1, 2], {1: 2}, (1, [2]), slice(1, 2)
    assert all(isinstance(multihash(i), int) for i in inputs)

def test_intersection():
    a,b,c = (1,2,3,4), (2,3,4,5), (3,4,5,6)

    assert tuple(intersection(a,b,c)) == (3,4)

def test_take():
    assert take(2, range(5)) == (0, 1)
    assert take(0, range(5)) == (0, 1, 2, 3, 4)
    assert take(None, range(5)) == range(5)

def test_interleave():
    assert ''.join(interleave(('ABC', '123'))) == 'A1B2C3'
    assert ''.join(interleave(('ABC', '1'))) == 'A1BC'

def test_groupsizes():
    assert set(groupsizes(4, 2)) == set(((1, 3), (2, 2), (3, 1)))
    assert set(groupsizes(5, 2)) == set(((1, 4), (2, 3), (3, 2), (4, 1)))
    assert set(groupsizes(4, 1)) == set([(4,)])
    assert set(groupsizes(4, 4)) == set([(1, 1, 1, 1)])

def test_raises():
    raises(ZeroDivisionError, lambda: 1/0)

def test_groupby():
    d = groupby(lambda x: x%2, range(10))
    assert set(d.keys()) == set((0, 1))
    assert set(d[0]) == set((0, 2, 4, 6, 8))
    assert set(d[1]) == set((1, 3, 5, 7, 9))

def test_merge():
    assert merge({1: 2}, {3: 4}, {5: 6}) == {1: 2, 3: 4, 5: 6}
