"""Maze generator and shortest-path solver.

the module provides the MazeGenerator class, which generates a
rectangular maze width a depth-first search (DFS) and finds the shortest
path from the entry to the exit with a breadth-first search (BFS).

Each cell is a 4-bit integer, one bit per direction: a bit set to 1
means a closed wall, a bit set to 0 means an open wall. The constants
N, E, S and W are the masks of the four bits. The wall between two
adjacent cells is stored in bots cells(E in one, W in the other) and
break_wall() keeps the two sides consistent.

If the maze has at least 9 columns and 7 rows, the "42" pattern is drawn
using fully closed cells.
"""

import random
from random import Random
from collections import deque

# I bit di ogni direzione
N: int = 1
E: int = 2
S: int = 4
W: int = 8

FOUR: list[str] = [
    "#..",
    "#..",
    "###",
    "..#",
    "..#"
]

TWO: list[str] = [
    "###",
    "..#",
    "###",
    "#..",
    "###"
]

# dizionario di tuple per sapere
# di quanto si sposta in base alla
# direzione
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

# Il numero massimo di celle utilizabile per la costruzione del maze
MAX_CELLS: int = 2000 * 2000


class MazeGenerator:
    """Generate a maze and find the shortest path to its exit.

    After creating the object, call generate_maze() and, if the path is
    needed, find_path().

    Example:
        >>> gen = MazeGenerator(15, 11, True, 42, (0, 0), (14, 10))
        >>> gen.generate_maze()
        >>> gen.find_path()
        >>> len(gen.maze), len(gen.maze[0])
        (11, 15)

    Attributes:
        width: Number of columns of the maze.
        height: Number of rows of the maze.
        perfect: True for a perfect maze (exactly one path between any two
            cells), False for a maze with loops.
        entry_pos: (x, y) coordinates of the entry cell.
        exit_pos: (x, y) coordinates of the exit cell.
        seed: Seed used by the random number generator.
        rng: Random number generator (random.Random) initialised with seed.
        maze: Grid of height rows by width columns, accessed as
            maze[y][x]. Empty until generate_maze() is called.
        path: List of moves ("N", "E", "S", "W") from the entry to the
            exit. Empty until find_path() is called.
        pattern_cords: Set of (x, y) coordinates of the cells forming the
            42 pattern. Empty if the maze is smaller than 9x7."""

    def __init__(self, width: int, height: int,
                 perfect: bool, seed: int | None,
                 entry_pos: tuple[int, int],
                 exit_pos: tuple[int, int]) -> None:
        """Create the generator and check that the parameters are valid.

        The maze is not generated here: call generate_maze() for that. If the
        maze is smaller than 9x7 the 42 pattern cannot be drawn and a warning
        is printed.

        Args:
            width: Number of columns (at least 1).
            height: Number of rows (at least 1).
            perfect: If True the maze is perfect, meaning there is exactly one
                possible path between any two cells. If False, after the
                generation some walls are opened to remove dead ends, which
                creates loops.
            seed: Seed of the random number generator. With the same
                parameters and the same seed the same maze is always
                generated. If None a random seed is chosen, readable
                afterwards from self.seed.
            entry_pos: (x, y) coordinates of the entry. x is the column
                (from 0 to width - 1) and y is the row (from 0 to height - 1).
            exit_pos: (x, y) coordinates of the exit, same format as
                entry_pos.

        Raises:
            ValueError: If width or height is lower than 1, if
                width * height exceeds MAX_CELLS, if entry_pos and exit_pos
                are the same, if either of them is outside the maze, or if
                either of them falls on a cell of the 42 pattern."""

        self.width = width
        self.height = height
        self.perfect = perfect
        self.entry_pos = entry_pos
        self.exit_pos = exit_pos
        self.maze: list[list[int]] = []
        self.path: list[str] = []
        self.pattern_cords: set[tuple[int, int]] = self.draw_num()
        if seed is None:
            self.seed = random.SystemRandom().randrange(2**32)
        else:
            self.seed = seed

        if (width < 1) or (height < 1):
            raise ValueError("Height and width can't be lower than 1")

        if (width * height) > MAX_CELLS:
            raise ValueError(f"Can't generate more than {MAX_CELLS} cells")

        if (entry_pos == exit_pos):
            raise ValueError("Entry and exit can't have the same coordinates")

        if not self.check_cell(entry_pos[0], entry_pos[1]):
            raise ValueError("Entry out of maze")

        if not self.check_cell(exit_pos[0], exit_pos[1]):
            raise ValueError("Exit out of maze")

        if (self.width < 9) or (self.height < 7):
            print("The pattern 42 will not be displayed")

        if ((entry_pos in self.pattern_cords) or
           (exit_pos in self.pattern_cords)):
            raise ValueError("Entry or exit can't be in the 42 pattern")

        self.rng: Random = random.Random(self.seed)

    def make_grid(self) -> None:
        """Create the initial grid with all the walls closed.

        Replace maze with a grid of height rows by width columns where
        every cell is 0xF (N, E, S and W walls closed). Any previous maze
        is discarded."""
        self.maze = []
        for _ in range(self.height):
            row: list[int] = []
            for _ in range(self.width):
                row.append(0xF)
            self.maze.append(row)

    # Funizone per spaccare i muri tra le celle
    def break_wall(self, x: int, y: int,
                   direction: int) -> None:
        """Open the wall between a cell and its neighbour.

        Clear the direction bit in cell(x, y) and the opposite bit in the
        nieghbouring cell, so the wall stays consistent on both sides.The
        bounds are not checked: the neighbouring cell must be inside the grid

        Args:
            x: Column of the cell.
            y: Row of the cell.
            direction: Direction of the wall to open(N, E, S or W)."""
        dx, dy = moves[direction]
        nx = x + dx
        ny = y + dy
        self.maze[y][x] &= ~direction
        self.maze[ny][nx] &= ~opposites[direction]

    # controllo se la cella é valida
    def check_cell(self, x: int, y: int) -> bool:
        """Check if the coordinates are inside the maze.

        Args:
            x: Column to check.
            y: row to check.

        Returns:
            True if 0 <= x < width and 0 <= y < height, otherwise False.The
            42 pattern is not taken into account."""
        return (0 <= y < self.height and 0 <= x < self.width)

    # Funzione per controllare i vicini per sapere dove si puo andare e dove no
    def check_nearby(self, x: int, y: int,
                     visited: set[tuple[int, int]]
                     ) -> list[tuple[int, int, int]]:
        """Generates a list of neighbour cells that have not been visited yet.

        A neighbour is valid only if is inside the maze and is not in visited.
        The walls are not looked at because this is used by DFS to see where
        to carve.The 42 cells are included in visited

        Args:
            x: Column of the cell
            y: Row of the cell
            visited: List of cells that has been visited, contains also
            the cells of 42 pattern.

        Returns:
            List of (nx, ny, direction) tuples, for each valid neighbour,
            where direction leads from (x, y) to (nx, ny). The list is empty
            if ther are no valid neighbours."""
        neighbors: list[tuple[int, int, int]] = []
        for direction in directions:
            dx, dy = moves[direction]
            nx = x + dx
            ny = y + dy
            if self.check_cell(nx, ny) and (nx, ny) not in visited:
                neighbors.append((nx, ny, direction))
        return neighbors

    # genera il maze con DFS
    def generate_maze(self) -> None:
        """Generate a new_maze with an iterative DFS.

        Creates the grid width make_grid(), then it starts carving a
        passage from entry_pos towards a random unvisited neighbour
        chosen with rng.When a cell has no more neighbours, backtrack.
        The cells of the 42 pattern are never visited and stay closed.

        The result is a perfect maze.If perfect is False, remove_dead_ends()
        is called at the end, which opens some walls and create loops.

        Overwrite maze and empty path: after a new_maze, find_path() must
        be called again.The random number generator is not re-initialised
        so repeated calls on the same istance give different maze, but
        always reproducible for a given seed."""
        self.make_grid()
        self.path = []
        visited: set[tuple[int, int]] = {self.entry_pos}
        stack: list[tuple[int, int]] = [self.entry_pos]
        visited = visited.union(self.pattern_cords)
        while stack:
            x, y = stack[-1]
            neighbors: list[tuple[int,
                            int, int]] = self.check_nearby(x, y, visited)
            if neighbors:
                nx, ny, direction = self.rng.choice(neighbors)
                self.break_wall(x, y, direction)
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()
        if not self.perfect:
            self.remove_dead_ends()

    # La BFS - algortimo per solvere il maze
    # Parent = {dove devo andare: da dove sono arrivato e la direzione}
    def find_path(self) -> None:
        """Find the shortest path from entry to the exit with a BFS.

        Store the result in path as a list of moves ("N", "E", "S", "W"),
        replacing the previous one.Call if after generate_maze(), and again
        every time a new maze is generated.

        Raises:
            RuntimeError: If generate_maze() has not been called yet, or if
                the exit cannot be reached from the entry.
            ValueError: If the path reconstruction fails.This should not
                happen: it would mean an internal inconsistency"""
        if self.maze == []:
            raise RuntimeError("generate_maze() needs to be called first")
        moves_done: list[str] = []
        queue: deque[tuple[int, int]] = deque([self.entry_pos])
        parent: dict[tuple[int, int],
                     tuple[int, int, int] | None] = {self.entry_pos: None}
        while queue:
            x, y = queue.popleft()
            if (x, y) == self.exit_pos:
                break
            for direction in directions:
                dx, dy = moves[direction]
                nx = x + dx
                ny = y + dy
                if (self.check_cell(nx, ny) and
                        (self.maze[y][x] & direction) == 0 and
                        (nx, ny) not in parent):
                    parent[(nx, ny)] = (x, y, direction)
                    queue.append((nx, ny))
        if self.exit_pos not in parent:
            raise RuntimeError("The exit is not accessible from the entry")
        current: tuple[int, int] = self.exit_pos
        while current != self.entry_pos:
            position: tuple[int, int, int] | None = parent[current]
            if position is None:
                raise ValueError("The path reconstruction failed, "
                                 f"at cell: {current}")
            px, py, step = position
            moves_done.append(direction_values[step])
            current = (px, py)
        moves_done.reverse()
        self.path = moves_done

    def draw_num(self) -> set[tuple[int, int]]:
        """Compute the cells that form the "42" pattern.

        The pattern is 7 cells wide and 5 cells tall: 3 columns for the "4",
        one empty column and 3 columns for the "2".It is centered in the maze
        and only appears if there are at least 9 columns and 7 rows.

        Returns:
            Set of (x, y) coordinates of the cells to leave completely closed.
            It is empty if maze is smaller than 9x7"""
        if (self.width < 9) or (self.height < 7):
            return set()
        start_col: int = (self.width - 7) // 2
        start_row: int = (self.height - 5) // 2
        draw: set[tuple[int, int]] = set()
        for row, symbol in enumerate(FOUR):
            for col, char in enumerate(symbol):
                if char == "#":
                    draw.add((start_col + col, start_row + row))
        for row, symbol in enumerate(TWO):
            for col, char in enumerate(symbol):
                if char == "#":
                    draw.add((start_col + 4 + col, start_row + row))
        return draw

    def find_dead_ends(self) -> list[tuple[int, int]]:
        """"Finds all the dead ends of the maze.

        A dead end is a cell with exactly one wall open.The cells of 42
        pattern are not dead ends.

        Returns:
            List of (x, y) coordinates, ordered by column from top to bottom
            and by row from left to right"""
        dead_ends: list[tuple[int, int]] = []
        for row, string in enumerate(self.maze):
            for cell, char in enumerate(string):
                count: int = 0
                for direction in directions:
                    if (char & direction) == 0:
                        count += 1
                if count == 1:
                    dead_ends.append((cell, row))
        return dead_ends

    def is_dead_end(self, x: int, y: int) -> bool:
        """Check whether a cell is a dead end

        Unlike find_dead_ends() thos looks at a single cell and reads
        the current state, so it is useful after other walls have
        been opened

        Args:
            x: Column of the cell.
            y: Row of the cell.

        Returns:
            True if the cell has exactly one open wall, otherwise False."""
        open_walls: int = 0
        for direction in directions:
            if (self.maze[y][x] & direction) == 0:
                open_walls += 1
        return open_walls == 1

    def breakable_walls(self, x: int, y: int) -> list[int]:
        """List the closd walls of a cell which is a dead end that can be
        opened.

        A wall is a candidate if it is closed and there is a cell inside the
        maze on the other side, so border walls are excluded. This does not
        check wheter the neighbouring cell is part of the 42 pattern, nor
        whether opening the wall creates an open 3x3 area (see check_zone()):
        the calles must do that.

        Args:
            x: Column of the cell.
            y: Row of the cell.

        Returns:
            List of the directions (N, E, S, W) of the walls that can be
            opened. It is empty if there is none."""
        candidates: list[int] = []
        for direction in directions:
            dx, dy = moves[direction]
            nx = x + dx
            ny = y + dy
            if (self.check_cell(nx, ny) and
                    (self.maze[y][x] & direction) != 0):
                candidates.append(direction)
        return candidates

    def check_zone(self, x: int, y: int, direction: int) -> bool:
        """Check that opening a wall does not create an open 3x3 area.

        An open 3x3 area is a block of 3x3 cells in which all 12 internal
        walls are open. This examines the 3x3 blocks that contain both cells
        on the sides of the wall: if in one of them that wall is the only one
        still closed, opening it would leave the whole block open.

        Call it before break_wall(), while the wall is still closed: if it is
        already open the result is meaningless. It is used by
        remove_dead_ends().

        Args:
            x: Column of the cell the wall starts from.
            y: Row of the cell the wall starts from.
            direction: Direction of the wall to open (N, E, S or W).

        Returns:
            True if opening the wall is safe, False if it would create an
            open 3x3 area."""
        closed_walls: int = 0
        candidate: bool = False
        bx_candidates: list[int] = []
        by_candidates: list[int] = []
        dx, dy = moves[direction]
        nx = x + dx
        ny = y + dy
        minx: int = min(x, nx)
        miny: int = min(y, ny)
        if (direction == E or direction == W):
            bx_candidates = [minx - 1, minx]
            by_candidates = [y - 2, y - 1, y]
        elif (direction == N or direction == S):
            bx_candidates = [x - 2, x - 1, x]
            by_candidates = [miny - 1, miny]
        for bx in bx_candidates:
            for by in by_candidates:
                if ((0 <= bx and bx + 2 < self.width) and
                        (0 <= by and by + 2 < self.height)):
                    closed_walls = 0
                    candidate = False
                    for row in range(by, by + 3):
                        for col in range(bx, bx + 3):
                            if (col != bx + 2):
                                if (self.maze[row][col] & E) != 0:
                                    closed_walls += 1
                            if (row != by + 2):
                                if (self.maze[row][col] & S) != 0:
                                    closed_walls += 1
                            if (direction == E or direction == W):
                                if (set([(x, y), (nx, ny)]) ==
                                        set([(col + 1, row), (col, row)])):
                                    candidate = True
                            if (direction == S or direction == N):
                                if (set([(x, y), (nx, ny)]) ==
                                        set([(col, row + 1), (col, row)])):
                                    candidate = True
                    if (closed_walls == 1) and candidate:
                        return False
        return True

    def remove_dead_ends(self) -> None:
        """Open walls to remove dead ends, creating loops.

        Make a single pass over the dead ends found by find_dead_ends() and
        open at most one wall for each, chosen with rng among those that:

        * do not lead into a cell of the 42 pattern;
        * do not create an open 3x3 area (see check_zone()).

        Among the valid walls, those leading to another dead end are
        preferred, because a single wall removes two dead ends.

        Some dead ends may remain after the call, if all their walls are
        excluded by the rules above.

        Call it only once the generation is over, not during the DFS: it could
        open walls towards cells not visited yet, and the DFS, which does not
        use check_zone(), could then complete an open 3x3 area. It is called
        by generate_maze() when perfect is False."""
        dead_ends: list[tuple[int, int]] = self.find_dead_ends()
        obstacle: int = 0
        for x, y in dead_ends:
            if self.is_dead_end(x, y):
                walls: list[int] = self.breakable_walls(x, y)
                if walls:
                    n_dead_end: list[int] = []
                    c_dead_end: list[int] = []
                    for wall in walls:
                        dx, dy = moves[wall]
                        nx = x + dx
                        ny = y + dy
                        if ((nx, ny) not in self.pattern_cords and
                           self.check_zone(x, y, wall)):
                            if self.is_dead_end(nx, ny):
                                n_dead_end.append(wall)
                            else:
                                c_dead_end.append(wall)
                    if n_dead_end:
                        obstacle = self.rng.choice(n_dead_end)
                        self.break_wall(x, y, obstacle)
                    elif c_dead_end:
                        obstacle = self.rng.choice(c_dead_end)
                        self.break_wall(x, y, obstacle)
