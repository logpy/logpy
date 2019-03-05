kanren
=====

[![](https://travis-ci.org/logpy/logpy.png)](https://travis-ci.org/logpy/logpy)

Logic Programming in Python

Examples
--------

kanren enables the expression of relations and the search for values which satisfy them.  The following code is the "Hello, world!" of logic programming.  It asks for `1` number, `x`, such that `x == 5`

~~~~~~~~~~~Python
>>> from kanren import run, eq, membero, var, conde
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

kanren uses [unification](http://en.wikipedia.org/wiki/Unification_%28computer_science%29), an advanced form of pattern matching, to match within expression trees.
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
~~~~~~~~~~~

### Logic Variables

As in the above examples, `z = var()` creates a logic variable. You may also, optionally, pass a token name for a variable to aid in debugging:

~~~~~~~~~~~Python
>>> z = var('test')
>>> z
~test
~~~~~~~~~~~

Lastly, you may also use `vars()` with an integer parameter to create multiple logic variables at once:

~~~~~~~~~~~Python
>>> a, b, c = vars(3)
>>> a
~_1
>>> b
~_2
>>> c
~_3
~~~~~~~~~~~

### Representing Knowledge

kanren stores data as facts that state relationships between terms.

The following code creates a parent relationship and uses it to state
facts about who is a parent of whom within the Simpsons family.

~~~~~~~~~~~Python
>>> from kanren import Relation, facts
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

Data Structures
---------------

kanren depends on functions, tuples, dicts, and generators.  There are almost no new data structures/classes in kanren so it should be simple to integrate into preexisting code.


Extending kanren to other Types
------------------------------

kanren uses [Multiple Dispatch](http://github.com/mrocklin/multipledispatch/) and the [unification library](https://github.com/mrocklin/unification) to support pattern matching on user defined types.  Also see [unification (wikipedia)](http://en.wikipedia.org/wiki/Unification_%28computer_science%29).
Types which can be unified can be used for logic programming. See the [project examples](https://github.com/mrocklin/unification#examples) for how to extend the collection of unifiable types to your use case.

Install
-------

With `pip` or `easy_install`

    pip install kanren

From source

    git clone git@github.com:logpy/logpy.git
    cd logpy
    python setup.py install

Run tests with tox

    tox

Dependencies
------------

``kanren`` supports 3.5+.
It is pure Python and requires no dependencies beyond the standard
library, [`toolz`](http://github.com/pytoolz/toolz/),
[`multipledispatch`](http://github.com/mrocklin/multipledispatch/), and
[`unification`](http://github.com/mrocklin/unification/).

It is, in short, a light weight dependency.

Author
------

[Matthew Rocklin](http://matthewrocklin.com)

License
-------

New BSD license. See LICENSE.txt

Motivation
----------

Logic programming is a general programming paradigm.  This implementation however came about specifically to serve as an algorithmic core for Computer Algebra Systems in Python and for the automated generation and optimization of numeric software.  Domain specific languages, code generation, and compilers have recently been a hot topic in the Scientific Python community.  kanren aims to be a low-level core for these projects.

References
----------

*   [Logic Programming on wikipedia](http://en.wikipedia.org/wiki/Logic_programming)
*   [miniKanren](http://minikanren.org/), a Scheme library for relational programming on which this library is based.  More information can be found in the
[thesis of William
Byrd](https://scholarworks.iu.edu/dspace/bitstream/handle/2022/8777/Byrd_indiana_0093A_10344.pdf).
*   [core.logic](https://github.com/clojure/core.logic) a popular implementation of miniKanren in Clojure.
