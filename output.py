from pathlib import Path


class OutputError(Exception):
    """Gestisce gli errori di output"""


def print_hex(maze: list[list[int]]) -> str:
    """Converte il maze in una stringa di esadecimali"""
    lines: list[str] = []
    for row in maze:
        lines.append("".join(f"{cell:X}" for cell in row))
    return "\n".join(lines)


def output_writer(maze: list[list[int]],
                  entry: tuple[int, int],
                  exit_point: tuple[int, int],
                  path: list[str],
                  output_file: Path
                  ) -> None:
    """Stampa in output_file il maze con sotto entry, exit e soluzione.
    
    Args:
        maze: griglia di int 0-15 da convertire e stampare
        entry: le coordinate di entry (x,y)
        exit_point: le coordinate di exit (x,y)
        solution:
        output_file: il file in cui stampare tutto
        
    Raises:
        OutputError: se il file non può essere scritto su output_file.
    """
    solution: str = "".join(path)
    output: str = (
        print_hex(maze)
        + "\n\n"
        + f"{entry[0]},{entry[1]}\n"
        + f"{exit_point[0]},{exit_point[1]}\n"
        + f"{solution}\n"
    )
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)
    except OSError as e:
        raise OutputError(f"Cannot write in '{output_file}': {e}") from e
