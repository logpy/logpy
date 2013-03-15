from logpy.facts import Relation, fact, facts
from logpy.core import var, run, conde, reify

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
    assert set(run(5, x, parent(x, "Bart")))  == set(("Homer", "Marge"))

    def grandparent(x, z):
        y = var()
        return conde((parent(x, y), parent(y, z)))

    assert set(run(5, x, grandparent(x, "Bart") )) == set(("Abe", "Jackie"))

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

