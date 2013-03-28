from logpy.variables import isvar, var

def test_isvar():
    assert not isvar(3)
    assert isvar(var(3))

def test_var():
    assert var(1) == var(1)
    assert var() != var()

def test_var_inputs():
    assert var(1) == var(1)
    assert var() != var()

