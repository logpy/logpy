from logpy.core import isvar, success, fail, assoc, goaleval
from sympy.ntheory.generate import prime, isprime
import itertools as it



def primo(x):
    return goaleval((_primo, x))
def _primo(x):
    if isvar(x):
        return lambda s: (assoc(s, x, p) for p in it.imap(prime, it.count(1)))
    else:
        return success if isprime(x) else fail
