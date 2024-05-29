from fastapi import APIRouter, HTTPException
from starlette.responses import PlainTextResponse
from models.board import Board
from services.domino_service import generate_board, generate_dominos, find_max_pips, solve_puzzle
from utils.printer import print_board_with_solution, print_dominos

router = APIRouter()


@router.get("/generate_board/", summary="Generate a Domino Board")
async def generate_board_route(rows: int, cols: int):
    """
    Generates a domino board of a given size.

    - **rows**: The number of rows in the board.
    - **cols**: The number of columns in the board.

    The board size must be even (rows * cols).
    """
    if rows * cols % 2 != 0:
        raise HTTPException(status_code=400, detail="Board size must be even.")
    board = generate_board(rows, cols)
    return {"board": board}


@router.post("/solve/", response_class=PlainTextResponse,
          responses={200: {"description": "A solution for the provided domino board"},
                     400: {"description": "Invalid board size"}})
async def solve_route(board: Board):
    """
    Solves the domino puzzle for the given board configuration.

    - **board**: The board configuration to solve.
    """
    dominos = generate_dominos(find_max_pips(board.board))
    placement = [[None for _ in range(len(board.board[0]))] for _ in range(len(board.board))]
    solved = solve_puzzle(board.board, dominos, 0, 0, placement)

    solution_str = "Domino Board:\n"
    solution_str += print_board_with_solution(board.board, placement, False)
    solution_str += "\nDominos:\n"
    solution_str += print_dominos(dominos, find_max_pips(board.board))

    if solved:
        solution_str += "\nSolution:\n"
        solution_str += print_board_with_solution(board.board, placement, True)
    else:
        solution_str += "\nNo solution exists.\n"

    return PlainTextResponse(content=solution_str)
