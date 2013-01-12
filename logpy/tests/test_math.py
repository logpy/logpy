from logpy.core import (var, eq, conde, run, membero, fail, success, Relation,
        fact, facts)
from logpy.math import primo

def test_primo():
    x = var()
    assert tuple(run(0, x, membero(x, (1,2,3,4,5,6,7,8,9,10,11)),
                           (primo, x))) == (2, 3, 5, 7, 11)
