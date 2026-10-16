#I bit di ogni direzione
N: int = 1
E: int = 2
S: int = 4
W: int = 8

"""dizionario di tuple per sapere 
   di quanto si sposta in base alla 
   direzione"""
moves: dict[int, (int, int)] = {
            N:(0, -1), S:(0, 1),
            W:(-1, 0), E:(1, 0)
        }

#Dizionario per sapere l'opposto della direzione
opposites: dict[int, int] = {N:S, W:E, E:W, S:N}

#Una tupla che serve solo per ciclare per evitare le ripetizioni
# directions: tuple[int, int, int, int] = (N, E, S, W)

#Funzione per creare il quadrato del maze
def make_grid(width: int, height: int) -> list[list[int]]:
    maze: list[list[int]] = []
    for _ in range(height):
        row: list[int] = []
        for _ in range(width):
            row.append(0xF)
        maze.append(row)
    return maze

#Funizone per spaccare i muri tra le celle
def break_wall(maze: list[list[int]], 
                x: int, y: int, 
                direction: int) -> None:
    dx, dy = moves[direction]
    nx = x + dx
    ny = y + dy
    maze[y][x] &= ~direction
    maze[ny][nx] &= ~opposites[direction]

#controllo se la cella é valida
def check_cell(x: int, y: int, width: int, height: int) -> bool:
    if 0 <= y <= height:
        return True
    if 0 <= x <= width: 
        return True
    return False

#Funzione per controllare i vicini per sapere dove si puo andare e dove no
def check_nearby(cell: tuple[int, int]) -> list[int]:
    pass
