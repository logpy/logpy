"""
LogPy is a Python library for logic and relational programming.
"""

from core import run, eq, conde, membero
from variable import var, isvar, variables, Var
from goals import seteq, permuteq, goalify
from facts import Relation, fact, facts
from unification import unify, reify
from unifymore import logify

__version__ = '0.1.10'
