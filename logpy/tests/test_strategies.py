from logpy.core import var, run, eq, membero, fail, conso
from logpy.strategies import bindearly, anyfail

x = var()
y = var()
z = var()

def test_fail():
    def failconstructor():
        return fail
    assert tuple(anyfail({}, ((eq, x, 1), (failconstructor,)))) == (fail,)
