from logpy.variable import isvar, var, vars, variables

def test_isvar():
    assert not isvar(3)
    assert isvar(var(3))

def test_var():
    assert var(1) == var(1)
    assert var() != var()

def test_var_inputs():
    assert var(1) == var(1)
    assert var() != var()

def test_vars():
    vs = vars(3)
    assert len(vs) == 3
    assert all(map(isvar, vs))

def test_context_manager():
    with variables(1):
        assert isvar(1)
    assert not isvar(1)
