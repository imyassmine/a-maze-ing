#!/usr/bin/env python3


import sys

from src.config.parser import MazeConfig
from src.ui.display import build_maze, user_interaction


def main() -> int:
    """Generate a maze from a config file, then run the terminal viewer."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>", file=sys.stderr)
        return 1
    try:
        maze_config = MazeConfig.from_config(sys.argv[1])
        result = build_maze(maze_config)
        if result is None:
            return 1
        maze, pattern = result
        user_interaction(maze, maze_config, maze_config.entry,
                         maze_config.exit_pos, pattern,
                         maze_config.output_file)
        return 0
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"[STDERR] {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
