import collections
import operator
from itertools import permutations, tee

from unification import isvar, var, reify, unify
from unification.utils import transitive_get as walk

from .core import (eq, EarlyGoalError, conde, condeseq, lany, lallgreedy, lall,
                   lanyseq, fail, success, goaleval)
from .util import unique, interleave, dicthash
from .cons import cons, car, cdr, is_null


def heado(head, coll):
    """ head is the head of coll

    See also:
        tailo
        conso
    """
    return (eq, cons(head, var()), coll)


def tailo(tail, coll):
    """ tail is the tail of coll

    See also:
        heado
        conso
    """
    return (eq, cons(var(), tail), coll)


def conso(h, t, l):
    """ cons h + t == l
    """
    return (eq, cons(h, t), l)


def nullo(l):
    """A relation asserting that a term is a "Lisp-like" null.

    For un-unified logic variables, it unifies with `None`.

    See `is_null`.
    """
    def _nullo(s):
        _s = reify(l, s)
        if isvar(_s):
            yield unify(_s, None, s)
        elif is_null(_s):
            yield s

    return _nullo


def itero(l):
    """A relation asserting that a term is an iterable type.

    This is a generic version of the standard `listo` that accounts for
    different iterable types supported by `cons` in Python.

    See `nullo`
    """
    c, d = var(), var()
    return (conde,
            [(nullo, l), success],
            [(conso, c, d, l),
             (itero, d)])


def permuteq(a, b, eq2=eq):
    """ Equality under permutation

    For example (1, 2, 2) equates to (2, 1, 2) under permutation
    >>> from kanren import var, run, permuteq
    >>> x = var()
    >>> run(0, x, permuteq(x, (1, 2)))
    ((1, 2), (2, 1))

    >>> run(0, x, permuteq((2, 1, x), (2, 1, 2)))
    (2,)
    """
    if isinstance(a, tuple) and isinstance(b, tuple):
        if len(a) != len(b):
            return fail
        elif collections.Counter(a) == collections.Counter(b):
            return success
        else:
            c, d = list(a), list(b)
            for x in list(c):
                # TODO: This is quadratic in the number items in the sequence.
                # Need something like a multiset. Maybe use
                # collections.Counter?
                try:
                    d.remove(x)
                    c.remove(x)
                except ValueError:
                    pass
            c, d = tuple(c), tuple(d)
            if len(c) == 1:
                return (eq2, c[0], d[0])
            return condeseq(
                ((eq2, x, d[0]), (permuteq, c[0:i] + c[i + 1:], d[1:], eq2))
                for i, x in enumerate(c)
            )

    if isvar(a) and isvar(b):
        raise EarlyGoalError()

    if isvar(a) or isvar(b):
        if isinstance(b, tuple):
            c, d = a, b
        elif isinstance(a, tuple):
            c, d = b, a

        return (condeseq, ([eq(c, perm)]
                           for perm in unique(permutations(d, len(d)))))


def seteq(a, b, eq2=eq):
    """ Set Equality

    For example (1, 2, 3) set equates to (2, 1, 3)

    >>> from kanren import var, run, seteq
    >>> x = var()
    >>> run(0, x, seteq(x, (1, 2)))
    ((1, 2), (2, 1))

    >>> run(0, x, seteq((2, 1, x), (3, 1, 2)))
    (3,)
    """
    ts = lambda x: tuple(set(x))
    if not isvar(a) and not isvar(b):
        return permuteq(ts(a), ts(b), eq2)
    elif not isvar(a):
        return permuteq(ts(a), b, eq2)
    else:  # not isvar(b)
        return permuteq(a, ts(b), eq2)


def goalify(func, name=None):
    """ Convert Python function into kanren goal

    >>> from kanren import run, goalify, var, membero
    >>> typo = goalify(type)
    >>> x = var('x')
    >>> run(0, x, membero(x, (1, 'cat', 'hat', 2)), (typo, x, str))
    ('cat', 'hat')

    Goals go both ways.  Here are all of the types in the collection

    >>> typ = var('typ')
    >>> results = run(0, typ, membero(x, (1, 'cat', 'hat', 2)), (typo, x, typ))
    >>> print([result.__name__ for result in results])
    ['int', 'str']
    """

    def funco(inputs, out):
        if isvar(inputs):
            raise EarlyGoalError()
        else:
            if isinstance(inputs, (tuple, list)):
                if any(map(isvar, inputs)):
                    raise EarlyGoalError()
                return (eq, func(*inputs), out)
            else:
                return (eq, func(inputs), out)

    name = name or (func.__name__ + 'o')
    funco.__name__ = name

    return funco


def membero(x, coll):
    """ Goal such that x is an item of coll """
    if not isvar(coll):
        return (lany, ) + tuple((eq, x, item) for item in coll)
    raise EarlyGoalError()


typo = goalify(type, name='typo')
isinstanceo = goalify(isinstance, name='isinstanceo')
not_equalo = goalify(operator.ne, name='not_equalo')


def appendo(l, s, ls, base_type=tuple):
    """
    Goal that ls = l + s.

    See Byrd thesis pg. 247
    https://scholarworks.iu.edu/dspace/bitstream/handle/2022/8777/Byrd_indiana_0093A_10344.pdf

    Parameters
    ==========
    base_type: type
        The empty collection type to use when all terms are logic variables.
    """
    if all(map(isvar, (l, s, ls))):
        raise EarlyGoalError()
    a, d, res = [var() for i in range(3)]
    return (lany, (lallgreedy, (eq, l, base_type()), (eq, s, ls)),
            (lall, (conso, a, d, l), (conso, a, res, ls),
             (appendo, d, s, res)))


def collect(s, f_lists=None):
    """A function that produces suggestions (for condp) based on the values of
    partially reified terms.

    This goal takes a list of suggestion function, variable pairs lists and
    evaluates them at their current, partially reified variable values
    (i.e. `f(walk(x, s))` for pair `(f, x)`).  Each evaluated function should
    return `None`, a string label in a corresponding condp clause, or the
    string "use-maybe".

    Each list of suggestion functions is evaluated in order, their output
    is concatenated, and, if the output contains a "use-maybe" string, the
    next list of suggestion functions is evaluated.

    Parameters
    ==========
    s: dict
        miniKanren state/replacements dictionary.
    f_lists: list or tuple (optional)
        A collection of function + variable pair collections (e.g.
        `[[(f0, x0), ...], ..., [(f, x), ...]]`).
    """
    if isinstance(f_lists, (tuple, list)):
        # TODO: Would be cool if this was lazily evaluated, no?
        # Seems like this whole thing would have to become a generator
        # function, though.
        ulos = ()
        # ((f0, x0), ...), ((f, x), ...)
        for f_list in f_lists:
            f, args = car(f_list), cdr(f_list)
            _ulos = f(*(walk(a, s) for a in args))
            ulos += _ulos
            if "use-maybe" not in _ulos:
                return ulos
        return ulos
    else:
        return ()


def condp(global_sugs, branches):
    """A goal generator that produces a conde-like relation driven by
    suggestions potentially derived from partial miniKanren state values.

    BOSKIN, BENJAMIN STRAHAN, WEIXI MA, DAVID THRANE CHRISTIANSEN, and DANIEL
    P. FRIEDMAN. n.d. “A Surprisingly Competitive Conditional Operator.”

    Parameters
    ==========
    global_sugs: `tuple`
        A tuple containing tuples of suggestion functions and their
        logic variable arguments.  Each suggestion function is evaluated
        using the reified versions of its corresponding logic variables (i.e.
        their "projected" values).  Each suggestion function is expected to
        return a tuple of branch labels corresponding to the keys in
        `branch_mappings`.
    branches: `Sequence` or `Mapping`
        Sequence or mapping of string labels--for each branch in a conde-like
        goal--to a tuple of goals pairs.
    """
    if isinstance(branches, collections.abc.Mapping):
        branches = branches.items()

    def _condp(s):
        global_los = collect(s, global_sugs)
        res = tuple((lall,) + g for k, g in branches
                    if k in global_los)

        yield from lanyseq(res)(s)

    return _condp


def collectseq(branch_s, f_lists=None):
    """A version of `collect` that takes a dict of branches-to-states.

    Parameters
    ==========
    branch_s: dict
        Branch labels to miniKanren state/replacements dictionaries.
    f_lists: list or tuple (optional)
        A collection of function + variable pair collections (e.g.
        `[[(f0, x0), ...], ..., [(f, x), ...]]`).
    """
    if isinstance(f_lists, (tuple, list)):
        ulos = ()
        for f_list in f_lists:
            f, args = f_list
            _ulos = f({k: reify(args, s)
                       for k, s in branch_s.items()})
            ulos += _ulos
            if "use-maybe" not in _ulos:
                return ulos
        return ulos
    else:
        return ()


def condpseq(branches):
    """An experimental version of `condp` that passes branch-state-reified
    maps to branch-specific suggestion functions.

    In other words, each branch-specific suggestion function is passed a `dict`
    with branch-label keys and the its function arguments reified against the
    state resulting from said branch.

    NOTE: Only previously evaluated branches will show up in these `dict`s, so
    branch order will determine the information available to each suggestion
    function.

    Parameters
    ==========
    branches: `OrderedDict`
        Ordered map or a sequence of tuples mapping string labels--for each
        branch in a conde-like goal--to a tuple starting with a single
        suggestion function followed by the branch goals.
    """
    if isinstance(branches, dict):
        branches = branches.items()

    def _condpseq(s, __bm=branches):
        __bm, local_items = tee(__bm)

        # Provide each branch-specific suggestion function a
        # copy of the state after the preceding branches goals have
        # been evaluated.
        def f(items):
            los = set()
            branch_s = {}
            for k, goals_branch_sugs in local_items:
                # Branch suggestions can be `None` and all branch
                # goals will be added.
                branch_sugs = car(goals_branch_sugs)
                goals = cdr(goals_branch_sugs)

                if branch_sugs:
                    # We only expect one suggestion function per-branch.
                    branch_sugs = (branch_sugs,)
                    los |= set(collectseq(branch_s or {k: s}, branch_sugs))

                if branch_sugs is None or k in los:
                    try:
                        a, b = tee(goaleval(lall(*goals))(s))
                        branch_s[k] = next(a)
                        yield b
                    except EarlyGoalError:
                        pass

                branch_s.setdefault(k, None)

        return unique(
            interleave(
                f(local_items),
                pass_exceptions=[EarlyGoalError]),
            key=dicthash)

    return _condpseq
