LogPy
=====

Logic Programming in Python.  An variant of miniKanren.

Examples
--------

~~~~~~~~~~~Python
>>> from logpy import run, eq, membero, var
>>> x = var()
>>> run(1, x, eq(1, x))
(1,)
>>> run(1, x, eq((1, (2, 3)), (1, (x, 3))))
(2,)

>>> run(3, x, membero(x, (1, 2, 3)),  # x is a member of (1, 2, 3)
              membero(x, (2, 3, 4)))  # x is a member of (2, 3, 4)
(2, 3)

>>> from logpy import Relation, facts, conde
>>> parent = Relation()
>>> facts(parent, ("Homer", "Bart"),
                  ("Homer", "Lisa"),
                  ("Abe",  "Homer"))

>>> run(2, x, parent(x, "Bart"))
('Homer',)

>>> run(2, x, parent("Homer", x))
('Lisa', 'Bart')

>>> def grandparent(x, z):
...     y = var()
...     return conde((parent(x, y), parent(y, z)))

>>> run(2, x, grandparent(x, "Bart"))
('Abe,')
~~~~~~~~~~~
