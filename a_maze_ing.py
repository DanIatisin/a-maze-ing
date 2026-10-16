# import mazegen
from parsing import parse_config
# import display
import sys
from typing import Any

def main() -> None:
    
    if len(sys.argv) != 2:
        print("Usage: python a_maze_ing.py <config_file>")
        sys.exit(1)
        
        config: dict[str, Any] = parse_config(sys.argv[1])