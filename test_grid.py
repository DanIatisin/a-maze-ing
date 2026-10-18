from typing import Any
import typing
from mazegen.generator import generate_maze, count_passages
from display import print_hex


def print_maze(maze: list[list[int]]) -> None:
    for row in maze:
        text: str = ""
        for cell in row:
            text = text + f"{cell:X}"
        print(text)


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
    # maze = generate_maze(10, 10, 1)
    a = generate_maze(5, 5, 1)
    print(count_passages(a))
    b = generate_maze(10, 10, 1)
    print(count_passages(b))
    # print(check_cell(1, 3, 3, 3))
    # print(check_nearby(0, 0, 3, 3, {}))
    # print(check_nearby(0, 0, 3, 3, {(1, 0)}))
    # print(check_nearby(1, 1, 3, 3, {}))
    #print(print_hex(maze))


if __name__ == "__main__":
    main()