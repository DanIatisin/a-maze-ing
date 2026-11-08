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
the direction will be saved in a list to recreate all the path from start to end

### Braided Maze


## Features
- Random maze generation.
- Perfect and non-perfect maze modes.
- Seed support for reproducible generation.
- Maze visualization using MiniLibX.
- Shortest path calculation.
- Interactive controls.
- ...

## Instructions

### Requirements
List the required software and dependencies.

### Installation
Explain how to install the dependencies and set up the project.

### Usage
Explain how to execute the program.

### Configuration File
Explain the configuration file format.

Example:
```text
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=False
```
## Resources