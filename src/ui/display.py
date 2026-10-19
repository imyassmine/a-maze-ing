from secrets import randbits
from typing import Any

from mazegen import MazeGenerator
from src.config.parser import MazeConfig
from src.patterns.pattern42 import get_42_pattern

DEFAULT_PALETTE: dict[str, Any] = {
    "WALL_H": "\033[37m▄▄▄\033[0m",
    "WALL_H_TOP": "\033[37m▀▀▀\033[0m",
    "WALL_V": "\033[47m \033[0m",
    "HALF": "\033[37m▄\033[0m",
    "HALF_UP": "\033[37m▀\033[0m",
    "ENTRY_H": "\033[45m   \033[0m",
    "EXIT_H": "\033[41m   \033[0m",
    "FORTY_2": "\033[100m   \033[0m",
    "PATH_H": "   ",
    "PATH_V": " ",
    "ROTATE": False,
}

ALT_PALETTE: dict[str, Any] = {
    **DEFAULT_PALETTE,
    "WALL_H": "\033[34m▄▄▄\033[0m",
    "WALL_H_TOP": "\033[34m▀▀▀\033[0m",
    "WALL_V": "\033[44m \033[0m",
    "HALF": "\033[34m▄\033[0m",
    "HALF_UP": "\033[34m▀\033[0m",
    "ENTRY_H": "\033[47m   \033[0m",
    "EXIT_H": "\033[42m   \033[0m",
    "FORTY_2": "\033[43m   \033[0m",
    "ROTATE": True,
}

PATH_OFF = ("   ", " ")
PATH_ON = {
    False: ("\033[44m   \033[0m", "\033[44m \033[0m"),
    True: ("\033[41m   \033[0m", "\033[41m \033[0m"),
}


def _has_vertical_wall(maze: MazeGenerator, x: int, y: int) -> bool:
    """Return whether the vertical border at column x of row y is a wall."""
    if x == 0:
        return maze.grid[y][0].walls["West"]
    if x == maze.width:
        return maze.grid[y][maze.width - 1].walls["East"]
    return maze.grid[y][x].walls["West"]


def ascii_maze(
    maze: MazeGenerator,
    entry: tuple[int, int],
    exit_pos: tuple[int, int],
    pattern: list[tuple[int, int]],
    path: list[tuple[int, int]],
    params: dict[str, Any] | None = None,
) -> str:
    """Render a maze as an ANSI-coloured string."""
    if params is None:
        params = DEFAULT_PALETTE
    maze_display = str()
    SPACE_H = "   "
    SPACE_V = " "

    for row in maze.grid:
        first_line = str()
        second_line = str()

        for x, case in enumerate(row):
            x, y = case.position

            above = y > 0 and _has_vertical_wall(maze, x, y - 1)
            below = _has_vertical_wall(maze, x, y)
            left = x > 0 and row[x - 1].walls["North"]
            right = case.walls["North"]
            if above and below:
                first_line += str(params["WALL_V"])
            elif above and (left or right):
                first_line += str(params["WALL_V"])
            elif left or right:
                first_line += str(params["HALF"])
            else:
                first_line += SPACE_V

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

        x, y = row[-1].position
        above = y > 0 and _has_vertical_wall(maze, maze.width, y - 1)
        below = _has_vertical_wall(maze, maze.width, y)
        left = row[-1].walls["North"]
        if (above and below) or (above and left):
            first_line += params["WALL_V"]
        elif left:
            first_line += params["HALF"]
        else:
            first_line += SPACE_V

        if row[-1].walls["East"]:
            second_line += str(params["WALL_V"])
        else:
            second_line += SPACE_V

        maze_display += first_line + "\n" + second_line + "\n"

    last_line = ""
    last_row = maze.grid[-1]
    for x, case in enumerate(last_row):
        x, y = case.position
        left = x > 0 and last_row[x - 1].walls["South"]
        right = case.walls["South"]
        if left or right:
            last_line += str(params["HALF_UP"])
        else:
            last_line += SPACE_V
        if case.walls["South"]:
            last_line += str(params["WALL_H_TOP"])
        else:
            last_line += SPACE_H

    if last_row[-1].walls["South"]:
        last_line += str(params["HALF_UP"])
    else:
        last_line += SPACE_V

    maze_display += last_line
    return maze_display


def build_maze(
    maze_config: MazeConfig,
) -> tuple[MazeGenerator, list[tuple[int, int]]] | None:
    """Build a maze and return it with its 42-pattern cells."""
    maze = MazeGenerator(
        maze_config.width,
        maze_config.height,
        seed=maze_config.seed,
        entry=maze_config.entry,
        exit_pos=maze_config.exit_pos,
        perfect=maze_config.perfect,
    )
    pattern = get_42_pattern(maze, maze_config.entry, maze_config.exit_pos)
    if pattern is None:
        return None
    maze.generate(set(pattern))
    return maze, pattern


def user_interaction(
    maze: MazeGenerator,
    maze_config: MazeConfig,
    entry: tuple[int, int],
    exit_pos: tuple[int, int],
    pattern: list[tuple[int, int]],
    output: str,
    params: dict[str, Any] | None = None,
) -> None:
    """Print the maze and run the interactive menu until the user quits."""
    params = dict(DEFAULT_PALETTE) if params is None else params

    def display() -> None:
        print(ascii_maze(
            maze, entry, exit_pos, pattern, maze.solution_path, params
        ))

    def save() -> None:
        maze.write_output(entry, exit_pos, maze.solution_directions, output)

    display()
    save()
    while True:
        print("\n=== A-Maze-ing ===")
        print("1. Generate a new maze")
        print("2. Toggle the solution path")
        print("3. Switch color palette")
        print("4. Quit")
        try:
            user = int(input("Select an option (1-4): "))
            if user < 1 or user > 4:
                raise ValueError()
        except ValueError:
            print("\n[ERROR] Invalid choice: enter a number between 1 and 4.")
            continue

        if user == 1:
            maze_config.seed = randbits(8)
            result = build_maze(maze_config)
            if result is None:
                return
            maze, pattern = result
            print()
            display()
            save()
        elif user == 2:
            if params["PATH_H"] == PATH_OFF[0]:
                params["PATH_H"], params["PATH_V"] = PATH_ON[params["ROTATE"]]
            else:
                params["PATH_H"], params["PATH_V"] = PATH_OFF
            display()
        elif user == 3:
            path_visible = params["PATH_H"] != PATH_OFF[0]
            params.update(
                ALT_PALETTE if not params["ROTATE"] else DEFAULT_PALETTE
            )
            if path_visible:
                params["PATH_H"], params["PATH_V"] = PATH_ON[params["ROTATE"]]
            display()
        else:
            return
