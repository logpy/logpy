LogPy
=====

Logic Programming in Python

Examples
--------

LogPy enables the expression of relations and the search for values which
satisfy them.  
The following code asks for a number, x, such that `x == 1`
~~~~~~~~~~~Python
>>> from logpy import run, eq, membero, var, conde
>>> x = var()
>>> run(1, x, eq(1, x))
(1,)
~~~~~~~~~~~

[Unification](http://en.wikipedia.org/wiki/Unification_%28computer_science%29)
enables the query of complex expressions.
The following code asks for a number, x, such that 
`(1, (2, 3)) == (1, (x, 3))` holds.

~~~~~~~~~~~Python
>>> run(1, x, eq((1, (2, 3)), (1, (x, 3))))
(2,)
~~~~~~~~~~~

The above examples use `eq`, a *goal* to state that two expressions are equal.  
Other goals exist such as `membero(item, coll)` which states that `item`
is a member of `coll`, a collection.  

The following example uses `membero` twice to ask for 2 values of x, 
such that x is a member of `(1, 2, 3)` and that x is a member of `(2, 3, 4)`.

~~~~~~~~~~~Python
>>> run(3, x, membero(x, (1, 2, 3)),  # x is a member of (1, 2, 3)
              membero(x, (2, 3, 4)))  # x is a member of (2, 3, 4)
(2, 3)

>>> run(1, x, membero(3, (2, x, 4)))  # What should x be so that 3 is in coll?
(3,)
~~~~~~~~~~~

Simple goals can be combined into complex ones using goal constructors like
`conde`, a constructor for logical *and* and *or*.

The following example uses `conde` and `eq` to ask for two numbers such that
`x == 1` *or* `x == 2`.

~~~~~~~~~~~Python
>>> run(2, x, conde([eq(x, 1)], [eq(x, 2)]))
(1, 2)
~~~~~~~~~~~

LogPy supports relations and facts.  This is best demonstrated by example. 

The following code creates a parent relationship and uses it to state 
facts about who is a parent of whom.

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

Note that x may be used in either position.  

Complex goals may be formed from simpler ones.  The following code uses
`parent` to define `grandparent`.  It demonstrates the programming of
relations.
~~~~~~~~~~~Python
>>> def grandparent(x, z):
...     y = var()
...     return conde((parent(x, y), parent(y, z)))

>>> run(2, x, grandparent(x, "Bart"))
('Abe,')
~~~~~~~~~~~

Install
-------

With `pip` or `easy_install`

    pip install logic

From source

    git clone git@github.com:logpy/logpy.git
    cd logpy

Author
------

[Matthew Rocklin](http://matthewrocklin.com)

License
-------

New BSD license. See LICENSE.txt

References
----------

[Logic Programming](http://en.wikipedia.org/wiki/Logic_programming) 
was first popularized through the 
[Prolog language](http://en.wikipedia.org/wiki/Prolog). 

This implementation closely follows the design of
[miniKanren](http://kanren.sourceforge.net/), a Scheme library for relational
programming.  More information can be found in the 
[thesis of William
Byrd](https://scholarworks.iu.edu/dspace/bitstream/handle/2022/8777/Byrd_indiana_0093A_10344.pdf).

miniKanren came to our attention through the
[core.logic](https://github.com/clojure/core.logic) Clojure library.
