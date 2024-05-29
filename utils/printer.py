from typing import List

from models.domino import Domino


def print_board_with_solution(board, placement, show_solution):
    rows = len(board)
    cols = len(board[0])  # Assuming all rows are of equal length

    output_lines = []

    # Top border
    top_border = '+'.join(['---'] * cols)
    output_lines.append(f"+{top_border}+")

    for i in range(rows):
        row_output = []
        for j in range(cols):
            # Handle placement visibility for solution
            if show_solution:
                divider = "| " if j == 0 or placement[i][j] != placement[i][j - 1] else "  "
            else:
                divider = "| " if j == 0 else "  "
            row_output.append(f"{divider}{board[i][j]} ")
        row_output.append("|")  # Right border
        output_lines.append(''.join(row_output))

        # Inter-row separator or bottom border
        bottom_border = []
        for j in range(cols):
            if i < rows - 1:
                # If not the last row
                separator = "+---" if show_solution and placement[i][j] != placement[i + 1][j] else "+   "
            else:
                # Last row, always draw bottom border
                separator = "+---"
            bottom_border.append(separator)
        output_lines.append(''.join(bottom_border) + "+")

    return '\n'.join(output_lines)


def print_dominos(dominos: List[Domino], max_pips: int) -> str:
    output = ""
    for i in range(max_pips + 1):
        for domino in dominos:
            if domino.side2 == i:
                output += "[{}|{}] ".format(domino.side1, domino.side2)
        output += "\n"
    return output
