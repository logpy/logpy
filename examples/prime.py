""" Example using SymPy to construct a prime number goal """

from kanren.core import (isvar, success, fail, assoc, goaleval, var, run,
        membero, condeseq, eq)
from sympy.ntheory.generate import prime, isprime
import itertools as it

def primo(x):
    """ x is a prime number """
    if isvar(x):
        return condeseq([(eq, x, p)] for p in it.imap(prime, it.count(1)))
    else:
        return success if isprime(x) else fail

x = var()
print set(run(0, x, (membero, x, (20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30)),
                    (primo, x)))
# set([29, 33])

print run(5, x, primo(x))
# (2, 3, 5, 7, 11)
