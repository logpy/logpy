with open('examples/data/adjacent-states.txt') as f: # lines like 'CA,OR,NV,AZ'
    adjlist = [line.strip().split(',') for line in f
                                       if line and line[0].isalpha()]
with open('examples/data/coastal-states.txt') as f:
    coastal_states = f.read().strip().split(',')

from logpy import run, fact, eq, Relation, var

adjacent = Relation()
coastal  = Relation()

for L in adjlist:                   # ['CA', 'OR', 'NV', 'AZ']
    head, tail = L[0], L[1:]        # 'CA', ['OR', 'NV', 'AZ']
    for state in tail:
        fact(adjacent, head, state) # e.g. 'CA' is adjacent to 'OR'

for state in coastal_states:        # ['NY', 'NJ', 'CT', ...]
    fact(coastal, state)            # e.g. 'NY' is coastal

x = var()
y = var()

print run(0, x, adjacent('CA', 'NY')) # California adjacent to New York?
# ()

print run(0, x, adjacent('CA', x))    # states next to California
# ('OR', 'NV', 'AZ')

print run(0, x, adjacent('TX', x),    # coastal states next to Texas
                coastal(x))
# ('LA',)

print run(0, x, coastal(y),           # states that border a coastal state
                adjacent(x, y))
# ('VT', 'AL', 'WV', 'DE', 'WA', 'RI', 'AZ', 'GA', 'ID', 'CT', 'IN', 'TX', 'WI', 'NC', 'MA', 'TN', 'DC', 'PA', 'OR', 'VA', 'AR', 'SD', 'ME', 'SC', 'CA', 'NH', 'NY', 'NV', 'OH', 'MS', 'ND', 'NM', 'IA', 'FL', 'NJ', 'LA', 'OK')


