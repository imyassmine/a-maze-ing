#!/usr/bin/env python3


import sys
from src.config.parser import MazeConfig
from src.ui.display import build_maze, user_interaction


def main() -> int:
    if len(sys.argv) != 2:
        print("[STDERR] Usage: python3 a_maze_ing.py config.txt")

    config_file_path = sys.argv[1]
    try:
        maze_config = MazeConfig.from_config(config_file_path)
        result = build_maze(maze_config)
        if not result:
            return 1
        maze, pattern = result
        entry = maze_config.entry
        exit_pos = maze_config.exit_pos
        output = maze_config.output_file
        start_cell = maze.grid[entry[1]][entry[0]]
        end_cell = maze.grid[exit_pos[1]][exit_pos[0]]
        directions = maze.find_shortest_path(start_cell, end_cell)
        path = maze.trace_path(start_cell, directions)
        user_interaction(maze, maze_config, entry,
                         exit_pos, pattern, path, output)
        return 0
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"[STDERR] {error}")
        return 0


if __name__ == "__main__":
    main()
