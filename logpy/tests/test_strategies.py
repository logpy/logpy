from logpy.core import var, run, eq, membero, fail
from logpy.strategies import bindearly, anyfail

def test_early():
    x = var()
    y = var()
    assert run(0, x, (eq, y, (1, 2)), (membero, x, y), binder=bindearly)
    assert run(0, x, (membero, x, y), (eq, y, (1, 2)), binder=bindearly)

def test_fail():
    x = var()
    def failconstructor():
        return fail
    assert tuple(anyfail({}, ((eq, x, 1), (failconstructor,)))) == (fail,)
