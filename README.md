LogPy
=====

Logic Programming in Python.  An variant of miniKanren.

Example
-------

    >>> from logpy import run, eq, membero, var
    >>> x = var(x)
    >>> run(3, x, membero(1, 2, 3), 
                  membero(2, 3, 4))
    (2, 3)
