from pathlib import Path
from typing import Any
from random import Random
import random


class ConfigError(Exception):
    """Gestisce gli errori del config file."""


def _check_int(s: str, key: str) -> int:
    """Converte una stringa in int."""
    try:
        return int(s)
    except ValueError as e:
        raise ConfigError(f"{key} must be an int, got '{s}'") from e


def _check_boolean(s: str) -> bool:
    """Converte 'True' e 'False' in bool."""
    s = s.lower()

    if s == "true":
        return True

    if s == "false":
        return False

    raise ConfigError(
        f"PERFECT value is invalid: {s}. It must be True or False"
        )


def _check_coordinates(s: str, key: str) -> tuple[int, int]:
    """Converte una stringa x,y in una tupla di int."""
    try:
        x, y = s.split(",")
        return int(x), int(y)
    except ValueError as e:
        raise ConfigError(
            f"Invalid {key} coordinates: '{s}', expected 'x,y'") from e


def _check_values(config: dict[str, Any]) -> None:
    """Converte tutti i valori del config file
    e controlla che rientrino nei parametri.

    - Controlla se WIDTH e HEIGHT sono int e sono maggiori di 1
    - Controlla se ENTRY ed EXIT sono coordinate valide
    - Controlla che ENTRY ed EXIT non siano uguali
    - Controlla che ENTRY ed EXIT siano all'interno del maze
    - Controlla che PERFECT sia un boolean
    - Converte SEED in un int se esiste
    - Controlla che OUTPUT_FILE esista
    """
    config['width'] = _check_int(config['width'], "WIDTH")
    config["height"] = _check_int(config["height"], "HEIGHT")

    if config['width'] <= 1:
        raise ConfigError("WIDTH must be > 1")
    if config['height'] <= 1:
        raise ConfigError("HEIGHT must be > 1")

    config['entry'] = _check_coordinates(config['entry'], "ENTRY")
    config['exit'] = _check_coordinates(config['exit'], "EXIT")
    if config['entry'] == config['exit']:
        raise ConfigError("ENTRY and EXIT must be different")
    for point in ('entry', 'exit'):
        x, y = config[point]
        if not (0 <= x < config['width'] and 0 <= y < config['height']):
            raise ConfigError(f"Coordinates are out of bounds: {point}")

    config['perfect'] = _check_boolean(config['perfect'])

    if 'seed' in config:
        config['seed'] = _check_int(config['seed'], "SEED")
    else:
        config["seed"] = random.SystemRandom().randrange(2**32)

    if not config['output_file']:
        raise ConfigError("OUTPUT_FILE cannot be empty")


def parse_config(config_file: str) -> dict[str, Any]:
    """Legge config.txt e restituisce i valori della configurazione.

    Args:
        config_file: file con la configurazione del labirinto

    Returns:
        Un dict con tutte le keys richieste per costruire
        un labirinto e i valori associati ad esse

    Raises: ConfigError
    """

    mandatory: set[str] = {
        "width",
        "height",
        "entry",
        "exit",
        "perfect",
        "output_file"
    }

    optional: set[str] = {
        "seed"
    }

    config: dict[str, Any] = {}

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError as e:
        raise ConfigError(f"Config file not found: '{config_file}'") from e
    except (OSError, UnicodeDecodeError) as e:
        raise ConfigError(
            f"File cannot be accessed: '{config_file}': {e}") from e

    for n, line in enumerate(lines, start=1):
        # Numera ogni linea partendo da 1.
        # Controlla che il config_file sia valido e assegna key e value"""
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            raise ConfigError(f"Line {n} not valid: "
                              f"correct format is KEY=VALUE, got '{line}'")

        key, value = line.split("=", 1)
        key = key.strip().lower()
        value = value.strip()
        if key not in mandatory | optional:
            raise ConfigError(f"Line {n}: invalid key '{key}'")
        if key in config:
            raise ConfigError(f"Line {n}: duplicate key '{key}'")
        config[key] = value

    # Controlla se ci siano keys mancanti
    missing_keys: set[str] = mandatory - config.keys()
    if missing_keys:
        raise ConfigError(f"Missing keys: {', '.join(sorted(missing_keys))}")

    # Controlla che output_file non sovrascrive config.txt
    if Path(config["output_file"]).resolve() == Path(config_file).resolve():
        raise ConfigError("OUTPUT_FILE cannot be the config file itself")

    _check_values(config)
    return config
