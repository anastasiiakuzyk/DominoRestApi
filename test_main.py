import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from main import app
from models.domino import Domino
from fastapi.security import HTTPAuthorizationCredentials

from services.auth_service import get_current_user
from services.database.database import get_board_by_id
from services.domino_service import generate_dominos, shuffle_dominos, generate_board, solve_puzzle, find_max_pips, \
    generate_all_boards
from utils.printer import print_board_with_solution, print_dominos
from unittest.mock import patch, MagicMock


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
async def test_register_and_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Register a user
        response = await ac.post("/auth/register", json={"username": "testuser", "password": "testpass"})
        assert response.status_code == 200
        assert response.json() == {"message": "User testuser registered successfully."}

        # Login with the registered user
        response = await ac.post("/auth/login", json={"username": "testuser", "password": "testpass"})
        assert response.status_code == 200
        token = response.json().get("token")
        assert token is not None

        return token


@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Register a user
        response = await ac.post("/auth/register", json={"username": "testuser", "password": "testpass"})
        assert response.status_code == 200
        assert response.json() == {"message": "User testuser registered successfully."}

        # Login with the registered user
        response = await ac.post("/auth/login", json={"username": "testuser", "password": "testpass"})
        assert response.status_code == 200
        token = response.json().get("token")
        assert token is not None

        return token


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
    board, board_id = generate_board(4, 4)
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
    board, _ = generate_board(2, 4)  # Generate a 2x4 board
    max_pips = max(max(row) for row in board)
    dominos = generate_dominos(max_pips)
    placement = [[None for _ in range(4)] for _ in range(2)]
    solved = solve_puzzle(board, dominos, 0, 0, placement)
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


def test_get_board_by_id_existing():
    board_id = 1
    expected_board = [[1, 2], [3, 4]]
    board_str = str(expected_board)

    with patch("services.database.database.open_database") as mock_open_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (board_str,)
        mock_open_db.return_value = mock_conn

        result = get_board_by_id(board_id)

        mock_open_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("SELECT BOARD FROM BOARD WHERE ID = ?;", (board_id,))
        mock_cursor.fetchone.assert_called_once()
        mock_conn.close.assert_called_once()

        assert result == expected_board


def test_get_board_by_id_non_existing():
    board_id = 999

    with patch("services.database.database.open_database") as mock_open_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_open_db.return_value = mock_conn

        result = get_board_by_id(board_id)

        mock_open_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("SELECT BOARD FROM BOARD WHERE ID = ?;", (board_id,))
        mock_cursor.fetchone.assert_called_once()
        mock_conn.close.assert_called_once()

        assert result is None


@pytest.mark.asyncio
async def test_create_dev_key_route_success():
    token = "valid_token"
    username = "test_user"
    dev_key = "new_dev_key"

    headers = {"Authorization": token}

    with patch("services.auth_service.authenticate", return_value=True) as mock_authenticate, \
            patch("services.auth_service.generate_dev_key", return_value=dev_key) as mock_generate_dev_key, \
            patch.dict("services.auth_service.active_tokens", {token: username}, clear=True), \
            patch.dict("services.auth_service.dev_keys", {}, clear=True):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/auth/create_dev_key", headers=headers)

        assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_dev_key_route_unauthorized():
    token = "invalid_token"

    headers = {"Authorization": token}

    with patch("services.auth_service.authenticate") as mock_authenticate, \
            patch.dict("services.auth_service.active_tokens", {}, clear=True), \
            patch.dict("services.auth_service.dev_keys", {}, clear=True):
        mock_authenticate.return_value = False

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("auth/create_dev_key", headers=headers)

        assert response.status_code == 401
        assert response.json() == {"detail": "Unauthorized: Invalid or missing token."}


def test_get_current_user_valid_token():
    token = "valid_token"
    username = "test_user"

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with patch.dict("services.auth_service.active_tokens", {token: username}, clear=True):
        result = get_current_user(credentials)
        assert result == username


def test_get_current_user_invalid_token():
    token = "invalid_token"

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with patch.dict("services.auth_service.active_tokens", {}, clear=True):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid or expired token"


@pytest.mark.asyncio
async def test_solve_route_unauthorized():
    token = "invalid_token"
    board_data = {"board": [[1, 2], [3, 4]]}
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/solve/", json=board_data, headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}


@pytest.mark.asyncio
async def test_generate_all_boards_invalid_size():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/generate_all_boards/", params={"rows": 3, "cols": 3})

    assert response.status_code == 400
    assert response.json() == {"detail": "Board size must be even."}


def test_generate_all_boards_success():
    rows, cols = 2, 2
    max_pips = max(rows, cols) - 1
    dominos = [MagicMock(side1=i, side2=j) for i in range(max_pips + 1) for j in range(i, max_pips + 1)]
    board_id = 1
    board_ids = [board_id]

    with patch("services.domino_service.generate_dominos", return_value=dominos), \
            patch("services.domino_service.place_dominos_on_board") as mock_place_dominos, \
            patch("services.domino_service.save_board_to_db", return_value=board_id) as mock_save_board_to_db:
        result = generate_all_boards(rows, cols)

        mock_place_dominos.assert_called()
        mock_save_board_to_db.assert_called()
        assert result == board_ids


def test_generate_all_boards_handles_index_error():
    rows, cols = 2, 2
    max_pips = max(rows, cols) - 1
    dominos = [MagicMock(side1=i, side2=j) for i in range(max_pips + 1) for j in range(i, max_pips + 1)]

    with patch("services.domino_service.generate_dominos", return_value=dominos), \
            patch("services.domino_service.place_dominos_on_board", side_effect=IndexError), \
            patch("services.domino_service.save_board_to_db") as mock_save_board_to_db:
        result = generate_all_boards(rows, cols)

        mock_save_board_to_db.assert_not_called()
        assert result == []


def test_generate_all_boards_no_duplicates():
    rows, cols = 2, 2
    max_pips = max(rows, cols) - 1
    dominos = [MagicMock(side1=i, side2=j) for i in range(max_pips + 1) for j in range(i, max_pips + 1)]
    board_id = 1
    board_ids = [board_id]

    with patch("services.domino_service.generate_dominos", return_value=dominos), \
            patch("services.domino_service.place_dominos_on_board") as mock_place_dominos, \
            patch("services.domino_service.save_board_to_db", return_value=board_id) as mock_save_board_to_db:
        unique_board_str = "[[-1, -1], [-1, -1]]"
        mock_place_dominos.side_effect = lambda board, dominos, index: board.__setitem__(0, [0, 0]) if board == eval(
            unique_board_str) else None

        result = generate_all_boards(rows, cols)

        mock_place_dominos.assert_called()
        mock_save_board_to_db.assert_called()
        assert result == board_ids

@pytest.mark.asyncio
async def test_generate_all_boards_invalid_size():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/generate_all_boards/", params={"rows": 3, "cols": 3})

    assert response.status_code == 400
    assert response.json() == {"detail": "Board size must be even."}
