from typing import Any
import typing


def print_maze(maze: list[list[int]]) -> None:
    


def generator(height: int, width: int) -> list[list[int]]:
    maze: list[list[int]] = []
    for _ in range(height):
        row: list[list[int]] = []
        for _ in range(width):
            row.append(0XF)
        maze.append(row)
    print_maze(maze)


def main() -> None:
    generator(5, 5)


if __name__ == "__main__":
    main()
    valore = 15
    print(f"{valore:X}")