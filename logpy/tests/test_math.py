from logpy.core import (var, eq, conde, run, membero, fail, success, Relation,
        fact, facts)
from logpy.math import primo, isprime

def test_primo():
    x = var()
    assert set(run(0, x, membero(x, (1,2,3,4,5,6,7,8,9,10,11)),
                           (primo, x))) == set((2, 3, 5, 7, 11))
    assert all(isprime(i) for i in run(5, x, primo(x)))
