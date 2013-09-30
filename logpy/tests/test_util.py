from logpy.util import take, groupsizes, dicthash, hashable, multihash, unique
import itertools

def test_hashable():
    assert hashable(2)
    assert hashable((2,3))
    assert not hashable({1: 2})
    assert not hashable((1, {2: 3}))

def test_unique_dict():
    assert tuple(unique(({1: 2}, {2: 3}), key=dicthash)) == ({1: 2}, {2: 3})
    assert tuple(unique(({1: 2}, {1: 2}), key=dicthash)) == ({1: 2},)

def test_unique_not_hashable():
    assert tuple(unique(([1], [1])))

def test_multihash():
    inputs = 2, (1, 2), [1, 2], {1: 2}, (1, [2]), slice(1, 2)
    assert all(isinstance(multihash(i), int) for i in inputs)

def test_take():
    assert take(2, range(5)) == (0, 1)
    assert take(0, range(5)) == (0, 1, 2, 3, 4)
    assert take(None, range(5)) == range(5)

def test_groupsizes():
    assert set(groupsizes(4, 2)) == set(((1, 3), (2, 2), (3, 1)))
    assert set(groupsizes(5, 2)) == set(((1, 4), (2, 3), (3, 2), (4, 1)))
    assert set(groupsizes(4, 1)) == set([(4,)])
    assert set(groupsizes(4, 4)) == set([(1, 1, 1, 1)])
