kanren's Types and Common Functions
----------------------------------

The design of kanren/miniKanren is simple.  It manipulates only a few types with only a few important functions.

### Terms

Terms can be

*   constants like `123` or `'cat'`
*   logical variables which we denote with a tilde like `~x`
*   tuples of terms like `(123, 'cat')` or `(~x, 1, (2, 3))`

In short, they are trees in which leaves may be either constants or variables.  Constants may be of any Python type.

### Unify

We *unify* two similar terms like `(1, 2)` and `(1, ~x)` to form a *substitution* `{~x: 2}`.  We say that `(1, 2)` and `(1, ~x)` unify under the substitution `{~x: 2}`.  Variables may assume the value of any term.

Unify is a function that takes two terms, `u` and `v`, and returns a substitution `s`.

Examples that unify

|       u           |       v           |        s          |
|:-----------------:|:-----------------:|:-----------------:|
| 123               | 123               | {}                |
| 'cat'             | 'cat'             | {}                |
| (1, 2)            | (1, 2)            | {}                |
| ~x                | 1                 | {~x: 1}           |
| 1                 | ~x                | {~x: 1}           |
| (1, ~x)           | (1, 2)            | {~x: 2}           |
| (1, 1)            | (~x, ~x)          | {~x: 1}           |
| (1, 2, ~x)        | (~y, 2, 3)        | {~x: 3, ~y: 1}    |

Examples that don't unify

|       u           |       v           |
|:-----------------:|:-----------------:|
| 123               | 'cat'             |
| (1, 2)            | 12                |
| (1, ~x)           | (2, 2)            |
| (1, 2)            | (~x, ~x)          |

Actually we lied, `unify` also takes a substitution as input.  This allows us to keep some history around.  For example

    >>> unify((1, 2), (1, x), {})  # normal case
    {~x: 2}
    >>> unify((1, 2), (1, x), {x: 2})  # x is already two. This is consitent
    {~x: 2}
    >>> unify((1, 2), (1, x), {x: 3})  # x is already three.  This conflicts
    False

### Reify

Reify is the opposite of unify.  `reify` transforms a term with logic variables like `(1, ~x)` and a substitution like `{~x: 2}` into a term without logic variables like `(1, 2)`.

    >>> reify((1, x), {x: 2})
    (1, 2)

### Goals and Goal Constructors

A *goal* is a function from one substitution to a stream of substitutions.

    goal :: substitution -> [substitutions]

We make goals with a *goal constructors*.  Goal constructors are the normal building block of a logical program.  Lets look at the goal constructor `membero` which states that the first input must be a member of the second input (a collection).

    goal = membero(x, (1, 2, 3)

We can feed this goal a substitution and it will give us a stream of substitutions.  Here we'll feed it the substitution with no information and it will tell us that either `x` can be `1` or `x` can be `2` or `x` can be `3`

    >>> for s in goal({}):
    ...     print s
    {~x: 1}
    {~x: 2}
    {~x: 3}

What if we already know that `x` is `2`?

    >>> for s in goal({x: 2}):
    ...     print s
    {~x: 2}

Remember *goals* are functions from one substitution to a stream of substitutions.  Users usually make goals with *goal constructors* like `eq`, or `membero`.

### Goal Combinators

After this point kanren is just a library to manage streams of substitutions.

For example if we know both that `membero(x, (1, 2, 3))` and `membero(x, (2, 3, 4))` then we could do something like the following:

    >>> g1 = membero(x, (1, 2, 3))
    >>> g2 = membero(x, (2, 3, 4))
    >>> for s in g1({}):
    ...     for ss in g2(s):
    ...         print ss
    {~x: 2}
    {~x: 3}

Logic programs can have many goals in complex hierarchies.  Writing explicit for loops would quickly become tedious.  Instead we provide functions that conglomerate goals logically.

    combinator :: [goals] -> goal

Two important logical goal combinators are logical all `lall` and logical any `lany`.

    >>> g = lall(g1, g2)
    >>> for s in g({}):
    ...     print s
    {~x: 2}
    {~x: 3}

    >>> g = lany(g1, g2)
    >>> for s in g({}):
    ...     print s
    {~x: 1}
    {~x: 2}
    {~x: 3}
    {~x: 4}


### Laziness

Goals produce a stream of substitutions.  This stream is computed lazily, returning values only as they are needed.  kanren depends on standard Python generators to maintain the necessary state and control flow.

    >>> stream = g({})
    >>> stream
    <generator object unique at 0x2e13690>
    >>> next(stream)
    {~x: 1}


### User interface

Traditionally programs are run with the `run` function

    >>> x = var('x')
    >>> run(0, x, membero(x, (1, 2, 3)), membero(x, (2, 3, 4)))
    (2, 3)

`run` has an implicit `lall` for the goals at the end of the call.  It `reifies` results when it returns so that the user never has to touch logic variables or substitutions.

### Conclusion

These are all the fundamental concepts that exist in kanren.  To summarize

*   Term: a constant, variable, or tree of terms
*   Substitution: a dictionary mapping variables to terms
*   Unify: A function to turn two terms into a substitution that makes them match
*   Goal: A function from a substitution to a stream of substitutions
*   Goal Constructor: A user-level function that defines a goal
