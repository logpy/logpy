LogPy
=====

Logic Programming in Python.  An variant of miniKanren.

Examples
--------

In LogPy we ask for the values which satisfy a set of relations.  In the
following we ask for a number x, such that `x == 1`
~~~~~~~~~~~Python
>>> from logpy import run, eq, membero, var
>>> x = var()
>>> run(1, x, eq(1, x))
(1,)
~~~~~~~~~~~

This uses
[Unification](http://en.wikipedia.org/wiki/Unification_%28computer_science%29) to
dive within expressions.  For example, for which x is the expression 
`(1, (2, 3)) == (1, (x, 3))` true?

~~~~~~~~~~~Python
>>> run(1, x, eq((1, (2, 3)), (1, (x, 3))))
(2,)
~~~~~~~~~~~

The above examples use `eq`, a *goal*.  We use goals to state relations we want
to be true.  Here we use `membero(item, coll)` which states that `item` is a
member of `coll`

~~~~~~~~~~~Python
>>> run(3, x, membero(x, (1, 2, 3)),  # x is a member of (1, 2, 3)
              membero(x, (2, 3, 4)))  # x is a member of (2, 3, 4)
(2, 3)

>>> run(1, x, membero(2, (2, x, 4)))  # What should x be to make this true?
(3,)
~~~~~~~~~~~

We can construct compound goals out of simple ones.  Here we use `conde` to ask
for up to three x's such that either `x == 1` or `x == 2`

~~~~~~~~~~~Python
>>> run(3, x, conde([eq(x, 1)], [eq(x, 2)]))
(1, 2)
~~~~~~~~~~~

LogPy supports relations and facts.  Here we create a parent relationship and
state some known facts about who is a parent of whom.

~~~~~~~~~~~Python
>>> from logpy import Relation, facts, conde
>>> parent = Relation()
>>> facts(parent, ("Homer", "Bart"),
                  ("Homer", "Lisa"),
                  ("Abe",  "Homer"))

>>> run(2, x, parent(x, "Bart"))
('Homer',)

>>> run(2, x, parent("Homer", x))
('Lisa', 'Bart')
~~~~~~~~~~~~

We can define compound goals from smaller ones.

~~~~~~~~~~~Python
>>> def grandparent(x, z):
...     y = var()
...     return conde((parent(x, y), parent(y, z)))

>>> run(2, x, grandparent(x, "Bart"))
('Abe,')
~~~~~~~~~~~

