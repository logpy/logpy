"""
An example showing how to use facts and relations to store data and query data

This example builds a small database of the US states.

The `adjacency` relation expresses which states border each other
The `coastal` relation expresses which states border the ocean
"""
from logpy import run, fact, eq, Relation, var

adjacent = Relation()
coastal  = Relation()


coastal_states = 'WA,OR,CA,TX,LA,MI,AL,GA,FL,SC,NC,VI,MD,DW,NJ,NY,CT,RI,MA,MN,NH,AK,HI'.split(',')

for state in coastal_states:        # ['NY', 'NJ', 'CT', ...]
    fact(coastal, state)            # e.g. 'NY' is coastal


with open('examples/data/adjacent-states.txt') as f: # lines like 'CA,OR,NV,AZ'
    adjlist = [line.strip().split(',') for line in f
                                       if line and line[0].isalpha()]

for L in adjlist:                   # ['CA', 'OR', 'NV', 'AZ']
    head, tail = L[0], L[1:]        # 'CA', ['OR', 'NV', 'AZ']
    for state in tail:
        fact(adjacent, head, state) # e.g. 'CA' is adjacent to 'OR',
                                    #      'CA' is adjacent to 'NV', etc...

x = var()
y = var()

print run(0, x, adjacent('CA', 'NY')) # is California adjacent to New York?
# ()

print run(0, x, adjacent('CA', x))    # all states next to California
# ('OR', 'NV', 'AZ')

print run(0, x, adjacent('TX', x),    # all coastal states next to Texas
                coastal(x))
# ('LA',)

print run(5, x, coastal(y),           # five states that border a coastal state
                adjacent(x, y))
# ('VT', 'AL', 'WV', 'DE', 'WA')


