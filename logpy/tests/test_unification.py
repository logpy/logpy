from logpy.unification import unify, reify, _unify, _reify
from logpy import var

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
    assert reify(e, s) == {1: 2, 3: {5: 4}}

def test_reify_list():
    x, y = var(), var()
    s = {x: 2, y: 4}
    e = [1, [x, 3], y]
    assert reify(e, s) == [1, [2, 3], 4]

def test_reify_complex():
    x, y = var(), var()
    s = {x: 2, y: 4}
    e = {1: [x], 3: (y, 5)}

    assert reify(e, s) == {1: [2], 3: (4, 5)}

def test_unify():
    assert unify(1, 1, {}) == {}
    assert unify(1, 2, {}) == False
    assert unify(var(1), 2, {}) == {var(1): 2}
    assert unify(2, var(1), {}) == {var(1): 2}

def test_unify_seq():
    assert unify((1, 2), (1, 2), {}) == {}
    assert unify([1, 2], [1, 2], {}) == {}
    assert unify((1, 2), (1, 2, 3), {}) == False
    assert unify((1, var(1)), (1, 2), {}) == {var(1): 2}
    assert unify((1, var(1)), (1, 2), {var(1): 3}) == False

def test_unify_dict():
    assert unify({1: 2}, {1: 2}, {}) == {}
    assert unify({1: 2}, {1: 3}, {}) == False
    assert unify({2: 2}, {1: 2}, {}) == False
    assert unify({1: var(5)}, {1: 2}, {}) == {var(5): 2}

def test_unify_complex():
    assert unify((1, {2: 3}), (1, {2: 3}), {}) == {}
    assert unify((1, {2: 3}), (1, {2: 4}), {}) == False
    assert unify((1, {2: var(5)}), (1, {2: 4}), {}) == {var(5): 4}

    assert unify({1: (2, 3)}, {1: (2, var(5))}, {}) == {var(5): 3}
    assert unify({1: [2, 3]}, {1: [2, var(5)]}, {}) == {var(5): 3}
