"""Standalone maze generation module.

This file is designed to be reusable in another project and installable with
pip as the `mazegen` module.

Example
-------
>>> from mazegen import MazeGenerator
>>> generator = MazeGenerator(width=20, height=15, seed=42)
>>> generator.generate()

Custom parameters
-----------------
- `width` and `height` define the maze size.
- `seed` makes the generation reproducible.
- `entry` and `exit_pos` define the coordinates used to compute the solution.
- `perfect` controls whether loops are added after the spanning maze is built.
- `loop_ratio` controls how many safe extra walls may be removed in a
  non-perfect maze.

Access to the generated structure
----------------------------------
The generated maze is available through `generator.grid`. Each cell exposes:
- `position`: the `(x, y)` coordinates of the cell.
- `walls`: a dictionary for the `North`, `East`, `South`, and `West` walls.
- `visited`: the internal traversal flag used during generation.

Access to a solution
--------------------
- `generator.solution_directions` returns the shortest path as a list of
  direction strings.
- `generator.solution_path` returns the same path as coordinates.
- `generator.find_shortest_path(start, end)` can be used directly if needed.

The module also provides `write_output()` to export the maze in the
standard hexadecimal file format.
"""

from __future__ import annotations

import sys
from collections import deque
from random import Random

DIRECTIONS = ("North", "East", "South", "West")
OPPOSITE = {
    "North": "South",
    "East": "West",
    "South": "North",
    "West": "East",
}
DELTAS = {
    "North": (0, -1),
    "East": (1, 0),
    "South": (0, 1),
    "West": (-1, 0),
}
WALL_BITS = {"West": 8, "South": 4, "East": 2, "North": 1}


class Cell:
    """Represents a single cell in the maze."""

    def __init__(self, position: tuple[int, int]):
        self.position = position
        self.walls = {direction: True for direction in DIRECTIONS}
        self.visited = False


class MazeGenerator:
    """Generate mazes and expose the resulting structure and solution."""

    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
        entry: tuple[int, int] = (0, 0),
        exit_pos: tuple[int, int] | None = None,
        perfect: bool = True,
        loop_ratio: float = 0.15,
    ):
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers.")
        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError("Entry position must be "
                             "within the maze dimensions.")
        if exit_pos is None:
            exit_pos = (width - 1, height - 1)
        if not (0 <= exit_pos[0] < width and 0 <= exit_pos[1] < height):
            raise ValueError("Exit position must be "
                             "within the maze dimensions.")
        if entry == exit_pos:
            raise ValueError("Entry and exit positions cannot be the same.")
        if loop_ratio < 0 or loop_ratio > 1:
            raise ValueError("Loop ratio must be between 0 and 1.")

        self.width = width
        self.height = height
        self.seed = seed
        self.entry = entry
        self.exit_pos = exit_pos
        self.perfect = perfect
        self.loop_ratio = loop_ratio
        self.rng = Random(seed)
        self.grid: list[list[Cell]] = self.create_grid()
        self.solution_directions: list[str] = []
        self.solution_path: list[tuple[int, int]] = []

    def create_grid(self) -> list[list[Cell]]:
        return [
            [Cell((x, y)) for x in range(self.width)]
            for y in range(self.height)
        ]

    def generate(
        self,
        protected_positions: set[tuple[int, int]] | None = None,
    ) -> "MazeGenerator":
        """Generate a new maze and compute its shortest path."""
        self.reset()
        if protected_positions is not None:
            for x, y in protected_positions:
                self.grid[y][x].visited = True
        self.generate_perfect_maze(self.grid[0][0])
        if not self.perfect:
            self.add_loops(self.loop_ratio, protected_positions)
        self.solution_directions = self.find_shortest_path(
            self.grid[self.entry[1]][self.entry[0]],
            self.grid[self.exit_pos[1]][self.exit_pos[0]],
        )
        self.solution_path = self.trace_path(
            self.grid[self.entry[1]][self.entry[0]],
            self.solution_directions
            )
        return self

    def reset(self) -> None:
        """Reset the maze to a fresh, fully walled grid."""
        self.grid = self.create_grid()
        self.solution_directions = []
        self.solution_path = []

    def generate_perfect_maze(self, current_cell: Cell) -> None:
        """Generate the maze using recursive backtracking.

        The search walks depth-first and randomly shuffles neighbors at each
        step so the resulting structure changes with the seed.
        """
        current_cell.visited = True
        neighbors_list = list(self.get_neighbors(current_cell).items())
        self.rng.shuffle(neighbors_list)
        for direction, neighbor in neighbors_list:
            if not neighbor.visited:
                self.break_wall(current_cell, direction)
                self.generate_perfect_maze(neighbor)

    def get_neighbors(self, cell: Cell) -> dict[str, Cell]:
        """Return neighboring cells and directions."""
        x, y = cell.position
        neighbors: dict[str, Cell] = {}
        if y - 1 >= 0:
            neighbors["North"] = self.grid[y - 1][x]
        if x + 1 < self.width:
            neighbors["East"] = self.grid[y][x + 1]
        if y + 1 < self.height:
            neighbors["South"] = self.grid[y + 1][x]
        if x - 1 >= 0:
            neighbors["West"] = self.grid[y][x - 1]
        return neighbors

    def break_wall(self, cell: Cell, direction: str) -> None:
        """Break the wall in the given direction, on both sides."""
        self._set_wall(cell, direction, False)

    def restore_wall(self, cell: Cell, direction: str) -> None:
        """Restore the wall in the given direction, on both sides."""
        self._set_wall(cell, direction, True)

    def _set_wall(self, cell: Cell, direction: str, closed: bool) -> None:
        """Set a wall on a cell and on its direct neighbour, if any."""
        if direction not in DELTAS:
            raise ValueError(
                f"Invalid direction: {direction}. "
                f"Valid directions are {', '.join(DIRECTIONS)}."
            )
        x, y = cell.position
        dx, dy = DELTAS[direction]
        neighbor_x, neighbor_y = x + dx, y + dy
        if not (0 <= neighbor_x < self.width
                and 0 <= neighbor_y < self.height):
            return
        cell.walls[direction] = closed
        self.grid[neighbor_y][neighbor_x].walls[OPPOSITE[direction]] = closed

    def add_loops(
        self,
        ratio: float = 0.15,
        protected_positions: set[tuple[int, int]] | None = None,
    ) -> None:
        """Add loops by breaking a ratio of closed walls safely."""
        closed_walls = self.get_all_closed_walls()
        self.rng.shuffle(closed_walls)
        target = int(len(closed_walls) * ratio)
        broken = 0
        for cell, direction in closed_walls:
            if broken >= target:
                break
            x, y = cell.position
            neighbor_position = (
                (x + 1, y) if direction == "East" else (x, y + 1)
            )
            if protected_positions and (
                cell.position in protected_positions
                or neighbor_position in protected_positions
            ):
                continue
            if self.try_break_wall_safely(cell, direction):
                broken += 1

    def get_all_closed_walls(self) -> list[tuple[Cell, str]]:
        """Return all closed East and South walls, each wall only once."""
        closed_walls: list[tuple[Cell, str]] = []
        for row in self.grid:
            for cell in row:
                if cell.walls["East"]:
                    closed_walls.append((cell, "East"))
                if cell.walls["South"]:
                    closed_walls.append((cell, "South"))
        return closed_walls

    def try_break_wall_safely(self, cell: Cell, direction: str) -> bool:
        """Break a wall only if it does not create a 3x3 open area."""
        x, y = cell.position
        self.break_wall(cell, direction)
        for cx, cy in self.get_affected_areas_3x3(x, y, direction):
            if self.is_open_area_3x3(cx, cy):
                self.restore_wall(cell, direction)
                return False
        return True

    def get_affected_areas_3x3(
        self,
        x: int,
        y: int,
        direction: str,
    ) -> list[tuple[int, int]]:
        """Return cells impacted by a broken wall."""
        if direction == "East":
            affected_areas = [
                (x - 1, y),
                (x, y),
                (x - 1, y - 2),
                (x, y - 2),
                (x - 1, y - 1),
                (x, y - 1),
            ]
        elif direction == "South":
            affected_areas = [
                (x, y - 1),
                (x, y),
                (x - 2, y - 1),
                (x - 2, y),
                (x - 1, y - 1),
                (x - 1, y),
            ]
        elif direction == "West":
            affected_areas = [
                (x + 1, y),
                (x, y),
                (x + 1, y - 2),
                (x, y - 2),
                (x + 1, y - 1),
                (x, y - 1),
            ]
        elif direction == "North":
            affected_areas = [
                (x, y + 1),
                (x, y),
                (x - 2, y + 1),
                (x - 2, y),
                (x - 1, y + 1),
                (x - 1, y),
            ]
        else:
            raise ValueError(
                f"Invalid direction: {direction}. "
                "Valid directions are 'North', 'East', 'South', 'West'."
            )
        filtered_areas: list[tuple[int, int]] = []
        for cx, cy in affected_areas:
            if (
                cx >= 0
                and cx + 2 < self.width
                and cy >= 0
                and cy + 2 < self.height
            ):
                filtered_areas.append((cx, cy))
        return filtered_areas

    def is_open_area_3x3(self, x: int, y: int) -> bool:
        """Check whether a 3x3 area starting at (x, y) is open."""
        for dy in range(3):
            for dx in range(2):
                neighbor_cell = self.grid[y + dy][x + dx]
                if neighbor_cell.walls["East"]:
                    return False
        for dx in range(3):
            for dy in range(2):
                neighbor_cell = self.grid[y + dy][x + dx]
                if neighbor_cell.walls["South"]:
                    return False
        return True

    def find_shortest_path(self, start: Cell, end: Cell) -> list[str]:
        """Find the shortest path from start to end with BFS.

        Returns a list of directions to reach the end cell from the start
        cell.
        """
        queue: deque[tuple[Cell, list[str]]] = deque([(start, [])])
        visited = set()
        visited.add(start.position)
        while queue:
            current_cell, path = queue.popleft()
            if current_cell.position == end.position:
                return path
            for direction, neighbor in (
                self.get_open_neighbors(current_cell).items()
            ):
                if neighbor.position not in visited:
                    visited.add(neighbor.position)
                    queue.append((neighbor, path + [direction]))
        return []

    def get_open_neighbors(self, cell: Cell) -> dict[str, Cell]:
        """Return neighboring cells reachable without crossing a wall."""
        neighbors = self.get_neighbors(cell)
        open_neighbors: dict[str, Cell] = {}
        for direction, neighbor in neighbors.items():
            if not cell.walls[direction]:
                open_neighbors[direction] = neighbor
        return open_neighbors

    def trace_path(
            self,
            start: Cell,
            directions: list[str]
            ) -> list[tuple[int, int]]:
        """Convert a list of directions into a list of coordinates."""
        if not directions:
            return []
        x, y = start.position
        cells: list[tuple[int, int]] = [(x, y)]
        for direction in directions:
            if direction == "North":
                y -= 1
            elif direction == "East":
                x += 1
            elif direction == "South":
                y += 1
            elif direction == "West":
                x -= 1
            cells.append((x, y))
        return cells

    def get_binary(self, cell: Cell) -> int:
        """Encode a cell's closed walls as a 4-bit integer."""
        return sum(bit for direction, bit in WALL_BITS.items()
                   if cell.walls[direction])

    def write_output(
        self,
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
        path: list[str],
        output_file: str,
    ) -> None:
        """Write the maze, entry/exit and solution to a file.

        The output contains one hexadecimal row per maze row, a blank line,
        the entry coordinates, the exit coordinates and the solution as a
        string of N/E/S/W directions.
        """
        hexa_lines = "".join(
            "".join(hex(self.get_binary(cell))[2:].upper() for cell in row)
            + "\n"
            for row in self.grid
        ) + "\n"
        letters = {"North": "N", "East": "E", "South": "S", "West": "W"}
        path_line = "".join(letters[direction] for direction in path) + "\n"

        try:
            with open(output_file, "w") as fd:
                fd.write(hexa_lines)
                fd.write(f"{entry[0]},{entry[1]}\n")
                fd.write(f"{exit_pos[0]},{exit_pos[1]}\n")
                fd.write(path_line)
        except OSError as msg:
            print(f"[STDERR] Error opening file '{output_file}': {msg}",
                  file=sys.stderr)


__all__ = ["Cell", "MazeGenerator"]
