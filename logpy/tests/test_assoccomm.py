from logpy.core import var
from logpy.assoccomm import assoc_unify

def test_assoc_eq():
    add = 'add'
    x = var()
    assert tuple(assoc_unify((add, 1,2,3), (add, 1,2,3), {}))
    assert tuple(assoc_unify((add, 1,2,3), (add, (add, 1, 2), 3), {}))
    assert tuple(assoc_unify((add, 1,2,3), (add, 1,x,3), {})) == ({x: 2},)
    assert tuple(assoc_unify((add, 1,2,3), (add, 1, x), {})) == ({x: (add, 2, 3)},)
    assert tuple(assoc_unify((add, 1,2,3), (add, x, 3), {})) == ({x: (add, 1, 2)},)
    assert tuple(assoc_unify((add, x, 3), (add, 1,2,3), {})) == ({x: (add, 1, 2)},)
