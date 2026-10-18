from typing import Any
import typing
from mazegen.generator import generate_maze, directions, moves, check_cell
from display import print_hex

N: int = 1
E: int = 2
S: int = 4
W: int = 8


def print_maze(maze: list[list[int]]) -> None:
    for row in maze:
        text: str = ""
        for cell in row:
            text = text + f"{cell:X}"
        print(text)


""" funzioni per controllare che il dfs ha creato un maze perfetto

def count_passages(maze: list[list[int]]) -> int:
    count: int = 0
    for row in maze:
        for cell in row:
            if (cell & E) == 0:
                count += 1
            if (cell & S) == 0:
                count += 1
    return count

# funzione per vedere se il maze é perfetto o no
def count_reachable(maze: list[list[int]]) -> int:
    height: int = len(maze)
    width: int = len(maze[0])
    visited: set[tuple[int, int]] = {(0, 0)}
    stack: list[tuple[int,int]] = [(0, 0)]
    while stack:
        x, y = stack.pop()
        for direction in directions:
            dx, dy = moves[direction]
            nx = x + dx
            ny= y + dy
            if (check_cell(nx, ny, width, height) and
                (maze[y][x] & direction) == 0 and
                (nx, ny)not in visited):
                visited.add((nx, ny))
                stack.append((nx, ny))
    return len(visited)
"""

# def make_grid(width: int, height: int) -> list[list[int]]:
#     maze: list[list[int]] = []
#     for _ in range(height):
#         row: list[int] = []
#         for _ in range(width):
#             row.append(0xF)
#         maze.append(row)
#     return maze
 

def main() -> None:
    # print_maze(maze)
    # print()
    # # print_maze(maze)
    # print()
    # break_wall(maze, 0, 0, 4)
    # print()
    # break_wall(maze, 1, 1, 2)
    # print_maze(maze)
    # print()
    # maze = generate_maze(10, 10, 2)
    a = generate_maze(5, 5, 1)
    print(count_passages(a))
    print(count_reachable(a))
    b = generate_maze(10, 10, 1)
    print(count_passages(b))
    print(count_reachable(b))
    # print(check_cell(1, 3, 3, 3))
    # print(check_nearby(0, 0, 3, 3, {}))
    # print(check_nearby(0, 0, 3, 3, {(1, 0)}))
    # print(check_nearby(1, 1, 3, 3, {}))
    #print(print_hex(maze))


if __name__ == "__main__":
    main()