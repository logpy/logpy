LogPy
=====

Logic Programming in Python

Examples
--------

In LogPy we ask for the values which satisfy a set of relations.  In the
following we ask for a number x, such that `x == 1`
~~~~~~~~~~~Python
>>> from logpy import run, eq, membero, var, conde
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

The above examples use `eq`, a *goal*.  We use goals to state relations that 
we want to be true.  Here we use `membero(item, coll)` which states that `item`
is a member of `coll`.  We use it twice and ask for all values x such that x is
a member of `(1, 2, 3)` and that x is a member of `(2, 3, 4)`.

~~~~~~~~~~~Python
>>> run(3, x, membero(x, (1, 2, 3)),  # x is a member of (1, 2, 3)
              membero(x, (2, 3, 4)))  # x is a member of (2, 3, 4)
(2, 3)

>>> run(1, x, membero(3, (2, x, 4)))  # What should x be so that 3 is in coll?
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
>>> from logpy import Relation, facts
>>> parent = Relation()
>>> facts(parent, ("Homer", "Bart"),
...               ("Homer", "Lisa"),
...               ("Abe",  "Homer"))

>>> run(1, x, parent(x, "Bart"))
('Homer',)

>>> run(2, x, parent("Homer", x))
('Lisa', 'Bart')
~~~~~~~~~~~~

Note that we can use the variable x in either position.  

We can define compound goals from smaller ones.

~~~~~~~~~~~Python
>>> def grandparent(x, z):
...     y = var()
...     return conde((parent(x, y), parent(y, z)))

>>> run(2, x, grandparent(x, "Bart"))
('Abe,')
~~~~~~~~~~~

Author
------

[Matthew Rocklin](http://matthewrocklin.com)

License
-------

New BSD license. See LICENSE.txt

References
----------

This closely follows the designs of
[miniKanren](http://kanren.sourceforge.net/), a Scheme library for relational
programming.  

More information can be found in the 
[thesis of William
Byrd](https://scholarworks.iu.edu/dspace/bitstream/handle/2022/8777/Byrd_indiana_0093A_10344.pdf).

miniKanren came to our attention through the
[core.logic](https://github.com/clojure/core.logic) Clojure library.
