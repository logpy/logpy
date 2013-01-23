LogPy
=====

Logic Programming in Python

Examples
--------

LogPy enables the expression of relations and the search for values which satisfy them.  The following code is the "Hello, world!" of logic programming.  It asks for `1` number, `x`, such that `x == 5`

~~~~~~~~~~~Python
>>> from logpy import run, eq, membero, var, conde
>>> x = var()
>>> run(1, x, eq(x, 5))
(5,)
~~~~~~~~~~~

Multiple variables and multiple goals can be used simultaneously.  The
following code asks for a number x such that `x == z` and `z == 3`

~~~~~~~~~~~Python
>>> z = var()
>>> run(1, x, eq(x, z),
              eq(z, 3))
(3,)
~~~~~~~~~~~

LogPy uses [unification](http://en.wikipedia.org/wiki/Unification_%28computer_science%29), an advanced form of pattern matching, to match within expression trees.
The following code asks for a number, x, such that `(1, 2) == (1, x)` holds.

~~~~~~~~~~~Python
>>> run(1, x, eq((1, 2), (1, x)))
(2,)
~~~~~~~~~~~

The above examples use `eq`, a *goal constructor* to state that two expressions 
are equal.  Other goal constructors exist such as `membero(item, coll)` which 
states that `item` is a member of `coll`, a collection.  

The following example uses `membero` twice to ask for 2 values of x, 
such that x is a member of `(1, 2, 3)` and that x is a member of `(2, 3, 4)`.

~~~~~~~~~~~Python
>>> run(2, x, membero(x, (1, 2, 3)),  # x is a member of (1, 2, 3)
              membero(x, (2, 3, 4)))  # x is a member of (2, 3, 4)
(2, 3)
>>> run(4, x, membero(x, (1, 2, 3)), # asks for 4 values of x
              membero(x, (2, 3, 4))) # but only 2 values are members of both
(2, 3)       
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

We can use intermediate variables for more complex queries.  Who is Bart's grandfather?

~~~~~~~~~~~Python
>>> y = var()
>>> run(1, x, parent(x, y), 
              parent(y, 'Bart'))  
('Abe',)
~~~~~~~~~~~~

We can express the grandfather relationship separately.  In this example we use `conde`, a goal constructor for logical *and* and *or*. 

~~~~~~~~~~~Python
>>> def grandparent(x, z):
...     y = var()
...     return conde((parent(x, y), parent(y, z)))

>>> run(1, x, grandparent(x, 'Bart'))
('Abe,')
~~~~~~~~~~~~

Install
-------

With `pip` or `easy_install`

    pip install logic

From source

    git clone git@github.com:logpy/logpy.git
    cd logpy
    python setup.py install

Run tests with nose
    
    nosetests

LogPy is pure Python

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
