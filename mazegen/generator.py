N: int = 1
E: int = 2
S: int = 4
W: int = 8


moves: dict[int, (int, int)] = {
            N:(0, -1), S:(0, 1),
            W:(-1, 0), E:(1, 0)
        }


opposites: dict[int, int] = {N:S, W:E, E:W, S:N}


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