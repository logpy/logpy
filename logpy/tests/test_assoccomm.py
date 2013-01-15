from logpy.core import var
from logpy.assoccomm import unify_assoc

def test_assoc_comm():
    add = 'add'
    x = var()
    assert tuple(unify_assoc((add, 1,2,3), (add, 1,2,3), {}))
    assert tuple(unify_assoc((add, 1,2,3), (add, (add, 1, 2), 3), {}))
    assert tuple(unify_assoc((add, 1,2,3), (add, 1,x,3), {})) == ({x: 2},)
    assert tuple(unify_assoc((add, 1,2,3), (add, 1, x), {})) == ({x: (add, 2, 3)},)
    assert tuple(unify_assoc((add, 1,2,3), (add, x, 3), {})) == ({x: (add, 1, 2)},)
    assert tuple(unify_assoc((add, x, 3), (add, 1,2,3), {})) == ({x: (add, 1, 2)},)
