from logpy.core import isvar, success, fail
from sympy.ntheory.generate import prime, isprime

def primo(x):
    if isvar(x):
        return it.imap(prime, it.count(1))
    else:
        return success if isprime(x) else fail
