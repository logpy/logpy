from logpy.core import var, run, eq, membero, fail, conso
from logpy.strategies import bindearly, anyfail

x = var()
y = var()
z = var()

def test_early():
    assert run(0, x, (eq, y, (1, 2)), (membero, x, y), bindfn=bindearly)
    assert run(0, x, (membero, x, y), (eq, y, (1, 2)), bindfn=bindearly)

def test_fail():
    def failconstructor():
        return fail
    assert tuple(anyfail({}, ((eq, x, 1), (failconstructor,)))) == (fail,)

def test_conso_early():
    assert (run(0, x, (conso, x, y, z), (eq, z, (1, 2, 3)), bindfn=bindearly)
            == (1,))
