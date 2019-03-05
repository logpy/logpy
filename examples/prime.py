""" Example using SymPy to construct a prime number goal """
import itertools as it

import pytest

from unification import isvar

from kanren import membero
from kanren.core import (success, fail, var, run,
                         condeseq, eq)
try:
    import sympy.ntheory.generate as sg
except ImportError:
    sg = None


def primo(x):
    """ x is a prime number """
    if isvar(x):
        return condeseq([(eq, x, p)] for p in map(sg.prime, it.count(1)))
    else:
        return success if sg.isprime(x) else fail


def test_primo():
    if not sg:
        pytest.skip("Test missing required library: sympy.ntheory.generate")

    x = var()
    res = (set(run(0, x, (membero, x, (20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                                       30)), (primo, x))))

    assert {23, 29} == res

    assert ((run(5, x, primo(x)))) == (2, 3, 5, 7, 11)
