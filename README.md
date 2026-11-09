*This project has been created as part of the 42 curriculum by diatisin, sabdalla.*

# A-Maze-ing

## Description
A-Maze-ing is a two person project at 42Roma that will teach you how to generate a maze,
how to recreate the path from the entry to the exit, how to create a braided maze and how
to visualiaze the maze in a window using MiniLibX (mlx)

### Maze Generator Algorithm
As a mazegenerator algorithm was used the DFS (Depth-First Search) which takes the root 
(entry position in maze) and will randomly select a direction, will break the wall 
creating a path towards the selected direction.It will go deep as it can, putting 
the coordinates of the cells it visited in a stack so it remembers them for furthure 
backtracking so it doesn't visit the same cell twice.

### Maze solver algorithm
As maze solver algorithm was used the BFS (Breadth-Firts search). It uses a queue
(First-In, First-Out) that track the visited nodes. First of all it will explore
the maze and will fill a dictionary with the coordinates of the cell where it needs 
to go(as KEY) and the cell where it came from alongside with the direction(as value).
Then it will check if the exit is present in the dictionary, if it is present then it
will look at it's value to see from wich cell it arrived and the direction it took therfore
the direction will be saved in a list to recreate all the path from the entry to the exit

### Braided Maze
If the flag Perfect in config.txt file is set to False a Braided maze will be created, with only 2 dead-ends
tolerated by the subject that are present in the 42 pattern.

## Features
- Random maze generation, reproducible with a seed.
- Perfect and non-perfect maze modes.
- Visible "42" pattern made of fully closed cells (omitted, with a message, if
  the maze is too small).
- Shortest path calculation (BFS).
- Output file with hexadecimal wall encoding, entry, exit and solution.
- Maze visualization using MiniLibX, with:
  - cell size automatically adapted to the screen;
  - an on-screen panel with the list of commands, usable with the keyboard or
    by clicking the buttons;
  - show/hide of the shortest path;
  - cycling through several wall colours (the background changes with them);
  - cycling through several colours for the "42" pattern;
  - regeneration of a new maze, which also rewrites the output file.
- Clean exit with `ESC`, with the window close button and with `Ctrl+C`.
- Clear error messages instead of tracebacks (invalid config, file not found,
  impossible maze parameters, maze too large for the screen, ...).

## Instructions
### Requirements

Before running the project, make sure you have the following installed:

- **Python 3.10 or newer**
- **pip** – Python package installer.
- **MiniLibX (MLX)** – Required for graphical maze visualization.
- **Linux with X11** – Required graphical environment for MiniLibX.

Additional development dependencies:

- **flake8** – For code style checking.
- **mypy** – For static type checking.
- **build** – For building the reusable Python package.
- **venv** – Allows you to not change the behaviour of your own system python command

Note: if some are missing they will be added during the installation

### Installation
1. Clone the repository
```bash
git clone <repository_url>
cd /path/a-maze-ing
```
2. Install dependecies
```bash
make install
```
3. Activate the virtual environment
```bash
source venv/bin/activate
```
4. To compile the project
```bash
make run
```

### Usage

```text
make run
```

which is equivalent to:

```text
python3 a_maze_ing.py config.txt
```

To use another configuration file: `make run CONFIG=other.txt`.

Other Makefile rules:

| Rule | Description |
|---|---|
| `make install` | create the virtual environment and install the dependencies |
| `make run` | run the program with `config.txt` |
| `make debug` | run the program inside the Python debugger (`pdb`) |
| `make clean` | remove `__pycache__`, `.mypy_cache`, build artifacts |
| `make lint` | run `flake8` and `mypy` with the flags required by the subject |
| `make lint-strict` | run `flake8` and `mypy --strict` |
| `make build` | build the `mazegen` package and copy it to the repository root |

`make build` command will create a .whl file.You need to install it in your project folder using
```bash
pip install /path/to/mazegen-1.0.0-py3-none-any.whl
```
to use it you need to import it in your file and pass the attributes values when creating the object. Example:
```python
from mazegen import MazeGenerator

maze = MazeGenerator(
    width=15
    height=11
    perfect=False
    seed=42
    entry_pos=(0, 0)
    exit_pos=(14, 10)
)
```

### Controls

| Key | Click on | Action |
|---|---|---|
| `1` | Generate a new maze | generate a new maze (new random seed) and rewrite the output file |
| `2` | Hide/show shortest path | show or hide the shortest path (animated) |
| `3` | Change maze color | next colour for the walls |
| `4` | Change 42 color | next colour for the "42" pattern |
| `ESC` | Close | close the program |

The entry cell is drawn in green and the exit cell in red when the path is
shown.

### Configuration File

The configuration file contains one `KEY=VALUE` pair per line.

| Key | Mandatory | Description | Example |
|---|---|---|---|
| `WIDTH` | yes | maze width in cells, integer greater than 1 | `WIDTH=20` |
| `HEIGHT` | yes | maze height in cells, integer greater than 1 | `HEIGHT=15` |
| `ENTRY` | yes | entry coordinates `x,y` | `ENTRY=0,0` |
| `EXIT` | yes | exit coordinates `x,y` | `EXIT=19,14` |
| `OUTPUT_FILE` | yes | name of the output file | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | yes | `True` for a perfect maze, `False` otherwise | `PERFECT=False` |
| `SEED` | no | integer seed, for reproducible generation | `SEED=42` |

Rules checked by the parser:

- lines starting with `#` and empty lines are ignored;
- keys are not case-sensitive (`width` and `WIDTH` are the same key), and
  spaces around keys and values are ignored;
- a value may contain `=`, only the first `=` separates key and value;
- a line without `=`, an unknown key, a duplicated key or a missing mandatory
  key is an error, and the message reports the line number when relevant;
- `WIDTH` and `HEIGHT` must be integers greater than 1;
- `ENTRY` and `EXIT` must be two integers separated by a comma, must be
  different and must be inside the maze;
- `PERFECT` accepts `True` or `False` (in any capitalization);
- `SEED`, if present, must be an integer;
- `OUTPUT_FILE` cannot be empty and cannot be the configuration file itself.

Example:

```text
# Maze configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=False
SEED=42
```

If the file is invalid, the program prints a clear message on `stderr` and
exits with a non-zero code.

### Output file format

The maze is written with one hexadecimal digit per cell, one row of the maze
per line. Each digit encodes the closed walls with four bits:

| Bit | Direction | Value |
|---|---|---|
| 0 (LSB) | North | 1 |
| 1 | East | 2 |
| 2 | South | 4 |
| 3 | West | 8 |

A bit set to 1 means the wall is closed. For example `F` is a cell closed on
all sides (this is how the "42" pattern is drawn), and `A` is a cell closed on
the East and West sides.

After the grid there is an empty line, followed by three lines: the entry
coordinates, the exit coordinates and the shortest path as a string of
`N`, `E`, `S`, `W` letters. Every line ends with `\n`.

The file is overwritten every time a new maze is generated, so it always
matches the maze shown on screen.

## Project structure

```text
.
├── a_maze_ing.py        # main program
├── config.txt           # default configuration
├── parsing.py           # configuration file parser
├── output.py            # hexadecimal output file writer
├── render.py            # MLX display
├── mazegen/             # reusable maze generation module
│   ├── __init__.py
│   └── generator.py     # MazeGenerator class
├── mazegen-1.0.0-py3-none-any.whl   # built package
├── pyproject.toml
├── Makefile
├── LICENSE.md
└── README.md
```

How the pieces are connected:

- `parsing.py` reads the configuration file and returns the validated
  values. It raises `ConfigError` on any problem.
- `a_maze_ing.py` builds the maze with `MazeGenerator`, solves it, writes the
  output file, and passes the generator to the display together with a
  function that builds a new maze. All errors are caught in `main()` and shown
  as messages.
- `render.py` draws the maze it receives and calls the "new maze" function when asked.
- `mazegen` knows nothing about any of the other files, so it can be reused.

## Team and project management

### Roles

- **sabdalla**: configuration file parser, output file writer, main program
  (`a_maze_ing.py`), MLX display (`render.py`), Makefile, README.
- **diatisin**: maze generation (`mazegen`), packaging and license, README.

### Tools

- **Git**, with one branch per feature and a review before merging into `main`
- **Python 3.10+** and `venv`
- **flake8** and **mypy** for code quality, **Make** to automate the tasks
- **MiniLibX** (Python wheel provided with the project) for the display
- **VS Code**, on Ubuntu and on WSL
- **Claude** AI assistant

## Resources
To understand DFS - https://www.codecademy.com/article/depth-first-search-dfs-algorithm
To understand BFS - https://www.codecademy.com/article/breadth-first-search-bfs-algorithm
To install MLX - https://harm-smits.github.io/42docs/libs/minilibx/getting_started.html
To understand MLX - https://github.com/SaraFreitas-dev/MinilibX-42-Pyhton-Documentation/blob/main/guides/mlx-reference.md

## Artificial Intelligence
AI was used in this project only to understand better the subject, debugging, testing and to understand various python concepts. 
It was also use to help write the README.
