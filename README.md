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
- Random maze generation.
- Perfect and non-perfect maze modes.
- Seed support for reproducible generation.
- Maze visualization using MiniLibX.
- Shortest path calculation.
- Interactive controls.

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
If you want to use only the generator first of all you need to create a wheel file.
In the project folder
```bash
make build
```
This command will create a .whl file.You need to install it in your project folder using
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

### Configuration File

The maze generator uses a configuration file (`config.txt`) to define the maze parameters.

Each line must contain a `KEY=VALUE` pair. Lines starting with `#` are treated as comments and ignored.

#### Available Parameters

| Parameter | Description | Example |
|---|---|---|
| WIDTH | Maze width (number of cells). | `WIDTH=20` |
| HEIGHT | Maze height (number of cells). | `HEIGHT=15` |
| ENTRY | Entry coordinates (x,y). | `ENTRY=0,0` |
| EXIT | Exit coordinates (x,y). | `EXIT=19,14` |
| OUTPUT_FILE | Name of the output file. | `OUTPUT_FILE=maze.txt` |
| PERFECT | Enables or disables perfect maze generation. | `PERFECT=True` |

#### Example Configuration

```text
# Maze dimensions
WIDTH=20
HEIGHT=15

# Entry and exit positions
ENTRY=0,0
EXIT=19,14

# Output file
OUTPUT_FILE=maze.txt

# Generation mode
PERFECT=True
```

## Resources
To understand DFS - https://www.codecademy.com/article/depth-first-search-dfs-algorithm

To understand BFS - https://www.codecademy.com/article/breadth-first-search-bfs-algorithm

## Artificial Intelligence
Was used in this project only to understand better the subject, debugging, testing and to understand various python concepts