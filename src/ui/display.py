from typing import Any
from secrets import randbits
from mazegen import MazeGenerator
from src.config.parser import MazeConfig
from src.patterns.pattern42 import apply_42_pattern
from src.patterns.pattern42 import pattern_list


def ascii_maze(
    maze: MazeGenerator,
    entry: tuple[int, int],
    exit_pos: tuple[int, int],
    pattern: list[tuple[int, int]],
    path: list[tuple[int, int]],
    params: dict[str, Any] = {"WALL_H": "\033[47m   \033[0m",
                              "WALL_V": "\033[47m \033[0m",
                              "ENTRY_H": "\033[45m   \033[0m",
                              "EXIT_H": "\033[41m   \033[0m",
                              "FORTY_2": "\033[100m   \033[0m",
                              "PATH_H": "   ",
                              "PATH_V": " ",
                              "ROTATE": False},
) -> str:
    maze_display = str()
    SPACE_H = "   "
    SPACE_V = " "

    for row in maze.grid:
        first_line = str()
        second_line = str()

        for case in row:
            x, y = case.position

            first_line += params["WALL_V"]
            if case.walls["North"]:
                first_line += str(params["WALL_H"])
            else:
                if case.position in path and y > 0 and (x, y - 1) in path:
                    first_line += str(params["PATH_H"])
                else:
                    first_line += SPACE_H

            if case.walls["West"]:
                second_line += str(params["WALL_V"])
            else:
                if case.position in path and x > 0 and (x - 1, y) in path:
                    second_line += str(params["PATH_V"])
                else:
                    second_line += SPACE_V

            if case.position == entry:
                second_line += str(params["ENTRY_H"])
            elif case.position == exit_pos:
                second_line += str(params["EXIT_H"])
            elif case.position in pattern:
                second_line += str(params["FORTY_2"])
            elif case.position in path:
                second_line += str(params["PATH_H"])
            else:
                second_line += SPACE_H

        first_line += params["WALL_V"]
        if row[-1].walls["East"]:
            second_line += str(params["WALL_V"])
        else:
            second_line += SPACE_V

        maze_display += first_line + "\n" + second_line + "\n"

    last_line = ""
    for case in maze.grid[-1]:
        last_line += str(params["WALL_V"])
        if case.walls["South"]:
            last_line += str(params["WALL_H"])
        else:
            last_line += SPACE_H
    last_line += str(params["WALL_V"])

    maze_display += last_line
    return maze_display


def build_maze(
    maze_config: MazeConfig,
) -> tuple[MazeGenerator, list[tuple[int, int]]] | None:
    """Build a maze and return it with the optional 42 pattern coordinates."""
    maze = MazeGenerator(
        maze_config.width,
        maze_config.height,
        seed=maze_config.seed,
        entry=maze_config.entry,
        exit_pos=maze_config.exit_pos,
        perfect=maze_config.perfect,
    )
    try:
        result = apply_42_pattern(maze, maze_config.entry,
                                  maze_config.exit_pos)
        if not result:
            raise ValueError("Change the file 'config.txt' "
                             "to allow the 42 pattern ")
        pattern: list[tuple[int, int]] = []
        pattern = pattern_list(maze)
        maze.generate(set(pattern) if result else None)
        return maze, pattern
    except ValueError as msg:
        print(msg)
        return None


def user_interaction(
    maze: MazeGenerator,
    maze_config: MazeConfig,
    entry: tuple[int, int],
    exit_pos: tuple[int, int],
    pattern: list[tuple[int, int]],
    path: list[tuple[int, int]],
    output: str,
    params: dict[str, Any] = {
        "WALL_H": "\033[47m   \033[0m",
        "WALL_V": "\033[47m \033[0m",
        "ENTRY_H": "\033[45m   \033[0m",
        "EXIT_H": "\033[41m   \033[0m",
        "FORTY_2": "\033[100m   \033[0m",
        "PATH_H": "   ",
        "PATH_V": " ",
        "ROTATE": False,
    },
) -> None:
    print(ascii_maze(maze, entry, exit_pos, pattern, path))
    start = maze.grid[entry[1]][entry[0]]
    end = maze.grid[exit_pos[1]][exit_pos[0]]
    path_list = maze.find_shortest_path(start, end)
    maze.write_output(maze, entry, exit_pos, path_list, output)
    while True:
        print("\n=== A-Maze-ing ====")
        print("1. Re-generate a new maze")
        print("2. Show/Hide path from entry to exit")
        print("3. Rotate maze colors")
        print("4. Quit")
        try:
            user = int(input("Choice? (1-4):  "))
            if user < 1 or user > 4:
                raise ValueError()
        except ValueError:
            print("\n[ERROR] You must enter an int between 1 and 4")
            continue

        if user == 1:
            maze_config.seed = randbits(8)
            result = build_maze(maze_config)
            if not result:
                return
            maze, new_pattern = result
            start = maze.grid[entry[1]][entry[0]]
            end = maze.grid[exit_pos[1]][exit_pos[0]]
            path_list = maze.find_shortest_path(start, end)
            path = maze.trace_path(start, path_list)
            print()
            print(ascii_maze(
                maze, entry, exit_pos, new_pattern, path, params
            ))
            maze.write_output(maze, entry, exit_pos, path_list, output)
            pattern = new_pattern
            continue

        elif user == 2:
            if params["PATH_H"] == "   ":
                if params["ROTATE"]:
                    params["PATH_H"] = "\033[41m   \033[0m"
                    params["PATH_V"] = "\033[41m \033[0m"
                else:
                    params["PATH_H"] = "\033[44m   \033[0m"
                    params["PATH_V"] = "\033[44m \033[0m"
            else:
                params["PATH_H"] = "   "
                params["PATH_V"] = " "
            print(ascii_maze(maze, entry, exit_pos, pattern, path, params))
            continue

        elif user == 3:
            if params["ROTATE"] is False:
                params["WALL_H"] = "\033[44m   \033[0m"
                params["WALL_V"] = "\033[44m \033[0m"
                params["ENTRY_H"] = "\033[47m   \033[0m"
                params["EXIT_H"] = "\033[42m   \033[0m"
                params["FORTY_2"] = "\033[43m   \033[0m"
                params["ROTATE"] = True
                if params["PATH_H"] != "   ":
                    params["PATH_H"] = "\033[41m   \033[0m"
                    params["PATH_V"] = "\033[41m \033[0m"

            else:
                params["WALL_H"] = "\033[47m   \033[0m"
                params["WALL_V"] = "\033[47m \033[0m"
                params["ENTRY_H"] = "\033[45m   \033[0m"
                params["EXIT_H"] = "\033[41m   \033[0m"
                params["FORTY_2"] = "\033[100m   \033[0m"
                params["ROTATE"] = False
                if params["PATH_H"] != "   ":
                    params["PATH_H"] = "\033[44m   \033[0m"
                    params["PATH_V"] = "\033[44m \033[0m"
            print(ascii_maze(maze, entry, exit_pos, pattern, path, params))
            continue

        else:
            return
