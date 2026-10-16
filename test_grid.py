from typing import Any
import typing
from mazegen.generator import make_grid, moves, opposites


def print_maze(maze: list[list[int]]) -> None:
    for row in maze:
        text: str = ""
        for cell in row:
            text = text + f"{cell:X}"
        print(text)


def make_grid(width: int, height: int) -> list[list[int]]:
    maze: list[list[int]] = []
    for _ in range(height):
        row: list[int] = []
        for _ in range(width):
            row.append(0xF)
        maze.append(row)
    return maze


def break_wall(maze: list[list[int]], 
                x: int, y: int, 
                direction: int) -> None:
    dx, dy = moves[direction]
    nx = x + dx
    ny = y + dy
    maze[y][x] &= ~direction
    maze[ny][nx] &= ~opposites[direction]

def main() -> None:
    maze: list[list[int]] = make_grid(3, 3)
    print_maze(maze)
    print()
    print_maze(maze)
    print()
    break_wall(maze, 0, 0, 4)
    print()
    break_wall(maze, 1, 1, 2)
    print_maze(maze)


if __name__ == "__main__":
    main()