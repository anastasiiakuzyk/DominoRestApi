from fastapi import APIRouter, HTTPException, Depends
from starlette.responses import PlainTextResponse
from models.board import Board
from services.database.database import get_board_by_id
from services.domino_service import generate_board, generate_dominos, generate_all_boards, find_max_pips, solve_puzzle, \
    solve_puzzle_parallel
from utils.printer import print_board_with_solution, print_dominos
from services.auth_service import get_current_user

router = APIRouter()


@router.get("/generate_board/", summary="Generate a Domino Board")
async def generate_board_route(rows: int, cols: int):
    """
    Generates a domino board of a given size and stores it in the database.

    - **rows**: The number of rows in the board.
    - **cols**: The number of columns in the board.

    The board size must be even (rows * cols).
    """
    if rows * cols % 2 != 0:
        raise HTTPException(status_code=400, detail="Board size must be even.")
    board, board_id = generate_board(rows, cols)
    return {"board": board, "board_id": board_id}


@router.post("/solve/", response_class=PlainTextResponse,
             responses={200: {"description": "A solution for the provided domino board"},
                        400: {"description": "Invalid board size"}})
async def solve_route(board: Board, user: str = Depends(get_current_user)):
    """
    Solves the domino puzzle for the given board configuration.

    - **board**: The board configuration to solve.
    """
    dominos = generate_dominos(find_max_pips(board.board))
    placement = [[None for _ in range(len(board.board[0]))] for _ in range(len(board.board))]
    solved = solve_puzzle_parallel(board.board, dominos, 0, 0, placement)

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


@router.get("/generate_all_boards/", summary="Generate All Unique Domino Boards")
async def generate_all_boards_route(rows: int, cols: int):
    """
    Generates all unique domino boards of a given size and stores them in the database.

    - **rows**: The number of rows in the board.
    - **cols**: The number of columns in the board.

    The board size must be even (rows * cols).
    """
    if rows * cols % 2 != 0:
        raise HTTPException(status_code=400, detail="Board size must be even.")
    board_ids = generate_all_boards(rows, cols)
    return {"board_ids": board_ids}


@router.get("/get_board_by_id/{board_id}", summary="Get Board by ID")
async def get_board_by_id_route(board_id: int):
    """
    Retrieves a board configuration from the database by its ID.

    - **board_id**: The ID of the board to retrieve.
    """
    board = get_board_by_id(board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found.")
    return {"board": board}
