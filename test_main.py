import pytest
from httpx import AsyncClient
from main import (app)
from models.domino import Domino
from services.domino_service import generate_dominos, shuffle_dominos, generate_board, solve_puzzle, find_max_pips
from utils.printer import print_board_with_solution, print_dominos


@pytest.mark.asyncio
async def test_generate_board_route_even():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/generate_board/", params={"rows": 4, "cols": 4})
    assert response.status_code == 200
    data = response.json()
    assert 'board' in data
    assert len(data['board']) == 4
    assert all(len(row) == 4 for row in data['board'])


@pytest.mark.asyncio
async def test_generate_board_route_odd():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/generate_board/", params={"rows": 3, "cols": 3})
    assert response.status_code == 400
    assert response.json() == {"detail": "Board size must be even."}


@pytest.mark.asyncio
async def test_solve_route_with_solution():
    test_board = {
        "board": [
            [1, 2],
            [3, 4]
        ]
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/solve/", json=test_board)
    assert response.status_code == 200
    assert "Solution:" in response.text


def test_generate_dominos():
    dominos = generate_dominos(6)
    assert len(dominos) == 28  # For a double-six set
    assert all(isinstance(domino, Domino) for domino in dominos)


def test_shuffle_dominos():
    dominos = generate_dominos(6)
    original_order = dominos.copy()
    shuffle_dominos(dominos)
    assert len(dominos) == 28
    assert dominos != original_order


def test_generate_board():
    board = generate_board(4, 4)
    assert len(board) == 4
    assert all(len(row) == 4 for row in board)
    assert all(all(cell != -1 for cell in row) for row in board)


def test_solve_puzzle_no_solution():
    board = [[0, 1], [2, 3]]
    dominos = generate_dominos(1)  # Intentionally insufficient dominos
    placement = [[None, None], [None, None]]
    solved = solve_puzzle(board, dominos, 0, 0, placement)
    assert not solved


def test_solve_puzzle_with_solution():
    board = generate_board(2, 4)  # Generate a 2x4 board
    max_pips = max(max(row) for row in board)
    dominos = generate_dominos(max_pips)
    placement = [[None for _ in range(4)] for _ in range(2)]
    solved = solve_puzzle(board, dominos)
    assert solved


def test_print_board_with_solution():
    board = [[1, 2], [3, 4]]
    placement = [[0, 0], [1, 1]]
    expected_output_with_solution = "+---+---+\n| 1   2 |\n+---+---+\n| 3   4 |\n+---+---+"
    expected_output_without_solution = "+---+---+\n| 1   2 |\n+   +   +\n| 3   4 |\n+---+---+"

    assert print_board_with_solution(board, placement, True) == expected_output_with_solution
    assert print_board_with_solution(board, placement, False) == expected_output_without_solution


def test_print_board_with_solution_no_divider():
    board = [[5, 5], [6, 6]]
    placement = [[0, 0], [1, 1]]
    expected_output = "+---+---+\n| 5   5 |\n+---+---+\n| 6   6 |\n+---+---+"

    assert print_board_with_solution(board, placement, True) == expected_output


def test_print_dominos():
    dominos = [Domino(0, 0), Domino(1, 1), Domino(0, 1), Domino(1, 2)]
    max_pips = 2
    expected_output = "[0|0] \n[1|1] [0|1] \n[1|2] \n"

    assert print_dominos(dominos, max_pips) == expected_output


def test_print_dominos_empty_list():
    dominos = []
    max_pips = 2
    expected_output = "\n\n\n"  # Expecting three lines of empty output

    assert print_dominos(dominos, max_pips) == expected_output


def test_find_max_pips_normal_board():
    board = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    assert find_max_pips(board) == 9, "Should return the maximum pip value on a normal board"
