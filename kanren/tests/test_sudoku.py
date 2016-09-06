"""
Based off
https://github.com/holtchesley/embedded-logic/blob/master/kanren/sudoku.ipynb
"""
from __future__ import absolute_import

from unification import var

from .. import run
from ..core import everyg
from ..goals import permuteq


DIGITS = tuple(range(1, 10))


def get_rows(board):
    return tuple(board[i:i + 9] for i in range(0, len(board), 9))


def get_columns(rows):
    return tuple(tuple(map(lambda x: x[i], rows)) for i in range(0, 9))


def get_square(rows, x, y):
    return tuple(
        rows[xi][yi] for xi in range(x, x + 3) for yi in range(y, y + 3))


def get_squares(rows):
    return tuple(
        get_square(rows, x, y) for x in range(0, 9, 3) for y in range(0, 9, 3))


def vars(hints):
    def helper(h):
        if h in DIGITS:
            return h
        else:
            return var()
    return tuple(helper(x) for x in hints)


def all_numbers(coll):
    return permuteq(coll, DIGITS)


def sudoku_solver(hints):
    variables = vars(hints)
    rows = get_rows(variables)
    cols = get_columns(rows)
    sqs = get_squares(rows)
    return run(
        1,
        variables,
        everyg(all_numbers, rows),
        everyg(all_numbers, cols),
        everyg(all_numbers, sqs)
    )


def test_missing_one_entry():
    example_board = (
        5, 3, 4, 6, 7, 8, 9, 1, 2,
        6, 7, 2, 1, 9, 5, 3, 4, 8,
        1, 9, 8, 3, 4, 2, 5, 6, 7,
        8, 5, 9, 7, 6, 1, 4, 2, 3,
        4, 2, 6, 8, 5, 3, 7, 9, 1,
        7, 1, 3, 9, 2, 4, 8, 5, 6,
        9, 6, 1, 5, 3, 7, 2, 8, 4,
        2, 8, 7, 4, 1, 9, 6, 3, 5,
        3, 4, 5, 2, 8, 6, 0, 7, 9
    )
    expected_solution = (
        5, 3, 4, 6, 7, 8, 9, 1, 2,
        6, 7, 2, 1, 9, 5, 3, 4, 8,
        1, 9, 8, 3, 4, 2, 5, 6, 7,
        8, 5, 9, 7, 6, 1, 4, 2, 3,
        4, 2, 6, 8, 5, 3, 7, 9, 1,
        7, 1, 3, 9, 2, 4, 8, 5, 6,
        9, 6, 1, 5, 3, 7, 2, 8, 4,
        2, 8, 7, 4, 1, 9, 6, 3, 5,
        3, 4, 5, 2, 8, 6, 1, 7, 9,
    )
    assert sudoku_solver(example_board)[0] == expected_solution


def test_missing_complex_board():
    example_board = (
        5, 3, 4, 6, 7, 8, 9, 0, 2,
        6, 7, 2, 0, 9, 5, 3, 4, 8,
        0, 9, 8, 3, 4, 2, 5, 6, 7,
        8, 5, 9, 7, 6, 0, 4, 2, 3,
        4, 2, 6, 8, 5, 3, 7, 9, 0,
        7, 0, 3, 9, 2, 4, 8, 5, 6,
        9, 6, 0, 5, 3, 7, 2, 8, 4,
        2, 8, 7, 4, 0, 9, 6, 3, 5,
        3, 4, 5, 2, 8, 6, 0, 7, 9,
    )
    expected_solution = (
        5, 3, 4, 6, 7, 8, 9, 1, 2,
        6, 7, 2, 1, 9, 5, 3, 4, 8,
        1, 9, 8, 3, 4, 2, 5, 6, 7,
        8, 5, 9, 7, 6, 1, 4, 2, 3,
        4, 2, 6, 8, 5, 3, 7, 9, 1,
        7, 1, 3, 9, 2, 4, 8, 5, 6,
        9, 6, 1, 5, 3, 7, 2, 8, 4,
        2, 8, 7, 4, 1, 9, 6, 3, 5,
        3, 4, 5, 2, 8, 6, 1, 7, 9,
    )
    assert sudoku_solver(example_board)[0] == expected_solution


def test_insolvable():
    example_board = (
        5, 3, 4, 6, 7, 8, 9, 1, 2,
        6, 7, 2, 1, 9, 5, 9, 4, 8,  # Note column 7 has two 9's.
        1, 9, 8, 3, 4, 2, 5, 6, 7,
        8, 5, 9, 7, 6, 1, 4, 2, 3,
        4, 2, 6, 8, 5, 3, 7, 9, 1,
        7, 1, 3, 9, 2, 4, 8, 5, 6,
        9, 6, 1, 5, 3, 7, 2, 8, 4,
        2, 8, 7, 4, 1, 9, 6, 3, 5,
        3, 4, 5, 2, 8, 6, 0, 7, 9
    )
    assert sudoku_solver(example_board) == ()


# @pytest.mark.skip(reason="Currently too slow!")
# def test_many_missing_elements():
#     example_board = (
#         5, 3, 0, 0, 7, 0, 0, 0, 0,
#         6, 0, 0, 1, 9, 5, 0, 0, 0,
#         0, 9, 8, 0, 0, 0, 0, 6, 0,
#         8, 0, 0, 0, 6, 0, 0, 0, 3,
#         4, 0, 0, 8, 0, 3, 0, 0, 1,
#         7, 0, 0, 0, 2, 0, 0, 0, 6,
#         0, 6, 0, 0, 0, 0, 2, 8, 0,
#         0, 0, 0, 4, 1, 9, 0, 0, 5,
#         0, 0, 0, 0, 8, 0, 0, 7, 9)
#     assert sudoku_solver(example_board)[0] == (
#         5, 3, 4, 6, 7, 8, 9, 1, 2,
#         6, 7, 2, 1, 9, 5, 3, 4, 8,
#         1, 9, 8, 3, 4, 2, 5, 6, 7,
#         8, 5, 9, 7, 6, 1, 4, 2, 3,
#         4, 2, 6, 8, 5, 3, 7, 9, 1,
#         7, 1, 3, 9, 2, 4, 8, 5, 6,
#         9, 6, 1, 5, 3, 7, 2, 8, 4,
#         2, 8, 7, 4, 1, 9, 6, 3, 5,
#         3, 4, 5, 2, 8, 6, 1, 7, 9)
#
#
# @pytest.mark.skip(reason="Currently too slow!")
# def test_websudoku_easy():
#     # A sudoku from websudoku.com.
#     example_board = (
#         0, 0, 8, 0, 0, 6, 0, 0, 0,
#         0, 0, 4, 3, 7, 9, 8, 0, 0,
#         5, 7, 0, 0, 1, 0, 3, 2, 0,
#         0, 5, 2, 0, 0, 7, 0, 0, 0,
#         0, 6, 0, 5, 9, 8, 0, 4, 0,
#         0, 0, 0, 4, 0, 0, 5, 7, 0,
#         0, 2, 1, 0, 4, 0, 0, 9, 8,
#         0, 0, 9, 6, 2, 3, 1, 0, 0,
#         0, 0, 0, 9, 0, 0, 7, 0, 0,
#     )
#     assert sudoku_solver(example_board) == (
#         9, 3, 8, 2, 5, 6, 4, 1, 7,
#         2, 1, 4, 3, 7, 9, 8, 6, 5,
#         5, 7, 6, 8, 1, 4, 3, 2, 9,
#         4, 5, 2, 1, 3, 7, 9, 8, 6,
#         1, 6, 7, 5, 9, 8, 2, 4, 3,
#         8, 9, 3, 4, 6, 2, 5, 7, 1,
#         3, 2, 1, 7, 4, 5, 6, 9, 8,
#         7, 8, 9, 6, 2, 3, 1, 5, 4,
#         6, 4, 5, 9, 8, 1, 7, 3, 2)
