import sqlite3
from typing import List

DB_PATH = "test.db"


def open_database():
    connection = sqlite3.connect(DB_PATH)
    return connection


def create_table():
    connection = open_database()
    cursor = connection.cursor()
    create_sql = """
    CREATE TABLE IF NOT EXISTS BOARD(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        COLS INT NOT NULL,
        ROWS INT NOT NULL,
        BOARD TEXT NOT NULL
    );
    """
    cursor.execute(create_sql)
    connection.commit()
    connection.close()


def save_board_to_db(cols: int, rows: int, board: List[List[int]]) -> int:
    connection = open_database()
    cursor = connection.cursor()
    board_str = str(board)  # Convert the board to a string representation
    insert_sql = "INSERT INTO BOARD (COLS, ROWS, BOARD) VALUES (?, ?, ?);"
    cursor.execute(insert_sql, (cols, rows, board_str))
    connection.commit()
    last_id = cursor.lastrowid
    connection.close()
    return last_id


def get_board_by_id(board_id: int) -> List[List[int]]:
    connection = open_database()
    cursor = connection.cursor()
    select_sql = "SELECT BOARD FROM BOARD WHERE ID = ?;"
    cursor.execute(select_sql, (board_id,))
    result = cursor.fetchone()
    connection.close()
    if result:
        board_str = result[0]
        return eval(board_str)  # Convert the string representation back to a list of lists
    else:
        return None


# Initialize the database
create_table()
