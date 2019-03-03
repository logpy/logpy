from functools import reduce

from itertools import chain

from collections import OrderedDict

try:
    from operator import length_hint
except ImportError:
    def length_hint(obj, default=0):
        """Return an estimate of the number of items in obj.
        From https://www.python.org/dev/peps/pep-0424/
        """
        try:
            return len(obj)
        except TypeError:
            try:
                get_hint = type(obj).__length_hint__
            except AttributeError:
                return default
            try:
                hint = get_hint(obj)
            except TypeError:
                return default
            if hint is NotImplemented:
                return default
            if not isinstance(hint, int):
                raise TypeError("Length hint must be an integer, not %r" %
                                type(hint))
            if hint < 0:
                raise ValueError("__length_hint__() should return >= 0")
            return hint

try:
    from collections.abc import Iterator
except ImportError:
    from collections import Iterator

from multipledispatch import dispatch

from toolz import drop, last

from six import add_metaclass

from unification.core import unify, _unify, reify, _reify


def first(x):
    return next(iter(x), None)


def rest(x):
    return drop(1, x)


class ConsType(type):
    def __instancecheck__(self, o):
        return is_cons(o)


@add_metaclass(ConsType)
class ConsPair(object):
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
    return (type(a) == ConsPair or
            (any(isinstance(a, d)
                 for _, d in cons_merge.funcs.keys()
                 if d not in (object, ConsPair)) and
             length_hint(a, 0) > 0))


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
