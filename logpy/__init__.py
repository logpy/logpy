"""
LogPy is a Python library for logic and relational programming.
"""

from core import run, eq, conde, membero
from termpy.variable import var, isvar, variables, Var
from goals import seteq, permuteq, goalify
from facts import Relation, fact, facts
from termpy import unify, reify, termify

__version__ = '0.1.10'
