from itertools import permutations
from models.domino import Domino
from typing import List, Optional, Tuple
import random

from services.database.database import save_board_to_db


def generate_dominos(max_pips: int) -> List[Domino]:
    return [Domino(i, j) for i in range(max_pips + 1) for j in range(i, max_pips + 1)]


def shuffle_dominos(dominos: List[Domino]):
    random.shuffle(dominos)


def place_dominos_on_board(board: List[List[int]], dominos: List[Domino], domino_index: int) -> None:
    rows = len(board)
    cols = len(board[0])
    for i in range(rows):
        for j in range(0, cols, 2):
            if domino_index >= len(dominos):
                raise IndexError("Ran out of dominos to place on the board.")
            board[i][j] = dominos[domino_index].side1
            if j + 1 < cols:
                board[i][j + 1] = dominos[domino_index].side2
            domino_index += 1


def generate_board(rows: int, cols: int) -> Tuple[List[List[int]], int]:
    max_pips = max(rows, cols) - 1
    dominos = generate_dominos(max_pips)
    shuffle_dominos(dominos)
    board = [[-1 for _ in range(cols)] for _ in range(rows)]
    domino_index = 0
    place_dominos_on_board(board, dominos, domino_index)
    board_id = save_board_to_db(cols, rows, board)
    return board, board_id


def generate_all_boards(rows: int, cols: int) -> List[int]:
    max_pips = max(rows, cols) - 1
    dominos = generate_dominos(max_pips)
    unique_boards = set()
    board_ids = []

    for domino_permutation in permutations(dominos):
        try:
            board = [[-1 for _ in range(cols)] for _ in range(rows)]
            domino_index = 0
            place_dominos_on_board(board, list(domino_permutation), domino_index)
            board_str = str(board)
            if board_str not in unique_boards:
                unique_boards.add(board_str)
                board_id = save_board_to_db(cols, rows, board)
                board_ids.append(board_id)
        except IndexError:
            continue  # Skip this permutation if it raises an IndexError

    return board_ids


def find_max_pips(board: List[List[int]]) -> int:
    return max(max(row) for row in board if row)


def can_place(board: List[List[int]], placement: List[List[Optional[int]]], domino: Domino, x: int, y: int,
              horizontal: bool) -> bool:
    rows, cols = len(board), len(board[0])
    if horizontal:
        if y + 1 >= cols or placement[x][y] is not None or placement[x][y + 1] is not None:
            return False
        return (board[x][y], board[x][y + 1]) in [(domino.side1, domino.side2), (domino.side2, domino.side1)]
    else:
        if x + 1 >= rows or placement[x][y] is not None or placement[x + 1][y] is not None:
            return False
        return (board[x][y], board[x + 1][y]) in [(domino.side1, domino.side2), (domino.side2, domino.side1)]


def solve_puzzle(board: List[List[int]], dominos: List[Domino], x: int = 0, y: int = 0,
                 placement: Optional[List[List[Optional[int]]]] = None) -> bool:
    if placement is None:
        placement = [[None for _ in range(len(board[0]))] for _ in range(len(board))]
    if y >= len(board[0]):
        x, y = x + 1, 0
    if x >= len(board):
        return True
    if placement[x][y] is not None:
        return solve_puzzle(board, dominos, x, y + 1, placement)
    for domino in dominos:
        if not domino.used:
            if can_place(board, placement, domino, x, y, True):
                domino.used = True
                placement[x][y], placement[x][y + 1] = domino.side1, domino.side2
                if solve_puzzle(board, dominos, x, y + 2, placement):
                    return True
                placement[x][y], placement[x][y + 1] = None, None
                domino.used = False
            if can_place(board, placement, domino, x, y, False):
                domino.used = True
                placement[x][y], placement[x + 1][y] = domino.side1, domino.side2
                if solve_puzzle(board, dominos, x, y + 1, placement):
                    return True
                placement[x][y], placement[x + 1][y] = None, None
                domino.used = False
    return False
