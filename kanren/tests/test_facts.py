from __future__ import absolute_import

from unification import var

from ..core import run, conde
from ..facts import Relation, fact, facts


def test_relation():
    parent = Relation()
    fact(parent, "Homer", "Bart")
    fact(parent, "Homer", "Lisa")
    fact(parent, "Marge", "Bart")
    fact(parent, "Marge", "Lisa")
    fact(parent, "Abe", "Homer")
    fact(parent, "Jackie", "Marge")

    x = var('x')
    assert set(run(5, x, parent("Homer", x))) == set(("Bart", "Lisa"))
    assert set(run(5, x, parent(x, "Bart"))) == set(("Homer", "Marge"))

    def grandparent(x, z):
        y = var()
        return conde((parent(x, y), parent(y, z)))

    assert set(run(5, x, grandparent(x, "Bart"))) == set(("Abe", "Jackie"))

    foo = Relation('foo')
    assert 'foo' in str(foo)


def test_fact():
    rel = Relation()
    fact(rel, 1, 2)
    assert (1, 2) in rel.facts
    assert (10, 10) not in rel.facts

    facts(rel, (2, 3), (3, 4))
    assert (2, 3) in rel.facts
    assert (3, 4) in rel.facts


def test_unify_variable_with_itself_should_not_unify():
    # Regression test for https://github.com/logpy/logpy/issues/33
    valido = Relation()
    fact(valido, "a", "b")
    fact(valido, "b", "a")
    x = var()
    assert run(0, x, valido(x, x)) == ()


def test_unify_variable_with_itself_should_unify():
    valido = Relation()
    fact(valido, 0, 1)
    fact(valido, 1, 0)
    fact(valido, 1, 1)
    x = var()
    assert run(0, x, valido(x, x)) == (1, )


def test_unify_tuple():
    # Tests that adding facts can be unified with unpacked versions of those
    # facts.
    valido = Relation()
    fact(valido, (0, 1))
    fact(valido, (1, 0))
    fact(valido, (1, 1))
    x = var()
    y = var()
    assert set(run(0, x, valido((x, y)))) == set([0, 1])
    assert set(run(0, (x, y), valido((x, y)))) == set([(0, 1), (1, 0), (1, 1)])
    assert run(0, x, valido((x, x))) == (1, )
