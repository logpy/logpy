from contextlib import contextmanager
from .util import hashable
from .dispatch import dispatch

_global_logic_variables = set()
_glv = _global_logic_variables

class Var(object):
    """ Logic Variable """

    _id = 1
    def __new__(cls, *token):
        if len(token) == 0:
            token = "_%s" % Var._id
            Var._id += 1
        elif len(token) == 1:
            token = token[0]

        obj = object.__new__(cls)
        obj.token = token
        return obj

    def __str__(self):
        return "~" + str(self.token)
    __repr__ = __str__

    def __eq__(self, other):
        return type(self) == type(other) and self.token == other.token

    def __hash__(self):
        return hash((type(self), self.token))

var = lambda *args: Var(*args)
vars = lambda n: [var() for i in range(n)]


@dispatch(Var)
def isvar(v):
    return True


@dispatch(object)
def isvar(o):
    return not not _glv and hashable(o) and o in _glv


@contextmanager
def variables(*variables):
    """ Context manager for logic variables

    >>> from __future__ import with_statement
    >>> from logpy import variables, var, isvar
    >>> with variables(1):
    ...     print(isvar(1))
    True

    >>> print(isvar(1))
    False

    Normal approach

    >>> from logpy import run, eq
    >>> x = var('x')
    >>> run(1, x, eq(x, 2))
    (2,)

    Context Manager approach
    >>> with variables('x'):
    ...     print(run(1, 'x', eq('x', 2)))
    (2,)
    """
    old_global_logic_variables = _global_logic_variables.copy()
    _global_logic_variables.update(set(variables))
    try:
        yield
    finally:
        _global_logic_variables.clear()
        _global_logic_variables.update(old_global_logic_variables)
