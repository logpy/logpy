Differences with miniKanren
===========================

kanren is a Python library.  The Python language introduces some necessary deviations from the original design.  Other deviations have been followed by choice.  

Syntax
------

Basic kanren syntax is as follows

    >>> x = var()
    >>> run(1, x, (eq, x, 2))

The first argument is the maximum number of desired results.  Select `0` for all values and `None` to receive a lazy iterator.

The second argument is the result variable.  Because Python does not support macros this variable must be created beforehand on the previous line.  Similarly there is no `fresh`; additional variables must be created ahead of time.

    >>> x, y = var(), var()
    >>> run(1, x, (eq, x, y), (eq, y, 2))

Evaluation of goals -- `eq(x, 2)` vs `(eq, x, 2)`
-------------------------------------------------

Traditional Python code is written `f(x)`.  Traditional Scheme code is written `(f, x)`.  kanren uses both syntaxes but prefers `(f, x)` so that goals may be constructed at the last moment.  This allows the goals to be reified with as much information as possible.  Consider the following 

    >>> x, y = var(), var()
    >>> run(0, x, eq(y, (1, 2, 3)), membero(x, y)))

In this example `membero(x, y)` is unable to provide sensible results because, at the time it is run y is a variable.  However, if membero is called *after* `eq(y, (1, 2, 3))` then we know that `y == (1, 2, 3)`.  With this additional information `membero is more useful.  If we write this as follows

    >>> x, y = var(), var()
    >>> run(0, x, eq(y, (1, 2, 3)), (membero, x, y)))

then kanren is able to evaluate the `membero` goal after it learns that `y == (1, 2, 3)`. 

In short, `goal(arg, arg)` is conceptually equivalent to `(goal, arg, arg)` but the latter gives more control to kanren.

Strategies and goal ordering
----------------------------

Python does not naturally support the car/cdr or head/tail list concept.  As a result functions like `conso` or `appendo` are difficult to write generally because there is no way to match a head and tail variable to a list variable.  This is a substantial weakness.  

To overcome this weakness kanren detects failed goals and reorders them at goal construction time.  This is evident in the following example

    >>> x, y = var(), var()
    >>> run(0, x, (membero, x, y), (eq, y, (1, 2, 3)))

`(membero, x, y)` does not produce sensible results when both `x` and `y` are variables.  When this goal is evaluated it raises an `EarlyGoalError`.  The kanren logical all function (equivalent to `bind*`) is sensitive to this and reorders goals so that erring goals are run after non-erring goals.  The code is converted

    >>> run(0, x, (membero, x, y), (eq, y, (1, 2, 3)))  # original
    >>> run(0, x, (eq, y, (1, 2, 3)), (membero, x, y))  # optimized

`conde`
-------

`conde` is available and common in kanren; it is not however related to
any idiomatic Python concept.  We separate `conde` into two functions

*   `lall` - Logical All
*   `lany` - Logical Any

As a result the following are equivalent and the first expands to the second

    (conde, (a, b, c), 
            (d, e))

    (lany, (lall, a, b, c),
           (lall, d, e))

`lany` and `lall` were roughly `mplus` and `bind*` in miniKanren.  `lany`
interleaves results rather than chain them.  `lall` reorders goals as mentioned
above.  There is some development to make these behaviors programmable through
strategies.
