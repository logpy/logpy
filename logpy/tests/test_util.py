from logpy.util import (isempty, take, unique, unique_dict, interleave,
        intersection, groups)
import itertools

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

def test_take():
    assert take(2, range(5)) == (0, 1)
    assert take(0, range(5)) == (0, 1, 2, 3, 4)
    assert take(None, range(5)) == range(5)

def test_isempty():
    assert isempty(())
    assert not isempty((1,2))
    it = (x for x in (1,2))
    a, it = itertools.tee(it, 2)
    assert not isempty(a)
    assert next(it) == 1

def test_interleave():
    assert ''.join(interleave(('ABC', '123'))) == 'A1B2C3'
    assert ''.join(interleave(('ABC', '1'))) == 'A1BC'

def test_groups():
    assert set(groups(4, 2)) == set(((1, 3), (2, 2), (3, 1)))
    assert set(groups(5, 2)) == set(((1, 4), (2, 3), (3, 2), (4, 1)))
    assert set(groups(4, 1)) == set([(4,)])
    assert set(groups(4, 4)) == set([(1, 1, 1, 1)])
