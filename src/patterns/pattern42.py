import sys

from mazegen import MazeGenerator

PATTERN_SHAPE = [
    (0, 0), (4, 0), (5, 0), (6, 0),
    (0, 1), (6, 1),
    (0, 2), (1, 2), (2, 2), (4, 2), (5, 2), (6, 2),
    (2, 3), (4, 3),
    (2, 4), (4, 4), (5, 4), (6, 4),
]


def pattern_list(maze: MazeGenerator) -> list[tuple[int, int]]:
    """Return the coordinates of the centered "42" pattern."""
    y_start = (maze.height - 5) // 2
    x_start = (maze.width - 7) // 2
    return [(x + x_start, y + y_start) for x, y in PATTERN_SHAPE]


def get_42_pattern(
    maze: MazeGenerator,
    entry: tuple[int, int],
    exit_pos: tuple[int, int],
) -> list[tuple[int, int]] | None:
    """Return the "42" pattern cells, or None if it does not fit.

    The pattern requires a maze of at least 7x5 cells and must not overlap
    the entry or the exit.
    """
    if maze.width < 7 or maze.height < 5:
        print("[STDERR] The maze size does not allow the '42' pattern",
              file=sys.stderr)
        return None
    pattern = pattern_list(maze)
    if entry in pattern or exit_pos in pattern:
        print("[STDERR] The entry/exit can not be in the '42' pattern",
              file=sys.stderr)
        return None
    return pattern
