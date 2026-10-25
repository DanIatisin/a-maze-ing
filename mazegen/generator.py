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
    """
    Questa classe ha lo scopo di generare il labirinto
    in base agli parametri passati
    e di trovare il percorso piu corto verso l'exit
    """

    def __init__(self, width: int, height: int,
                 perfect: bool, seed: int | None,
                 entry_pos: tuple[int, int],
                 exit_pos: tuple[int, int]) -> None:
        """
        *Salva i parametri nell'ogetto
        *Decide il seed (o quello dato, oppure uno casuale) e crea
        il generatore casuale
        *Controlla che i valori siano validi e se no solleva ValueError

        ARGS:
            width - la larghezza del labirinto
            height - la lunghezza del labirinto
            perfect - puo assumere 2 valori:
                True: Un labirinto perfetto con un solo percorso verso la fine
                False: Un labirinto stile Pac-Man con ogni cella accessibile
                        da qualsiasi punto del labirinto
                Nota: Per il valore False non é stato ancora implementato
                il codice
            seed - una numero in base al quale verrá generato un labirinto
                    se seed é indicato - la stessa sequenza di maze per istanza
                    Se seed non é indiciato - ogni istanza ha
                    una sequenza diversa di maze
            entry_pos - le coordinate che indicano il punto di partenza
            exit_pos - le coordinate che indicano il punto da raggiungere
            Nota: entry_pos e exit_pos sono scritte sotto forma di una tuple:
                (x, y) dove x - é la colonna e va da 0 a width -1
                y é la riga e va da 0 a height -1

        Raises:
            ValueError - questo errore scatta solo nei seguenti casi:
                * width o height minori di uno, oppure se il loro prodotto
                superano il massimo di celle che si possono generare
                * Se entry_pos e exit_pos sono le stesse coordinate, oppure
                nel caso se sono fuori il labirinto
        """
        self.width = width
        self.height = height
        self.perfect = perfect
        self.entry_pos = entry_pos
        self.exit_pos = exit_pos
        self.maze: list[list[int]] = []
        self.path: list[str] = []
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

        self.pattern: set[tuple[int, int]] = self.draw_num()

        if not len(self.pattern) == 0:
            if (entry_pos in self.pattern) or (exit_pos in self.pattern):
                raise ValueError("Entry or exit can't be in the 42 pattern")

        self.rng: Random = random.Random(self.seed)

    def make_grid(self) -> None:
        """
        Questo metodo usando i attributi width e height
        della classe genera una griglia di dimensione fissa
        con valori F che sono celle con nessun muro aperto
        """
        self.maze = []
        for _ in range(self.height):
            row: list[int] = []
            for _ in range(self.width):
                row.append(0xF)
            self.maze.append(row)

    # Funizone per spaccare i muri tra le celle
    def break_wall(self, x: int, y: int,
                   direction: int) -> None:
        """
        Questo metodo prende l'attributo maze della classe e
        le coordinare x - width(colonne), y - height(righe)
        e una direzione. Ha lo scopo di
        calcolare la cella dove dovrebbe andare e
        distruggere il muro tra la cella attuale
        e quella calcolata
        """
        dx, dy = moves[direction]
        nx = x + dx
        ny = y + dy
        self.maze[y][x] &= ~direction
        self.maze[ny][nx] &= ~opposites[direction]

    # controllo se la cella é valida
    def check_cell(self, x: int, y: int) -> bool:
        """
        Questo metodo returna True se le coordinate passate
        sono all'interno del maze
        """
        return (0 <= y < self.height and 0 <= x < self.width)

    # Funzione per controllare i vicini per sapere dove si puo andare e dove no
    def check_nearby(self, x: int, y: int,
                     visited: set[tuple[int, int]]
                     ) -> list[tuple[int, int, int]]:
        """
        Questo metodo riceve come parametro due coordinate x e y
        e un set di tuple 'visited'.Ha lo scopo
        di verificare quale celle vicino alle coordinate sono accessibile
        e returna una lista di tuple con tutte le coordinate valide
        """
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
        """
        Questo metodo che usa gli attributi della classe
        (maze e path). Dentro sono richiamti i metodi make_grid()
        e break_wall() che andranno a modificare l'attributo maze
        della classe stessa cosi ottenendo un vero labirinto.
        come algorimto viene usato il DFS - Depth first search
        """
        self.make_grid()
        self.path = []
        visited: set[tuple[int, int]] = {(0, 0)}
        stack: list[tuple[int, int]] = [(0, 0)]
        visited = visited.union(self.draw_num())
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

    # La BFS - algortimo per solvere il maze
    # Parent = {dove devo andare: da dove sono arrivato}
    def find_path(self) -> None:
        """
        Questo metodo ricevi i attribuit della classe in
        particolare (path, maze, entry_pos, exit_pos), non restisuisce niente
        perche va a modificare diretamente l'attributo path della classe,
        cosi é possibile salvarsi il percorso. In caso di una generazione
        di un nuovo labirinto nella stessa istanza all'attributo path viene
        assegnata la nuova lista di mosse per ricreare il percorso
        dentro il nuovo maze.
        Dentro il metodo aviene un raise di 2 tipi Errori:
            1. RuntimeError - scatta quando il metodo find_path()
                viene chiamato pirima del metodo generate_maze()
                oppure se exit non é raggiungibile
            2. ValueError - scatta quando position che riceve una tuple
                dal parent che indica da dove sono arrivato e la direzione
                e la direzione in qui sono andato é None ovvero non si riesce
                ad arrivare al exit
        """
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
