import sys
from typing import Any

from mazegen import MazeGenerator
from output import OutputError, output_writer
from parsing import ConfigError, parse_config


def make_maze(config: dict[str, Any]) -> MazeGenerator:
    """Genera un oggetto Maze usando la classe MazeGenerator.
    Può essere chiamato più volte durante la visualizzazione in MLX
    """
    maze = MazeGenerator(
        width=config["width"],
        height=config["height"],
        perfect=config["perfect"],
        seed=config.get("seed"),
        entry_pos=config["entry"],
        exit_pos=config["exit"],
    )
    maze.generate_maze()
    maze.find_path()
    output_writer(
            maze.maze, maze.entry_pos, maze.exit_pos,
            maze.path, config['output_file']
            )
    return maze


def main() -> None:
    """
    Controlla se ci sono esattamente 2 argomenti;
    Esegue il parsing;
    Genera il maze;
    Stampa il maze a schermo con MLX;
    Gestisce gli errori."""
    # Controlla se ci sono esattamente 2 argomenti
    if len(sys.argv) != 2:
        print("Usage: python a_maze_ing.py <config_file>")
        sys.exit(1)

    try:
        from render import DisplayError, MlxDisplay

        config: dict[str, Any] = parse_config(sys.argv[1])
        maze = make_maze(config)

        def regenerate() -> MazeGenerator:
            """Genera un nuovo maze con un seed random"""
            return make_maze({**config, "seed": None})

        MlxDisplay(maze, regenerate).run()
    except ConfigError as e:
        print(f"Config error: {e}")
        sys.exit(1)
    except OutputError as e:
        print(f"Output error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Value error: {e}")
        sys.exit(1)
    except DisplayError as e:
        print(f"Display error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except RuntimeError as e:
        print(f"\n Runtime Error: {e}")


if __name__ == "__main__":
    main()
