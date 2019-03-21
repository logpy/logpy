from functools import reduce
from itertools import chain
from operator import length_hint
from collections import OrderedDict
from collections.abc import Iterator

from multipledispatch import dispatch

from toolz import drop, last

from unification.core import unify, _unify, reify, _reify


def first(x):
    return next(iter(x), None)


def rest(x):
    return drop(1, x)


class ConsType(type):
    def __instancecheck__(self, o):
        return is_cons(o)


class ConsPair(metaclass=ConsType):
    """An object representing cons pairs.

    These objects, and the class constructor alias `cons`, serve as a sort of
    generalized delayed append operation for various collection types.  When
    used with the built-in Python collection types, `cons` behaves like the
    concatenate operator between the given types, if any.

    A Python `list` is returned when the cdr is a `list` or `None`; otherwise,
    a `ConsPair` is returned.

    The arguments to `ConsPair` can be a car & cdr pair, or a sequence of
    objects to be nested in `cons`es, e.g.

        ConsPair(car_1, car_2, car_3, cdr) ==
            ConsPair(car_1, ConsPair(car_2, ConsPair(car_3, cdr)))
    """
    __slots__ = ['car', 'cdr']

    def __new__(cls, *parts):
        if len(parts) > 2:
            res = reduce(lambda x, y: ConsPair(y, x), reversed(parts))
        elif len(parts) == 2:
            car_part = first(parts)
            cdr_part = last(parts)
            try:
                res = cons_merge(car_part, cdr_part)
            except NotImplementedError:
                instance = super(ConsPair, cls).__new__(cls)
                instance.car = car_part
                instance.cdr = cdr_part
                res = instance
        else:
            raise ValueError('Number of arguments must be greater than 2.')

        return res

    def __hash__(self):
        return hash([self.car, self.cdr])

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.car == other.car and
                self.cdr == other.cdr)

    def __repr__(self):
        return '{}({} {})'.format(self.__class__.__name__,
                                  repr(self.car),
                                  repr(self.cdr))

    def __str__(self):
        return '({} . {})'.format(self.car, self.cdr)


cons = ConsPair


@dispatch(object, type(None))
def cons_merge(car_part, cdr_part):
    """Merge a generic car and cdr.

    This is the base/`nil` case with `cdr` `None`; it produces a standard list.
    """
    return [car_part]


@dispatch(object, ConsPair)
def cons_merge(car_part, cdr_part):
    """Merge a car and a `ConsPair` cdr."""
    return ConsPair([car_part, car(cdr_part)], cdr(cdr_part))


@dispatch(object, Iterator)
def cons_merge(car_part, cdr_part):
    """Merge a car and an `Iterator` cdr."""
    return chain([car_part], cdr_part)


@dispatch(object, (list, tuple))
def cons_merge(car_part, cdr_part):
    """Merge a car with a list or tuple cdr."""
    return type(cdr_part)([car_part]) + cdr_part


@dispatch((list, tuple), OrderedDict)
def cons_merge(car_part, cdr_part):
    """Merge a list/tuple car with a dict cdr."""
    if hasattr(cdr_part, 'move_to_end'):
        cdr_part.update([car_part])
        cdr_part.move_to_end(first(car_part), last=False)
    else:
        cdr_part = OrderedDict([car_part] + list(cdr_part.items()))

    return cdr_part


@dispatch(type(None))
def car(z):
    return None


@dispatch(ConsPair)
def car(z):
    return z.car


@dispatch((list, tuple, Iterator))
def car(z):
    return first(z)


@dispatch(OrderedDict)
def car(z):
    return first(z.items())


@dispatch(type(None))
def cdr(z):
    return None


@dispatch(ConsPair)
def cdr(z):
    return z.cdr


@dispatch(Iterator)
def cdr(z):
    return rest(z)


@dispatch((list, tuple))
def cdr(z):
    return type(z)(list(rest(z)))


@dispatch(OrderedDict)
def cdr(z):
    return cdr(list(z.items()))


def is_cons(a):
    """Determine if an object is the result of a `cons`.

    This is automatically determined by the accepted `cdr` types for each
    `cons_merge` implementation, since any such implementation implies that
    `cons` can construct that type.
    """
    return (issubclass(type(a), ConsPair) or
            (any(isinstance(a, d)
                 for _, d in cons_merge.funcs.keys()
                 if d not in (object, ConsPair)) and
             length_hint(a, 0) > 0))


def is_null(a):
    """Check if an object is a "Lisp-like" null.

    A "Lisp-like" null object is one that can be used as a `cdr` to produce a
    non-`ConsPair` collection (e.g. `None`, `[]`, `()`, `OrderedDict`, etc.)

    It's important that this function be used when considering an arbitrary
    object as the terminating `cdr` for a given collection (e.g. when unifying
    `cons` objects); otherwise, fixed choices for the terminating `cdr`, such
    as `None` or `[]`, will severely limit the applicability of the
    decomposition.

    Also, for relevant collections with no concrete length information, `None`
    is returned, and it signifies the uncertainty of the negative assertion.
    """
    if a is None:
        return True
    elif any(isinstance(a, d)
             for d, in cdr.funcs.keys()
             if not issubclass(d, (ConsPair, type(None)))):
        lhint = length_hint(a, -1)
        if lhint == 0:
            return True
        elif lhint > 0:
            return False
        else:
            return None
    else:
        return False


# Unfortunately, `multipledispatch` doesn't use `isinstance` on the arguments,
# so it won't use our fancy setup for `isinstance(x, ConsPair)` and we have to
# specify--and check--each `cons`-amenable type explicitly.
def _cons_unify(lcons, rcons, s):

    if not is_cons(lcons) or not is_cons(rcons):
        # One of the arguments is necessarily a `ConsPair` object,
        # but the other could be an empty iterable, which isn't a
        # `cons`-derivable object.
        return False

    s = unify(car(lcons), car(rcons), s)
    if s is not False:
        return unify(cdr(lcons), cdr(rcons), s)
    return False


_unify.add((ConsPair, (ConsPair, list, tuple, Iterator, OrderedDict), dict),
           _cons_unify)
_unify.add(((list, tuple, Iterator, OrderedDict), ConsPair, dict),
           _cons_unify)


@_reify.register(ConsPair, dict)
def reify_cons(lcons, s):
    rcar = reify(car(lcons), s)
    rcdr = reify(cdr(lcons), s)
    return cons(rcar, rcdr)
