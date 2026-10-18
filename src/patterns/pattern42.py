from mazegen import MazeGenerator


def pattern_list(maze: MazeGenerator) -> list[tuple[int, int]]:
    y_start = (maze.height - 5) // 2
    x_start = (maze.width - 7) // 2
    quarante_deux_shape = [
        (0, 0),
        (4, 0),
        (5, 0),
        (6, 0),
        (0, 1),
        (6, 1),
        (0, 2),
        (1, 2),
        (2, 2),
        (4, 2),
        (5, 2),
        (6, 2),
        (2, 3),
        (4, 3),
        (2, 4),
        (4, 4),
        (5, 4),
        (6, 4),
    ]
    coord_pattern = [
        (x + x_start, y + y_start)
        for x, y in quarante_deux_shape
    ]
    return coord_pattern


def apply_42_pattern(
    maze: MazeGenerator,
    entry: tuple[int, int],
    exit_pos: tuple[int, int],
) -> bool:
    """Return a bool if the 42 pattern can be added or not

    Parameters
    ----------
    maze : Maze
        The generated maze whose grid will be encoded.
    entry : tuple[int, int]
        The (x, y) coordinates of the maze entry.
    exit_pos : tuple[int, int]
        The (x, y) coordinates of the maze exit.

    Returns
    -------
    bool
        True if the 42 pattern can be apply and a False if it cannot.
    """
    if maze.width < 7 or maze.height < 5:
        print("[STDERR] The maze size does not allow the '42' pattern")
        return False
    coord_pattern = pattern_list(maze)
    if entry in coord_pattern or exit_pos in coord_pattern:
        print("[STDERR] The entry/exit can not be in the '42' pattern")
        return False
    for lst in maze.grid:
        for cell in lst:
            for tupl in coord_pattern:
                if tupl == cell.position:
                    cell.visited = True
    return True
