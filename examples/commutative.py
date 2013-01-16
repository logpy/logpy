from logpy import run, var, fact
from logpy.assoccomm import eq_assoccomm as eq
from logpy.assoccomm import commutative, associative

# Define some dummy Operationss
add = 'add'
mul = 'mul'
# Declare that these ops are commutative using the facts system
fact(commutative, mul)
fact(commutative, add)

# Define some wild variables
x, y = var('x'), var('y')

# Two expressions to match
pattern = (mul, (add, 1, x), y)                # (1 + x) * y
expr    = (mul, 2, (add, 3, 1))                # 2 * (3 + 1)
print run(0, (x,y), eq(pattern, expr))         # prints ((3, 2),) meaning
                                               #   x matches to 3
                                               #   y matches to 2
