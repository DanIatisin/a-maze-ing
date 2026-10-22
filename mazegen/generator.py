import random
from random import Random
from collections import deque

# I bit di ogni direzione
N: int = 1
E: int = 2
S: int = 4
W: int = 8

"""dizionario di tuple per sapere
   di quanto si sposta in base alla
   direzione"""
moves: dict[int, tuple[int, int]] = {
            N: (0, -1), S: (0, 1),
            W: (-1, 0), E: (1, 0)
        }

# Dizionario per trasformare le direzioni da int in str
direction_values: dict[int, str] = {N: "N", E: "E", S: "S", W: "W"}

# Dizionario per sapere l'opposto della direzione
opposites: dict[int, int] = {N: S, W: E, E: W, S: N}

# Una tupla che serve solo per ciclare per evitare le ripetizioni
directions: tuple[int, int, int, int] = (N, E, S, W)


# x = width
# y = height
# Funzione per creare il quadrato del maze
def make_grid(width: int, height: int) -> list[list[int]]:
    maze: list[list[int]] = []
    for _ in range(height):
        row: list[int] = []
        for _ in range(width):
            row.append(0xF)
        maze.append(row)
    return maze


# Funizone per spaccare i muri tra le celle
def break_wall(maze: list[list[int]],
               x: int, y: int,
               direction: int) -> None:
    dx, dy = moves[direction]
    nx = x + dx
    ny = y + dy
    maze[y][x] &= ~direction
    maze[ny][nx] &= ~opposites[direction]


# controllo se la cella é valida
def check_cell(x: int, y: int, width: int, height: int) -> bool:
    return (0 <= y < height and 0 <= x < width)


# Funzione per controllare i vicini per sapere dove si puo andare e dove no
def check_nearby(x: int, y: int,
                 width: int,
                 height: int,
                 visited: set[tuple[int, int]]
                 ) -> list[tuple[int, int, int]]:
    neighbors: list[tuple[int, int, int]] = []
    for direction in directions:
        dx, dy = moves[direction]
        nx = x + dx
        ny = y + dy
        if check_cell(nx, ny, width, height) and (nx, ny) not in visited:
            neighbors.append((nx, ny, direction))
    return neighbors


# genera il maze con DFS
def generate_maze(width: int, height: int,
                  seed: int | None = None) -> list[list[int]]:
    rng: Random = random.Random(seed)
    maze: list[list[int]] = make_grid(width, height)
    visited: set[tuple[int, int]] = {(0, 0)}
    stack: list[tuple[int, int]] = [(0, 0)]
    while stack:
        x, y = stack[-1]
        neighbors: list[tuple[int,
                        int, int]] = check_nearby(x, y, width, height, visited)
        if neighbors:
            nx, ny, direction = rng.choice(neighbors)
            break_wall(maze, x, y, direction)
            visited.add((nx, ny))
            stack.append((nx, ny))
        else:
            stack.pop()
    return maze


# La BFS - algortimo per solvere il maze
# Parent = {dove devo andare: da dove sono arrivato}
def find_path(maze: list[list[int]],
              entry_pos: tuple[int, int],
              exit_pos: tuple[int, int]) -> list[str] | None:
    if entry_pos == exit_pos:
        raise ValueError("The entry and the exit can't "
                         "have the same coordinates")
    height: int = len(maze)
    width: int = len(maze[0])
    queue: deque[tuple[int, int]] = deque([entry_pos])
    parent: dict[tuple[int, int],
                 tuple[int, int, int] | None] = {entry_pos: None}
    while queue:
        x, y = queue.popleft()
        if (x, y) == exit_pos:
            break
        for direction in directions:
            dx, dy = moves[direction]
            nx = x + dx
            ny = y + dy
            if (check_cell(nx, ny, width, height) and
                    (maze[y][x] & direction) == 0 and
                    (nx, ny) not in parent):
                parent[(nx, ny)] = (x, y, direction)
                queue.append((nx, ny))
    if exit_pos not in parent:
        return None
    current: tuple[int, int] = exit_pos
    moves_done: list[str] = []
    while current != entry_pos:
        position: tuple[int, int, int] | None = parent[current]
        if position is None:
            raise ValueError("The path reconstruction failed, "
                             f"at cell: {current}")
        px, py, step = position
        moves_done.append(direction_values[step])
        current = (px, py)
    moves_done.reverse()
    return moves_done
