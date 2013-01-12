# Family relationships from The Godfather
# Translated from the core.logic example found in
# "The Magical Island of Kanren – core.logic Intro Part 1"
# http://objectcommando.com/blog/2011/11/04/the-magical-island-of-kanren-core-logic-intro-part-1/

from logpy import Relation, facts, run, conde, var, eq

father = Relation()
mother = Relation()

facts(father, ('Vito', 'Michael'),
              ('Vito', 'Sonny'),
              ('Vito', 'Fredo'),
              ('Michael', 'Anthony'),
              ('Michael', 'Mary'),
              ('Sonny', 'Vicent'),
              ('Sonny', 'Francesca'),
              ('Sonny', 'Kathryn'),
              ('Sonny', 'Frank'),
              ('Sonny', 'Santino'))

facts(mother, ('Carmela', 'Michael'),
              ('Carmela', 'Sonny'),
              ('Carmela', 'Fredo'),
              ('Kay', 'Mary'),
              ('Kay', 'Anthony'),
              ('Sandra', 'Francesca'),
              ('Sandra', 'Kathryn'),
              ('Sandra', 'Frank'),
              ('Sandra', 'Santino'))

q = var()
# Vito is the father of who?
run(0, q, father('Vito', q))

# Who is the father of Michael?
run(0, q, father(q, 'Michael'))

def parent(p, child):
    return conde([father(p, child)], [mother(p, child)])

# Who is a parent of Michael
run(0, q, parent(q, 'Michael'))

def grandparent(gparent, child):
    p = var()
    return conde((parent(gparent, p), parent(p, child)))

# Who is a grandparent of Anthony
run(0, q, grandparent(q, 'Anthony'))

# Vito is a grandparent of whom?
run(0, q, grandparent('Vito', q))

def sibling(a, b):
    p = var()
    return conde((parent(p, a), parent(p, b)))

# All spouses
x, y, z = var(), var(), var()
run(0, (x, y), (father, x, z), (mother, y, z))
