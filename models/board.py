from typing import List

from pydantic import BaseModel


class Board(BaseModel):
    """
    A models representing a board for the domino puzzle.

    - **board**: A 2D list of integers representing the board configuration.
    """
    board: List[List[int]]
