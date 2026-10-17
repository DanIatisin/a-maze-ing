# import mazegen
import sys
from typing import Any
from pathlib import Path
from parsing import parse_config, ConfigError
from display import output_writer, OutputError
from test_grid import make_grid


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

    maze = make_grid(config['width'], config['height'])
    
    # Stampa il maze e la soluzione sul file output_file
    try:
        output_writer(maze, config['entry'], config['exit'], output_file)
    except OutputError as e:
        print(f"Output error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
