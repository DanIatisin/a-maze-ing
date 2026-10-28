# import mazegen
import sys
from typing import Any
from pathlib import Path
from parsing import parse_config, ConfigError
from output import output_writer, OutputError
from mazegen import MazeGenerator, N, E, S, W
from render import render_mlx


def make_maze(config: dict[str, Any]) -> MazeGenerator:
    """Genera un oggetto Maze usando la classe MazeGenerator.
    Può essere chiamato più volte durante la visualizzazione in MLX"""
    maze = MazeGenerator(
        width=config["width"],
        height=config["height"],
        perfect=config["perfect"],
        seed=config["seed"],
        entry_pos=config["entry"],
        exit_pos=config["exit"],
    )
    maze.generate_maze()
    maze.find_path()
    return maze


def main() -> None:

    # Controlla se ci sono esattamente 2 argomenti
    if len(sys.argv) != 2:
        print("Usage: python a_maze_ing.py <config_file>")
        sys.exit(1)

    # Converte il file config.txt in un Dict con valori validi
    try:
        config: dict[str, Any] = parse_config(sys.argv[1])
        output_file: Path = Path(config['output_file'])
    except ConfigError as e:
        print(f"Config error: {e}")
        sys.exit(1)

    
    # Crea il maze, stampa il maze e la soluzione sul file output_file
    try:
        maze = make_maze(config)
        output_writer(maze.maze, maze.entry_pos, maze.exit_pos, maze.path, output_file)
        render_mlx(maze.maze, maze.entry_pos, maze.exit_pos, maze.path)
    except OutputError as e:
        print(f"Output error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Value error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
